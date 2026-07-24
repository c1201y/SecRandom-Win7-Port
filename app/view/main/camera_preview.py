from __future__ import annotations

import os
import random
from typing import Optional

from PySide2.QtWidgets import *
from PySide2.QtGui import *
from PySide2.QtCore import *
from qfluentwidgets import *
from loguru import logger

from app.Language.obtain_language import (
    get_content_description_async,
    get_content_name_async,
    get_content_pushbutton_name_async,
)

from app.common.camera_preview_backend import (
    get_cached_camera_devices,
    get_recommended_camera_resolution,
    OpenCVCaptureWorker,
    FaceDetectorWorker,
    bgr_frame_to_qimage,
    warmup_camera_devices_async,
)
from app.common.camera_preview_backend.audio_player import camera_preview_audio_player
from app.tools.settings_access import get_settings_signals, readme_settings_async
from app.common.roll_call import roll_call_manager


class CameraPreview(QWidget):
    """带有 OpenCV 捕获和 ONNX 人脸检测的摄像头预览页面。"""

    camera_source_change_requested = Signal(object)
    camera_resolution_change_requested = Signal(object)
    capture_stop_requested = Signal()
    detector_enabled_changed = Signal(bool)
    detector_type_changed = Signal(object)
    detector_input_size_changed = Signal(object)

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self._devices = []
        self._workers_ready: bool = False
        self._preview_mode: int = 0
        self._detection_active = False
        self._has_face_once = False
        self._overlay_rects: list[tuple[int, int, int, int]] = []
        self._overlay_colors: list[QColor] = []
        self._overlay_circles: list[tuple[int, int, int]] = []
        self._latest_frame = None
        self._latest_qimage: Optional[QImage] = None
        self._latest_faces: list[tuple[int, int, int, int]] = []
        self._capture_resolution: Optional[tuple[int, int]] = None
        self._picker_color: QColor = QColor()
        self._picking_active: bool = False
        self._picking_started: bool = False
        self._picking_step: int = 0
        self._picking_total_steps: int = 32
        self._picking_duration_ms: int = 2000
        self._final_view_active: bool = False
        self._final_selected_rect: Optional[tuple[int, int, int, int]] = None
        self._final_face_pixmap: Optional[QPixmap] = None
        self._audio_loop_started: bool = False
        self._play_process_audio: bool = True
        self._play_result_audio: bool = True
        self._frame_pipeline_connected: bool = False
        self._pick_count: int = 1
        self._pick_max_count: int = 1
        self._pick_minus_button: Optional[QPushButton] = None
        self._pick_plus_button: Optional[QPushButton] = None
        self._pick_count_label: Optional[QLabel] = None
        self._pick_count_widget: Optional[QWidget] = None
        self._recognized_count_label: Optional[QLabel] = None
        self._target_pick_count: int = 1
        self._picked_faces: list[tuple[int, int, int, int]] = []
        self._picked_face_pixmaps: list[QPixmap] = []
        self._current_pick_rect: Optional[tuple[int, int, int, int]] = None
        self._commit_pending: bool = False
        self._commit_index: int = 0

        self._capture_thread: Optional[QThread] = None
        self._capture_worker: Optional[OpenCVCaptureWorker] = None
        self._detector_thread: Optional[QThread] = None
        self._detector_worker: Optional[FaceDetectorWorker] = None
        self._init_poll_left: int = 0
        self._init_poll_timer = QTimer(self)
        self._init_poll_timer.setSingleShot(True)
        self._init_poll_timer.timeout.connect(self._try_init_workers_nonblocking)

        self._clear_timer = QTimer(self)
        self._clear_timer.setSingleShot(True)
        self._clear_timer.timeout.connect(self._stop_detection_and_reset)

        self._no_face_timer = QTimer(self)
        self._no_face_timer.setSingleShot(True)
        self._no_face_timer.timeout.connect(self._on_no_face_timeout)

        self._picking_timer = QTimer(self)
        self._picking_timer.setSingleShot(True)
        self._picking_timer.timeout.connect(self._on_picking_tick)

        self._final_view_timer = QTimer(self)
        self._final_view_timer.setSingleShot(True)
        self._final_view_timer.timeout.connect(self._stop_detection_and_reset)

        self._init_ui()

    def showEvent(self, event: QShowEvent) -> None:
        super().showEvent(event)
        self._ensure_workers_nonblocking()
        self._start_preview_capture()
        self._apply_preview_mode()

    def hideEvent(self, event: QHideEvent) -> None:
        self._stop_preview_capture()
        super().hideEvent(event)

    def _ensure_workers_nonblocking(self) -> None:
        if self._workers_ready:
            return
        devices = get_cached_camera_devices()
        if devices:
            self._init_workers(devices=devices)
            return

        try:
            warmup_camera_devices_async(force_refresh=False)
        except Exception:
            pass

        if self._init_poll_left <= 0:
            self._init_poll_left = 40
        if not self._init_poll_timer.isActive():
            self._init_poll_timer.start(200)

    def _try_init_workers_nonblocking(self) -> None:
        if self._workers_ready:
            return
        devices = get_cached_camera_devices()
        if devices:
            self._init_workers(devices=devices)
            try:
                if self.isVisible():
                    self._start_preview_capture()
                    self._apply_preview_mode()
            except Exception:
                pass
            return

        self._init_poll_left = int(self._init_poll_left) - 1
        if self._init_poll_left > 0:
            self._init_poll_timer.start(200)
            return
        try:
            self.start_button.setEnabled(False)
        except Exception:
            pass
        try:
            self.preview_label.setText(
                get_content_description_async("camera_preview", "no_camera")
            )
        except Exception:
            pass
        self._show_message("no_camera")

    def _read_preview_mode(self) -> int:
        try:
            v = readme_settings_async("face_detector_settings", "camera_preview_mode")
            idx = int(v) if v is not None else 0
        except Exception:
            idx = 0
        return 0 if idx not in (0, 1) else idx

    def _apply_preview_mode(self, mode_index: Optional[int] = None) -> None:
        mode = self._read_preview_mode() if mode_index is None else int(mode_index)
        mode = 0 if mode not in (0, 1) else mode
        self._preview_mode = mode

        pick_widget = self._pick_count_widget
        count_label = self._recognized_count_label

        if mode == 1:
            try:
                self.start_button.setVisible(False)
            except Exception:
                pass
            if pick_widget is not None:
                try:
                    pick_widget.setVisible(False)
                except Exception:
                    pass
            if count_label is not None:
                try:
                    count_label.setVisible(True)
                except Exception:
                    pass

            self._clear_timer.stop()
            self._no_face_timer.stop()
            self._picking_timer.stop()
            self._final_view_timer.stop()

            self._detection_active = True
            self._picking_active = False
            self._picking_started = False
            self._commit_pending = False
            self._final_view_active = False
            self._final_selected_rect = None
            self._final_face_pixmap = None
            self._overlay_circles = []
            self._overlay_colors = []

            try:
                self._camera_opacity_effect.setOpacity(1.0)
            except Exception:
                pass
            try:
                self.preview_stack.setCurrentWidget(self.preview_label)
            except Exception:
                pass

            try:
                if self._audio_loop_started:
                    camera_preview_audio_player.stop(wait=False)
            except Exception:
                pass
            self._audio_loop_started = False

            self.detector_enabled_changed.emit(True)
            self._load_recognition_frame_color()
            self._update_recognition_status()
            return

        if count_label is not None:
            try:
                count_label.setVisible(False)
            except Exception:
                pass
        if pick_widget is not None:
            try:
                pick_widget.setVisible(True)
            except Exception:
                pass
        try:
            self.start_button.setVisible(True)
        except Exception:
            pass

        if self._detection_active:
            self._stop_detection_and_reset()

    def _update_recognition_status(self) -> None:
        if self._preview_mode != 1:
            return
        rects = list(self._latest_faces or [])
        self._overlay_circles = [self._compute_circle_from_rect(r) for r in rects]
        base_color = (
            self._picker_color
            if self._picker_color is not None and self._picker_color.isValid()
            else QColor(255, 255, 255)
        )
        self._overlay_colors = [base_color for _ in self._overlay_circles]

        label = self._recognized_count_label
        if label is not None:
            try:
                label.setText(
                    get_content_name_async("camera_preview", "recognized_count").format(
                        count=len(rects)
                    )
                )
            except Exception:
                try:
                    label.setText(str(len(rects)))
                except Exception:
                    pass

    def _start_preview_capture(self) -> None:
        if not self._workers_ready:
            return

        detector_thread = self._detector_thread
        if detector_thread is not None and not detector_thread.isRunning():
            try:
                detector_thread.start()
            except Exception:
                pass

        capture_thread = self._capture_thread
        if capture_thread is not None and not capture_thread.isRunning():
            try:
                capture_thread.start()
            except Exception:
                pass

        self._connect_frame_pipeline()

        capture_worker = self._capture_worker
        if capture_worker is None:
            return
        if capture_thread is not None and capture_thread.isRunning():
            QMetaObject.invokeMethod(
                capture_worker,
                "start",
                Qt.ConnectionType.QueuedConnection,
            )
        else:
            try:
                capture_worker.start()
            except Exception:
                pass

    def _stop_preview_capture(self) -> None:
        self._clear_timer.stop()
        self._no_face_timer.stop()
        self._picking_timer.stop()
        self._final_view_timer.stop()

        try:
            self._stop_detection_and_reset()
        except Exception:
            pass

        self._disconnect_frame_pipeline()

        try:
            camera_preview_audio_player.stop(wait=False)
        except Exception:
            pass
        self._audio_loop_started = False

        capture_worker = self._capture_worker
        if capture_worker is None:
            return

        capture_thread = self._capture_thread
        if capture_thread is not None and capture_thread.isRunning():
            QMetaObject.invokeMethod(
                capture_worker,
                "stop",
                Qt.ConnectionType.BlockingQueuedConnection,
            )
        else:
            try:
                capture_worker.stop()
            except Exception:
                pass

    def _disconnect_frame_pipeline(self) -> None:
        if self._capture_worker is None:
            self._frame_pipeline_connected = False
            return
        if not self._frame_pipeline_connected:
            return
        try:
            self._capture_worker.frame_ready.disconnect()
        except Exception:
            pass
        self._frame_pipeline_connected = False

    def _connect_frame_pipeline(self) -> None:
        if self._capture_worker is None:
            return
        if self._frame_pipeline_connected:
            return
        try:
            self._capture_worker.frame_ready.connect(self._on_frame_received)
        except Exception:
            pass
        if self._detector_worker is not None:
            try:
                self._capture_worker.frame_ready.connect(
                    self._detector_worker.process_frame
                )
            except Exception:
                pass
        self._frame_pipeline_connected = True

    def _init_ui(self) -> None:
        """初始化 UI 组件。"""
        self.setObjectName("cameraPreviewPage")

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(12)

        self.preview_label = QLabel(self)
        self.preview_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.preview_label.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding
        )
        self.preview_label.setMinimumHeight(320)
        self.preview_label.setStyleSheet(
            "QLabel { background: rgba(0,0,0,0.35); border-radius: 8px; }"
        )

        self._camera_opacity_effect = QGraphicsOpacityEffect(self.preview_label)
        self._camera_opacity_effect.setOpacity(1.0)
        self.preview_label.setGraphicsEffect(self._camera_opacity_effect)

        self.result_label = QLabel(self)
        self.result_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.result_label.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding
        )
        self.result_label.setMinimumHeight(320)
        self.result_label.setStyleSheet(
            "QLabel { background: rgba(0,0,0,0.35); border-radius: 8px; }"
        )

        self.preview_container = QWidget(self)
        self.preview_container.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding
        )
        self.preview_stack = QStackedLayout(self.preview_container)
        self.preview_stack.setContentsMargins(0, 0, 0, 0)
        self.preview_stack.addWidget(self.preview_label)
        self.preview_stack.addWidget(self.result_label)
        self.preview_stack.setCurrentWidget(self.preview_label)

        controls = QWidget(self)
        controls_layout = QVBoxLayout(controls)
        controls_layout.setContentsMargins(0, 0, 0, 0)
        controls_layout.setSpacing(8)

        self.start_button = PrimaryPushButton(
            get_content_pushbutton_name_async("camera_preview", "start_button"),
            self,
        )
        roll_call_manager.set_widget_font(self.start_button, 15)
        self.start_button.setFixedSize(180, 45)
        self.start_button.clicked.connect(self._on_start_clicked)

        self._pick_minus_button = PushButton("-")
        self._pick_plus_button = PushButton("+")
        self._pick_count_label = BodyLabel("1")
        self._pick_count_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        roll_call_manager.set_widget_font(self._pick_minus_button, 20)
        roll_call_manager.set_widget_font(self._pick_plus_button, 20)
        roll_call_manager.set_widget_font(self._pick_count_label, 20)

        self._pick_minus_button.setFixedSize(45, 45)
        self._pick_plus_button.setFixedSize(45, 45)
        self._pick_count_label.setFixedSize(65, 45)

        self._pick_minus_button.setContextMenuPolicy(Qt.ContextMenuPolicy.NoContextMenu)
        self._pick_plus_button.setContextMenuPolicy(Qt.ContextMenuPolicy.NoContextMenu)

        self._pick_minus_button.clicked.connect(lambda: self._change_pick_count(-1))
        self._pick_plus_button.clicked.connect(lambda: self._change_pick_count(1))

        self._recognized_count_label = BodyLabel("")
        try:
            self._recognized_count_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        except Exception:
            pass
        roll_call_manager.set_widget_font(self._recognized_count_label, 16)
        self._recognized_count_label.setFixedSize(180, 45)
        self._recognized_count_label.setVisible(False)

        self._pick_count_widget = QWidget(self)
        self._pick_count_widget.setFixedWidth(180)
        pick_layout = QHBoxLayout(self._pick_count_widget)
        pick_layout.setContentsMargins(0, 0, 0, 0)
        pick_layout.setSpacing(0)
        pick_layout.addWidget(self._pick_minus_button)
        pick_layout.addStretch(1)
        pick_layout.addWidget(self._pick_count_label)
        pick_layout.addStretch(1)
        pick_layout.addWidget(self._pick_plus_button)
        self._apply_pick_count_limits()

        controls_layout.addWidget(
            self._recognized_count_label, 0, Qt.AlignmentFlag.AlignRight
        )
        controls_layout.addWidget(
            self._pick_count_widget, 0, Qt.AlignmentFlag.AlignRight
        )
        controls_layout.addWidget(self.start_button, 0, Qt.AlignmentFlag.AlignRight)

        bottom = QWidget(self)
        bottom_layout = QHBoxLayout(bottom)
        bottom_layout.setContentsMargins(0, 0, 0, 0)
        bottom_layout.addStretch(1)
        bottom_layout.addWidget(controls, 0, Qt.AlignmentFlag.AlignRight)

        main_layout.addWidget(self.preview_container, 1)
        main_layout.addWidget(bottom, 0)

    def _init_workers(self, devices: Optional[list] = None) -> None:
        """初始化摄像头捕获和检测工作线程。"""
        if self._workers_ready:
            return

        os.environ.setdefault("OPENCV_VIDEOIO_PRIORITY_MSMF", "1")

        if devices is None:
            devices = get_cached_camera_devices()
        try:
            self._devices = list(devices or [])
        except Exception:
            self._devices = []
        if not self._devices:
            self.start_button.setEnabled(False)
            self.preview_label.setText(
                get_content_description_async("camera_preview", "no_camera")
            )
            self._show_message("no_camera")
            return

        saved_source = readme_settings_async("face_detector_settings", "camera_source")
        default_source = None
        if saved_source is not None:
            for device in self._devices:
                if (
                    device.qt_id == saved_source
                    or str(device.qt_id) == str(saved_source)
                    or device.source == saved_source
                    or str(device.source) == str(saved_source)
                ):
                    default_source = device.source
                    break
        if default_source is None:
            default_source = self._devices[0].source
            default_camera_id = (
                self._devices[0].qt_id
                if getattr(self._devices[0], "qt_id", "")
                else self._devices[0].source
            )
        else:
            default_camera_id = None
            for device in self._devices:
                try:
                    if device.source == default_source:
                        default_camera_id = (
                            device.qt_id
                            if getattr(device, "qt_id", "")
                            else device.source
                        )
                        break
                except Exception:
                    continue
            if default_camera_id is None:
                default_camera_id = default_source

        desired_resolution = self._resolve_camera_display_resolution(default_camera_id)

        self._capture_thread = QThread(self)
        self._capture_worker = OpenCVCaptureWorker(default_source, desired_resolution)
        self._capture_worker.moveToThread(self._capture_thread)
        self._capture_thread.started.connect(self._capture_worker.start)
        self.capture_stop_requested.connect(self._capture_worker.stop)
        self.camera_source_change_requested.connect(
            self._capture_worker.request_source_change
        )
        self.camera_resolution_change_requested.connect(
            self._capture_worker.request_resolution_change
        )
        self._capture_worker.resolution_applied.connect(
            self._on_capture_resolution_applied
        )
        self._capture_worker.error_occurred.connect(self._on_worker_error)

        self._detector_thread = QThread(self)
        detector_type = readme_settings_async("face_detector_settings", "detector_type")
        self._detector_worker = FaceDetectorWorker()
        self._detector_worker.set_model_filename(detector_type)
        try:
            w = int(
                readme_settings_async("face_detector_settings", "model_input_width")
            )
            h = int(
                readme_settings_async("face_detector_settings", "model_input_height")
            )
            self._detector_worker.set_input_size((w, h) if w > 0 and h > 0 else None)
        except Exception:
            self._detector_worker.set_input_size(None)
        self._detector_worker.moveToThread(self._detector_thread)
        self._detector_thread.started.connect(self._detector_worker.ensure_loaded)
        self.detector_enabled_changed.connect(self._detector_worker.set_enabled)
        self.detector_type_changed.connect(self._detector_worker.set_model_filename)
        self.detector_input_size_changed.connect(self._detector_worker.set_input_size)
        self._detector_worker.faces_ready.connect(self._on_faces_detected)
        self._detector_worker.error_occurred.connect(self._on_worker_error)

        try:
            get_settings_signals().settingChanged.connect(self._on_setting_changed)
        except Exception:
            pass

        try:
            self._detector_thread.start()
            self._capture_thread.start()
        except Exception as exc:
            logger.exception("启动摄像头线程失败: {}", exc)
            self._show_message("unavailable", details=str(exc))
            self.start_button.setEnabled(False)
            return

        self._connect_frame_pipeline()
        self._workers_ready = True

    def _on_start_clicked(self) -> None:
        """启动人脸检测流程。"""
        if self._preview_mode == 1:
            return
        if self._detector_worker is None or self._capture_worker is None:
            self._show_message("unavailable")
            return

        try:
            v = readme_settings_async(
                "face_detector_settings", "picking_duration_seconds"
            )
            seconds = int(v) if v is not None else 2
            seconds = max(1, min(seconds, 10))
            self._picking_duration_ms = int(seconds * 1000)
        except Exception:
            self._picking_duration_ms = 2000

        try:
            v = readme_settings_async("face_detector_settings", "play_process_audio")
            self._play_process_audio = True if v is None else bool(v)
        except Exception:
            self._play_process_audio = True

        try:
            v = readme_settings_async("face_detector_settings", "play_result_audio")
            self._play_result_audio = True if v is None else bool(v)
        except Exception:
            self._play_result_audio = True

        self.start_button.setEnabled(False)
        self._detection_active = True
        self._has_face_once = False
        self._overlay_rects = []
        self._overlay_colors = []
        self._overlay_circles = []
        self._latest_faces = []
        self._picker_color = QColor()
        self._picking_active = True
        self._picking_started = False
        self._picking_step = 0
        self._final_view_active = False
        self._final_selected_rect = None
        self._final_face_pixmap = None
        self._audio_loop_started = False
        self._picked_faces = []
        self._picked_face_pixmaps = []
        self._current_pick_rect = None
        self._commit_pending = False
        self._commit_index = 0
        self._target_pick_count = (
            int(self._pick_count) if int(self._pick_count) > 0 else 1
        )
        self._connect_frame_pipeline()
        try:
            self._camera_opacity_effect.setOpacity(1.0)
        except Exception:
            pass
        try:
            self.result_label.clear()
        except Exception:
            pass
        try:
            self.preview_stack.setCurrentWidget(self.preview_label)
        except Exception:
            pass
        self.detector_enabled_changed.emit(True)

        self._no_face_timer.start(10_000)

    def _on_setting_changed(
        self, first_level_key: str, second_level_key: str, value: object
    ) -> None:
        if first_level_key != "face_detector_settings":
            return
        if second_level_key == "camera_display_resolution_map":
            if self._capture_worker is None:
                return
            camera_id = readme_settings_async("face_detector_settings", "camera_source")
            desired = self._resolve_camera_display_resolution(camera_id)
            self.camera_resolution_change_requested.emit(desired)
            return
        if second_level_key in ("model_input_width", "model_input_height"):
            try:
                w = int(
                    readme_settings_async("face_detector_settings", "model_input_width")
                )
                h = int(
                    readme_settings_async(
                        "face_detector_settings", "model_input_height"
                    )
                )
                self.detector_input_size_changed.emit(
                    (w, h) if w > 0 and h > 0 else None
                )
            except Exception:
                self.detector_input_size_changed.emit(None)
            return
        if second_level_key == "picker_frame_color":
            try:
                text = str(value).strip() if value is not None else ""
                c = QColor(text) if text else QColor()
                if self._preview_mode == 1:
                    self._picker_color = c if c.isValid() else QColor(255, 255, 255)
                    self._update_recognition_status()
                    try:
                        if self._latest_frame is not None:
                            self._on_frame_received(self._latest_frame)
                    except Exception:
                        pass
                elif c.isValid():
                    self._picker_color = c
            except Exception:
                if self._preview_mode == 1:
                    self._picker_color = QColor(255, 255, 255)
            return
        if second_level_key == "detector_type":
            self.detector_type_changed.emit(value)
            return
        if second_level_key == "camera_preview_mode":
            try:
                self._apply_preview_mode(int(value) if value is not None else 0)
            except Exception:
                self._apply_preview_mode()
            return
        if second_level_key != "camera_source":
            return

        if self._capture_worker is None:
            return

        source = None
        if value is not None:
            for device in self._devices:
                if (
                    device.qt_id == value
                    or str(device.qt_id) == str(value)
                    or device.source == value
                    or str(device.source) == str(value)
                ):
                    source = device.source
                    break
            if source is None:
                source = value

        if source is None and self._devices:
            source = self._devices[0].source

        if source is None:
            self._show_message("camera_open_failed")
            return

        self._stop_detection_and_reset()
        self._no_face_timer.stop()
        self._clear_timer.stop()
        self.camera_source_change_requested.emit(source)
        desired = self._resolve_camera_display_resolution(value)
        self.camera_resolution_change_requested.emit(desired)
        self._apply_preview_mode()

    def _get_camera_display_resolution_map(self) -> dict:
        value = readme_settings_async(
            "face_detector_settings", "camera_display_resolution_map"
        )
        return value if isinstance(value, dict) else {}

    def _get_camera_key_variants(self, camera_id: object) -> list[str]:
        values: list[object] = []
        if camera_id is not None:
            values.append(camera_id)

        for device in self._devices:
            try:
                if (
                    device.qt_id == camera_id
                    or str(device.qt_id) == str(camera_id)
                    or device.source == camera_id
                    or str(device.source) == str(camera_id)
                ):
                    if getattr(device, "qt_id", ""):
                        values.append(device.qt_id)
                    values.append(device.source)
                    break
            except Exception:
                continue

        keys: list[str] = []
        for v in values:
            try:
                k = str(v).strip()
            except Exception:
                continue
            if k and k not in keys:
                keys.append(k)
        return keys

    def _set_camera_display_resolution_for_camera(
        self, camera_id: object, resolution: tuple[int, int]
    ) -> None:
        keys = self._get_camera_key_variants(camera_id)
        if not keys:
            return
        mapping = self._get_camera_display_resolution_map()
        text = f"{int(resolution[0])}x{int(resolution[1])}"
        for key in keys:
            mapping[key] = text
        try:
            from app.tools.settings_access import update_settings

            update_settings(
                "face_detector_settings", "camera_display_resolution_map", mapping
            )
        except Exception:
            return

    def _resolve_camera_display_resolution(
        self, camera_id: object
    ) -> Optional[tuple[int, int]]:
        mapping = self._get_camera_display_resolution_map()
        keys = self._get_camera_key_variants(camera_id)
        for key in keys:
            raw = mapping.get(key)
            if not raw:
                continue
            try:
                text = str(raw).strip().lower()
                if "x" in text:
                    w_str, h_str = text.split("x", 1)
                    w = int(w_str.strip())
                    h = int(h_str.strip())
                    if w > 0 and h > 0:
                        return (w, h)
            except Exception:
                continue

        recommended = None
        try:
            preferred_id: object = camera_id
            for device in self._devices:
                try:
                    if (
                        device.qt_id == camera_id
                        or str(device.qt_id) == str(camera_id)
                        or device.source == camera_id
                        or str(device.source) == str(camera_id)
                    ):
                        preferred_id = (
                            device.qt_id
                            if getattr(device, "qt_id", "")
                            else device.source
                        )
                        break
                except Exception:
                    continue
            recommended = get_recommended_camera_resolution(preferred_id)
        except Exception:
            recommended = None
        if recommended is not None:
            self._set_camera_display_resolution_for_camera(camera_id, recommended)
        return recommended

    def _stop_detection_and_reset(self) -> None:
        """停止检测，清除覆盖层，并恢复 UI 状态。"""
        self._detection_active = False
        self.detector_enabled_changed.emit(False)
        self._overlay_rects = []
        self._overlay_colors = []
        self._overlay_circles = []
        self._picking_active = False
        self._picking_started = False
        self._picking_timer.stop()
        self._final_view_timer.stop()
        self._final_view_active = False
        self._final_selected_rect = None
        self._final_face_pixmap = None
        self._picked_faces = []
        self._picked_face_pixmaps = []
        self._current_pick_rect = None
        self._commit_pending = False
        self._commit_index = 0
        self._connect_frame_pipeline()
        try:
            self._camera_opacity_effect.setOpacity(1.0)
        except Exception:
            pass
        try:
            self.result_label.clear()
        except Exception:
            pass
        try:
            self.preview_stack.setCurrentWidget(self.preview_label)
        except Exception:
            pass
        if self._audio_loop_started:
            try:
                camera_preview_audio_player.stop(wait=False)
            except Exception:
                pass
            self._audio_loop_started = False
        self.start_button.setEnabled(True)

    def _on_no_face_timeout(self) -> None:
        """处理短时间内未检测到人脸的情况。"""
        if not self._detection_active or self._has_face_once:
            return

        self._stop_detection_and_reset()
        self._show_message("no_face_detected")

    def _on_frame_received(self, frame_bgr) -> None:
        """在 UI 中渲染新帧。"""
        self._latest_frame = frame_bgr
        try:
            h = int(frame_bgr.shape[0])
            w = int(frame_bgr.shape[1])
            if w > 0 and h > 0:
                self._capture_resolution = (w, h)
        except Exception:
            pass
        try:
            if self.preview_stack.currentWidget() is not self.preview_label:
                return
        except Exception:
            pass
        try:
            qimage = bgr_frame_to_qimage(frame_bgr)
        except Exception as exc:
            logger.exception("帧转换失败: {}", exc)
            return
        self._latest_qimage = qimage

        pixmap = QPixmap.fromImage(qimage)
        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)

        if self._detection_active and self._overlay_circles:
            for circle, color in zip(
                self._overlay_circles, self._overlay_colors, strict=True
            ):
                pen = QPen(color, 6)
                painter.setPen(pen)
                cx, cy, r = circle
                painter.drawEllipse(QPointF(float(cx), float(cy)), float(r), float(r))

        painter.end()

        target = self.preview_label.size()
        if target.width() > 0 and target.height() > 0:
            pixmap = pixmap.scaled(
                target,
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation,
            )
        self.preview_label.setPixmap(pixmap)

    def _on_capture_resolution_applied(self, resolution: object) -> None:
        try:
            if (
                isinstance(resolution, (list, tuple))
                and len(resolution) >= 2
                and int(resolution[0]) > 0
                and int(resolution[1]) > 0
            ):
                self._capture_resolution = (int(resolution[0]), int(resolution[1]))
        except Exception:
            return

        try:
            if self._latest_frame is not None:
                self._on_frame_received(self._latest_frame)
        except Exception:
            pass

    def _update_result_pixmap(self) -> None:
        pix = self._final_face_pixmap
        if pix is None:
            return
        target = self.result_label.size()
        if target.width() <= 0 or target.height() <= 0:
            return
        scaled = pix.scaled(
            target,
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation,
        )
        self.result_label.setPixmap(scaled)

    def resizeEvent(self, event: QResizeEvent) -> None:
        try:
            if self.preview_stack.currentWidget() is self.result_label:
                self._update_result_pixmap()
        except Exception:
            pass
        super().resizeEvent(event)

    def _on_faces_detected(self, rects: list[tuple[int, int, int, int]]) -> None:
        """从检测线程接收人脸矩形。"""
        if self._preview_mode == 1:
            self._latest_faces = rects or []
            self._detection_active = True
            self._update_recognition_status()
            return
        if not self._detection_active:
            return

        self._latest_faces = rects or []
        self._apply_pick_count_limits()

        if (
            self._commit_pending
            and self._current_pick_rect is not None
            and self._latest_faces
        ):
            best = self._find_best_match_rect(
                self._current_pick_rect, self._latest_faces
            )
            if best is not None:
                self._current_pick_rect = best
        if self._picking_active and not self._picking_started and self._latest_faces:
            self._has_face_once = True
            self._no_face_timer.stop()
            self._picking_started = True
            self._picking_step = 0
            self._load_picker_settings()
            if self._play_process_audio and not self._audio_loop_started:
                try:
                    started = camera_preview_audio_player.play(
                        "face/process.wav", loop=True, volume=1.0
                    )
                    self._audio_loop_started = True if started else False
                except Exception:
                    self._audio_loop_started = False
            self._schedule_next_pick_tick()

    def _on_worker_error(self, key: str, _title: str, details: str) -> None:
        """处理来自工作线程的错误。"""
        logger.error("CameraPreview 工作线程错误 {}: {}", key, details)
        self._stop_detection_and_reset()
        self._show_message(key, details=details)

    def _change_pick_count(self, change: int) -> None:
        try:
            self._pick_count = int(self._pick_count) + int(change)
        except Exception:
            self._pick_count = 1
        self._apply_pick_count_limits()

    def _apply_pick_count_limits(self) -> None:
        try:
            self._pick_count = int(self._pick_count)
        except Exception:
            self._pick_count = 1
        self._pick_count = max(1, min(self._pick_count, 100))

        if self._pick_count_label is not None:
            self._pick_count_label.setText(str(self._pick_count))
        if self._pick_minus_button is not None:
            self._pick_minus_button.setEnabled(self._pick_count > 1)
        if self._pick_plus_button is not None:
            self._pick_plus_button.setEnabled(self._pick_count < 100)

    def _rect_iou(
        self, a: tuple[int, int, int, int], b: tuple[int, int, int, int]
    ) -> float:
        ax, ay, aw, ah = a
        bx, by, bw, bh = b
        ax2 = ax + aw
        ay2 = ay + ah
        bx2 = bx + bw
        by2 = by + bh

        ix1 = max(ax, bx)
        iy1 = max(ay, by)
        ix2 = min(ax2, bx2)
        iy2 = min(ay2, by2)
        iw = ix2 - ix1
        ih = iy2 - iy1
        if iw <= 0 or ih <= 0:
            return 0.0
        inter = float(iw * ih)
        union = float(aw * ah + bw * bh - inter)
        if union <= 0:
            return 0.0
        return inter / union

    def _find_best_match_rect(
        self,
        anchor: tuple[int, int, int, int],
        rects: list[tuple[int, int, int, int]],
        min_iou: float = 0.15,
    ) -> Optional[tuple[int, int, int, int]]:
        best_rect: Optional[tuple[int, int, int, int]] = None
        best_score = 0.0
        for rect in rects:
            score = self._rect_iou(anchor, rect)
            if score > best_score:
                best_score = score
                best_rect = rect
        if best_rect is None or best_score < float(min_iou):
            return None
        return best_rect

    def _load_picker_settings(self) -> None:
        try:
            value = readme_settings_async(
                "face_detector_settings", "picker_frame_color"
            )
            text = str(value).strip() if value is not None else ""
            c = QColor(text) if text else QColor()
            if not c.isValid():
                c = QColor(
                    random.randint(20, 235),
                    random.randint(20, 235),
                    random.randint(20, 235),
                )
            self._picker_color = c
        except Exception:
            self._picker_color = QColor(
                random.randint(20, 235),
                random.randint(20, 235),
                random.randint(20, 235),
            )

    def _load_recognition_frame_color(self) -> None:
        try:
            value = readme_settings_async(
                "face_detector_settings", "picker_frame_color"
            )
            text = str(value).strip() if value is not None else ""
            c = QColor(text) if text else QColor()
            self._picker_color = c if c.isValid() else QColor(255, 255, 255)
        except Exception:
            self._picker_color = QColor(255, 255, 255)

    def _compute_circle_from_rect(
        self, rect: tuple[int, int, int, int]
    ) -> tuple[int, int, int]:
        x, y, w, h = rect
        cx = int(x + w / 2)
        cy = int(y + h / 2)
        r = int(max(w, h) / 2) + 4
        return cx, cy, r

    def _schedule_next_pick_tick(self) -> None:
        if not self._picking_active or not self._picking_started:
            return
        total = int(self._picking_total_steps)
        duration = int(self._picking_duration_ms)
        if total <= 0:
            total = 1
        if duration <= 0:
            duration = 2000
        interval_ms = int(round(duration / float(total)))
        self._picking_timer.start(max(10, interval_ms))

    def _on_picking_tick(self) -> None:
        if (
            not self._detection_active
            or not self._picking_active
            or not self._picking_started
        ):
            return
        if self._commit_pending:
            self._commit_locked_face()
            return

        candidates = self._latest_faces or []
        if not candidates:
            self._schedule_next_pick_tick()
            return

        if self._picking_step >= self._picking_total_steps - 1:
            self._begin_commit_sequence(candidates)
            return

        rect = random.choice(candidates)
        self._set_overlay_for_rect(rect)
        self._picking_step += 1
        self._schedule_next_pick_tick()

    def _set_overlay_for_rect(self, rect: tuple[int, int, int, int]) -> None:
        self._current_pick_rect = rect
        self._overlay_circles = [self._compute_circle_from_rect(rect)]
        self._overlay_colors = [
            self._picker_color
            if self._picker_color.isValid()
            else QColor(255, 255, 255)
        ]

    def _begin_commit_sequence(
        self, candidates: list[tuple[int, int, int, int]]
    ) -> None:
        if not candidates:
            self._stop_detection_and_reset()
            self._show_message("no_face_detected")
            return

        try:
            target = int(self._target_pick_count)
        except Exception:
            target = 1
        target = max(1, min(target, 100))

        try:
            pool = list(candidates)
            target = min(target, len(pool))
            selected = random.sample(pool, k=target)
        except Exception:
            selected = [random.choice(candidates)]

        self._picked_faces = list(selected)
        self._picked_face_pixmaps = []
        self._commit_index = 0
        self._commit_pending = True
        self._lock_current_commit_target()

    def _lock_current_commit_target(self) -> None:
        if self._commit_index >= len(self._picked_faces):
            self._finish_commit_sequence()
            return
        rect = self._picked_faces[self._commit_index]
        self._set_overlay_for_rect(rect)
        self._picking_timer.start(220)

    def _commit_locked_face(self) -> None:
        if self._commit_index >= len(self._picked_faces):
            self._finish_commit_sequence()
            return

        rect = self._current_pick_rect or self._picked_faces[self._commit_index]

        qimage: Optional[QImage] = None
        try:
            if self._latest_frame is not None:
                qimage = bgr_frame_to_qimage(self._latest_frame)
        except Exception:
            qimage = None
        if (
            qimage is None
            and self._latest_qimage is not None
            and not self._latest_qimage.isNull()
        ):
            qimage = self._latest_qimage

        if qimage is not None:
            try:
                self._picked_face_pixmaps.append(self._crop_face_pixmap(qimage, rect))
            except Exception:
                pass

        self._commit_index += 1
        self._lock_current_commit_target()

    def _finish_commit_sequence(self) -> None:
        self._commit_pending = False
        self._picking_active = False
        self._picking_timer.stop()
        self._overlay_circles = []
        self._overlay_colors = []

        pixmap = self._compose_result_pixmap(self._picked_face_pixmaps)
        rect = self._picked_faces[0] if self._picked_faces else None
        self._show_final_result(pixmap, rect)

    def _compose_result_pixmap(self, pixmaps: list[QPixmap]) -> Optional[QPixmap]:
        items = [p for p in pixmaps if p is not None and not p.isNull()]
        if not items:
            return None
        if len(items) == 1:
            return items[0]

        import math

        count = len(items)
        cols = int(math.ceil(math.sqrt(count)))
        rows = int(math.ceil(count / float(cols)))
        cell = 240
        spacing = 12
        width = cols * cell + (cols - 1) * spacing
        height = rows * cell + (rows - 1) * spacing
        canvas = QPixmap(int(width), int(height))
        canvas.fill(QColor(0, 0, 0, 0))

        painter = QPainter(canvas)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)
        painter.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform, True)

        for idx, pix in enumerate(items):
            r = idx // cols
            c = idx % cols
            x = c * (cell + spacing)
            y = r * (cell + spacing)
            target = QRect(int(x), int(y), int(cell), int(cell))
            scaled = pix.scaled(
                target.size(),
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation,
            )
            dx = target.x() + int((target.width() - scaled.width()) / 2)
            dy = target.y() + int((target.height() - scaled.height()) / 2)
            painter.drawPixmap(dx, dy, scaled)

        painter.end()
        return canvas

    def _show_final_result(
        self, pixmap: Optional[QPixmap], rect: Optional[tuple[int, int, int, int]]
    ) -> None:
        self._final_selected_rect = rect
        self._final_face_pixmap = pixmap

        self._detection_active = False
        try:
            self.detector_enabled_changed.emit(False)
        except Exception:
            pass
        try:
            self._camera_opacity_effect.setOpacity(0.0)
        except Exception:
            pass
        try:
            self.preview_stack.setCurrentWidget(self.result_label)
            self._update_result_pixmap()
        except Exception:
            pass

        if self._audio_loop_started:
            try:
                camera_preview_audio_player.stop(wait=False)
            except Exception:
                pass
            self._audio_loop_started = False

        if self._play_result_audio:
            try:
                camera_preview_audio_player.play(
                    "face/result.wav", loop=False, volume=1.0
                )
            except Exception:
                pass

        self._final_view_timer.start(2500)

    def _crop_face_pixmap(
        self, qimage: QImage, rect: tuple[int, int, int, int]
    ) -> QPixmap:
        x, y, w, h = rect
        frame_rect = QRect(0, 0, qimage.width(), qimage.height())
        base_rect = QRect(int(x), int(y), int(w), int(h)).intersected(frame_rect)
        try:
            ex = int(max(8, round(float(w) * 0.30)))
            ey = int(max(8, round(float(h) * 0.20)))
            top_extra = int(max(8, round(float(h) * 0.45)))
        except Exception:
            ex, ey, top_extra = 8, 8, 12
        crop_rect = QRect(
            int(x) - ex,
            int(y) - top_extra,
            int(w) + ex * 2,
            int(h) + ey + top_extra,
        ).intersected(frame_rect)
        if crop_rect.width() <= 2 or crop_rect.height() <= 2:
            crop_rect = base_rect
        if crop_rect.width() <= 2 or crop_rect.height() <= 2:
            return QPixmap.fromImage(qimage)

        face_img = qimage.copy(crop_rect)
        return QPixmap.fromImage(face_img)

    def _set_final_selection(self, rect: tuple[int, int, int, int]) -> None:
        self._picking_active = False
        self._picking_timer.stop()
        self._overlay_circles = []
        self._overlay_colors = []
        self._final_selected_rect = rect
        self._final_view_active = False

        qimage: Optional[QImage] = None
        try:
            if self._latest_frame is not None:
                qimage = bgr_frame_to_qimage(self._latest_frame)
        except Exception:
            qimage = None

        if (
            qimage is None
            and self._latest_qimage is not None
            and not self._latest_qimage.isNull()
        ):
            qimage = self._latest_qimage

        self._final_face_pixmap = None
        if qimage is not None:
            try:
                self._final_face_pixmap = self._crop_face_pixmap(qimage, rect)
            except Exception:
                self._final_face_pixmap = None

        self._detection_active = False
        try:
            self.detector_enabled_changed.emit(False)
        except Exception:
            pass
        try:
            self._camera_opacity_effect.setOpacity(0.0)
        except Exception:
            pass
        try:
            self.preview_stack.setCurrentWidget(self.result_label)
            self._update_result_pixmap()
        except Exception:
            pass

        if self._audio_loop_started:
            try:
                camera_preview_audio_player.stop(wait=False)
            except Exception:
                pass
            self._audio_loop_started = False

        if self._play_result_audio:
            try:
                camera_preview_audio_player.play(
                    "face/result.wav", loop=False, volume=1.0
                )
            except Exception:
                pass

        self._final_view_timer.start(2500)

    def _show_message(self, key: str, details: str = "") -> None:
        """显示友好的错误消息框，可选包含诊断信息。"""
        title = get_content_name_async("camera_preview", key)
        message = get_content_description_async("camera_preview", key)

        if not title:
            title = get_content_name_async("camera_preview", "diagnostic_title") or ""
        if not message:
            message = (
                details
                or get_content_description_async("camera_preview", "diagnostic_title")
                or ""
            )

        if details and message and details not in message:
            message = f"{message}\n\n{details}"

        box = QMessageBox(self)
        box.setWindowTitle(title)
        box.setText(message)
        box.setIcon(QMessageBox.Icon.Warning)
        box.exec()

    def closeEvent(self, event: QCloseEvent) -> None:
        """页面关闭时释放资源。"""
        self._clear_timer.stop()
        self._no_face_timer.stop()
        self._picking_timer.stop()
        self._final_view_timer.stop()
        self.detector_enabled_changed.emit(False)
        if self._capture_worker is not None:
            if self._capture_thread is not None and self._capture_thread.isRunning():
                QMetaObject.invokeMethod(
                    self._capture_worker,
                    "stop",
                    Qt.ConnectionType.BlockingQueuedConnection,
                )
            else:
                try:
                    self._capture_worker.stop()
                except Exception:
                    pass
        else:
            self.capture_stop_requested.emit()

        for thread in [self._capture_thread, self._detector_thread]:
            if thread is None:
                continue
            try:
                thread.quit()
                thread.wait(1500)
            except Exception as exc:
                logger.exception("线程关闭失败: {}", exc)

        super().closeEvent(event)
