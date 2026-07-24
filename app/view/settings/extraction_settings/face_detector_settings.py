from __future__ import annotations
import os

from loguru import logger
from PySide2.QtCore import QTimer, QUrl
from PySide2.QtGui import QDesktopServices
from PySide2.QtWidgets import QHBoxLayout, QWidget, QVBoxLayout
from qfluentwidgets import (
    BodyLabel,
    ComboBox,
    ColorConfigItem,
    ColorSettingCard,
    GroupHeaderCardWidget,
    PushButton,
    SpinBox,
    SwitchButton,
)

from app.Language.obtain_language import (
    get_any_position_value_async,
    get_content_combo_name_async,
    get_content_description_async,
    get_content_name_async,
    get_content_pushbutton_name_async,
    get_content_switchbutton_name_async,
)
from app.common.camera_preview_backend import (
    get_cached_camera_devices,
    list_camera_resolutions,
    warmup_camera_devices_async,
)
from app.tools.path_utils import get_data_path
from app.tools.personalised import get_theme_icon
from app.tools.settings_access import readme_settings_async, update_settings
from app.tools.variable import WIDTH_SPINBOX


class face_detector_settings(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.vBoxLayout = QVBoxLayout(self)
        self.vBoxLayout.setContentsMargins(0, 0, 0, 0)
        self.vBoxLayout.setSpacing(10)

        self.basic_settings_widget = face_detector_basic_settings(self)
        self.vBoxLayout.addWidget(self.basic_settings_widget)

        self.advanced_settings_widget = face_detector_advanced_settings(self)
        self.vBoxLayout.addWidget(self.advanced_settings_widget)


class _ModelComboBox(ComboBox):
    def __init__(self, refresh_callback, parent=None):
        super().__init__(parent)
        self._refresh_callback = refresh_callback

    def showPopup(self):
        try:
            if self._refresh_callback is not None:
                self._refresh_callback()
        except Exception:
            pass
        return super().showPopup()


class face_detector_basic_settings(GroupHeaderCardWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setTitle(
            get_content_name_async("face_detector_settings", "basic_settings")
        )
        self.setBorderRadius(8)
        self._media_devices = None
        self._camera_devices = []
        self._camera_poll_left = 0

        self.camera_combo = _ModelComboBox(self._refresh_camera_list)
        self.camera_combo.currentIndexChanged.connect(self._on_camera_changed)
        QTimer.singleShot(0, self._init_camera_combo)

        self.camera_resolution_combo = ComboBox()
        self.camera_resolution_combo.currentTextChanged.connect(
            self._on_camera_resolution_changed
        )

        self.picking_duration_spin = SpinBox()
        self.picking_duration_spin.setFixedWidth(WIDTH_SPINBOX)
        self.picking_duration_spin.setRange(1, 10)
        self.picking_duration_spin.setSingleStep(1)
        self.picking_duration_spin.setSuffix("s")
        try:
            current = readme_settings_async(
                "face_detector_settings", "picking_duration_seconds"
            )
            self.picking_duration_spin.setValue(
                int(current) if current is not None else 2
            )
        except Exception:
            self.picking_duration_spin.setValue(2)
        self.picking_duration_spin.valueChanged.connect(
            lambda: update_settings(
                "face_detector_settings",
                "picking_duration_seconds",
                int(self.picking_duration_spin.value()),
            )
        )

        self.preview_mode_combo = ComboBox()
        self.preview_mode_combo.addItems(
            get_content_combo_name_async(
                "face_detector_settings", "camera_preview_mode"
            )
        )
        try:
            current = readme_settings_async(
                "face_detector_settings", "camera_preview_mode"
            )
            current_idx = int(current) if current is not None else 0
        except Exception:
            current_idx = 0
        current_idx = 0 if current_idx not in (0, 1) else current_idx
        self.preview_mode_combo.setCurrentIndex(current_idx)
        self.preview_mode_combo.currentIndexChanged.connect(
            lambda: update_settings(
                "face_detector_settings",
                "camera_preview_mode",
                self.preview_mode_combo.currentIndex(),
            )
        )

        self.play_process_audio_switch = SwitchButton()
        self.play_process_audio_switch.setOffText(
            get_content_switchbutton_name_async(
                "face_detector_settings", "play_process_audio", "disable"
            )
        )
        self.play_process_audio_switch.setOnText(
            get_content_switchbutton_name_async(
                "face_detector_settings", "play_process_audio", "enable"
            )
        )
        _process_audio = readme_settings_async(
            "face_detector_settings", "play_process_audio"
        )
        self.play_process_audio_switch.setChecked(
            True if _process_audio is None else bool(_process_audio)
        )
        self.play_process_audio_switch.checkedChanged.connect(
            lambda state: update_settings(
                "face_detector_settings", "play_process_audio", bool(state)
            )
        )

        self.play_result_audio_switch = SwitchButton()
        self.play_result_audio_switch.setOffText(
            get_content_switchbutton_name_async(
                "face_detector_settings", "play_result_audio", "disable"
            )
        )
        self.play_result_audio_switch.setOnText(
            get_content_switchbutton_name_async(
                "face_detector_settings", "play_result_audio", "enable"
            )
        )
        _result_audio = readme_settings_async(
            "face_detector_settings", "play_result_audio"
        )
        self.play_result_audio_switch.setChecked(
            True if _result_audio is None else bool(_result_audio)
        )
        self.play_result_audio_switch.checkedChanged.connect(
            lambda state: update_settings(
                "face_detector_settings", "play_result_audio", bool(state)
            )
        )

        self.addGroup(
            get_theme_icon("ic_fluent_camera_20_filled"),
            get_content_name_async("face_detector_settings", "camera_source"),
            get_content_description_async("face_detector_settings", "camera_source"),
            self.camera_combo,
        )

        self.addGroup(
            get_theme_icon("ic_fluent_resize_20_filled"),
            get_content_name_async(
                "face_detector_settings", "camera_display_resolution"
            ),
            get_content_description_async(
                "face_detector_settings", "camera_display_resolution"
            ),
            self.camera_resolution_combo,
        )

        self.addGroup(
            get_theme_icon("ic_fluent_reading_mode_mobile_20_filled"),
            get_content_name_async("face_detector_settings", "camera_preview_mode"),
            get_content_description_async(
                "face_detector_settings", "camera_preview_mode"
            ),
            self.preview_mode_combo,
        )

        self.addGroup(
            get_theme_icon("ic_fluent_timer_20_filled"),
            get_content_name_async(
                "face_detector_settings", "picking_duration_seconds"
            ),
            get_content_description_async(
                "face_detector_settings", "picking_duration_seconds"
            ),
            self.picking_duration_spin,
        )

        self.addGroup(
            get_theme_icon("ic_fluent_speaker_2_20_filled"),
            get_content_name_async("face_detector_settings", "play_process_audio"),
            get_content_description_async(
                "face_detector_settings", "play_process_audio"
            ),
            self.play_process_audio_switch,
        )

        self.addGroup(
            get_theme_icon("ic_fluent_speaker_edit_20_filled"),
            get_content_name_async("face_detector_settings", "play_result_audio"),
            get_content_description_async(
                "face_detector_settings", "play_result_audio"
            ),
            self.play_result_audio_switch,
        )

        self.frame_color_item = ColorConfigItem(
            "face_detector_settings",
            "picker_frame_color",
            readme_settings_async("face_detector_settings", "picker_frame_color"),
        )
        self.frame_color_item.valueChanged.connect(
            lambda color: update_settings(
                "face_detector_settings", "picker_frame_color", color.name()
            )
        )

        self.frame_color_card = ColorSettingCard(
            self.frame_color_item,
            get_theme_icon("ic_fluent_text_color_20_filled"),
            self.tr(
                get_content_name_async("face_detector_settings", "picker_frame_color")
            ),
            self.tr(
                get_content_description_async(
                    "face_detector_settings", "picker_frame_color"
                )
            ),
            self,
        )
        self.vBoxLayout.addWidget(self.frame_color_card)

    def _init_camera_combo(self) -> None:
        self._camera_poll_left = 30
        self._refresh_camera_list()
        self._apply_saved_camera_selection()
        self._refresh_camera_resolution_list()
        if self.camera_combo.count() <= 0:
            try:
                warmup_camera_devices_async(force_refresh=False)
            except Exception:
                pass
            self._schedule_camera_poll()

    def _list_cameras(self, force_refresh: bool = False):
        try:
            devices = get_cached_camera_devices()
            if force_refresh or not devices:
                warmup_camera_devices_async(force_refresh=force_refresh)
            return devices
        except Exception:
            return []

    def _schedule_camera_poll(self) -> None:
        if self._camera_poll_left <= 0:
            return
        self._camera_poll_left -= 1
        QTimer.singleShot(200, self._poll_camera_devices)

    def _poll_camera_devices(self) -> None:
        if self.camera_combo.count() > 0:
            return
        devices = self._list_cameras(force_refresh=False)
        if devices:
            self._refresh_camera_list()
            self._apply_saved_camera_selection()
            self._refresh_camera_resolution_list()
            return
        self._schedule_camera_poll()

    def _on_video_inputs_changed(self) -> None:
        self._refresh_camera_list(force_refresh=True)
        self._apply_saved_camera_selection()
        self._refresh_camera_resolution_list()
        self._schedule_camera_poll()

    def _refresh_camera_list(self, force_refresh: bool = False) -> None:
        current = None
        try:
            current = self.camera_combo.currentData()
        except Exception:
            current = None

        devices = self._list_cameras(force_refresh=force_refresh)
        self._camera_devices = list(devices)

        self.camera_combo.blockSignals(True)
        try:
            self.camera_combo.clear()
            for idx, device in enumerate(devices):
                self.camera_combo.addItem(device.name)
                try:
                    value = (
                        device.qt_id if getattr(device, "qt_id", "") else device.source
                    )
                    self.camera_combo.setItemData(idx, value)
                except Exception:
                    pass

            if current is not None and self.camera_combo.count() > 0:
                for idx in range(self.camera_combo.count()):
                    try:
                        if self.camera_combo.itemData(idx) == current:
                            self.camera_combo.setCurrentIndex(idx)
                            break
                    except Exception:
                        continue

            if self.camera_combo.count() > 0 and self.camera_combo.currentIndex() < 0:
                self.camera_combo.setCurrentIndex(0)
        finally:
            self.camera_combo.blockSignals(False)

    def _on_camera_changed(self, _index: int) -> None:
        value = None
        try:
            value = self.camera_combo.currentData()
        except Exception:
            value = None
        if value is None:
            return
        update_settings("face_detector_settings", "camera_source", value)
        self._refresh_camera_resolution_list()

    def _get_camera_resolution_map(self) -> dict:
        value = readme_settings_async(
            "face_detector_settings", "camera_display_resolution_map"
        )
        return value if isinstance(value, dict) else {}

    def _get_camera_key_variants(self, camera_id: object) -> list[str]:
        keys: list[object] = []
        if camera_id is not None:
            keys.append(camera_id)

        for device in self._camera_devices:
            try:
                if (
                    device.qt_id == camera_id
                    or str(device.qt_id) == str(camera_id)
                    or device.source == camera_id
                    or str(device.source) == str(camera_id)
                ):
                    if getattr(device, "qt_id", ""):
                        keys.append(device.qt_id)
                    keys.append(device.source)
                    break
            except Exception:
                continue

        normalized: list[str] = []
        for k in keys:
            try:
                kk = str(k).strip()
            except Exception:
                continue
            if kk and kk not in normalized:
                normalized.append(kk)
        return normalized

    def _normalize_resolution_text(self, value: object) -> str | None:
        if value is None:
            return None
        try:
            text = str(value).strip()
        except Exception:
            return None
        if not text:
            return None

        for sep in ("(", "（"):
            if sep in text:
                text = text.split(sep, 1)[0].strip()
                break

        text = (
            text.replace("×", "x")
            .replace("X", "x")
            .replace(" ", "")
            .replace("\t", "")
            .strip()
        )

        if "x" not in text:
            return None
        w_str, h_str = text.split("x", 1)
        try:
            w = int(w_str)
            h = int(h_str)
        except Exception:
            return None
        if w <= 0 or h <= 0:
            return None
        return f"{w}x{h}"

    def _set_camera_resolution_for_camera(
        self, camera_id: object, resolution: str
    ) -> None:
        normalized_keys = self._get_camera_key_variants(camera_id)
        if not normalized_keys:
            return

        normalized_resolution = self._normalize_resolution_text(resolution)
        if not normalized_resolution:
            return

        mapping = self._get_camera_resolution_map()
        for k in normalized_keys:
            mapping[k] = normalized_resolution
        try:
            update_settings(
                "face_detector_settings", "camera_display_resolution_map", mapping
            )
            try:
                camera_name = str(self.camera_combo.currentText()).strip()
            except Exception:
                camera_name = ""
            logger.info(
                f"摄像头预览分辨率已保存: {camera_name or 'Camera'} -> {normalized_resolution}"
            )
        except Exception as e:
            logger.exception(f"摄像头预览分辨率保存失败: {e}")

    def _refresh_camera_resolution_list(self) -> None:
        camera_id = None
        try:
            camera_id = self.camera_combo.currentData()
        except Exception:
            camera_id = None

        try:
            resolutions = list_camera_resolutions(camera_id)
        except Exception:
            resolutions = []

        try:
            suffix = get_any_position_value_async(
                "face_detector_settings",
                "camera_display_resolution",
                "recommended_suffix",
            )
            suffix = str(suffix).strip() if suffix is not None else ""
        except Exception:
            suffix = ""
        if not suffix:
            suffix = "推荐"

        self.camera_resolution_combo.blockSignals(True)
        try:
            self.camera_resolution_combo.clear()
            for i, (w, h) in enumerate(resolutions):
                text = f"{int(w)} x {int(h)}"
                if i == 0:
                    text = f"{text} ({suffix})"
                self.camera_resolution_combo.addItem(text, f"{int(w)}x{int(h)}")
        finally:
            self.camera_resolution_combo.blockSignals(False)

        if self.camera_resolution_combo.count() <= 0:
            return

        saved_map = self._get_camera_resolution_map()
        saved = None
        for key in self._get_camera_key_variants(camera_id):
            try:
                saved = saved_map.get(key)
            except Exception:
                saved = None
            if saved:
                break

        target_index = 0
        normalized_saved = self._normalize_resolution_text(saved)
        matched = False
        if normalized_saved:
            for idx in range(self.camera_resolution_combo.count()):
                try:
                    data = self.camera_resolution_combo.itemData(idx)
                    data_norm = self._normalize_resolution_text(data)
                    if data_norm and data_norm == normalized_saved:
                        target_index = idx
                        matched = True
                        break
                except Exception:
                    continue

        if normalized_saved and not matched:
            try:
                w_str, h_str = normalized_saved.split("x", 1)
                text = f"{int(w_str)} x {int(h_str)}"
            except Exception:
                text = normalized_saved
            self.camera_resolution_combo.blockSignals(True)
            try:
                self.camera_resolution_combo.addItem(text, normalized_saved)
                target_index = self.camera_resolution_combo.count() - 1
            finally:
                self.camera_resolution_combo.blockSignals(False)

        self.camera_resolution_combo.blockSignals(True)
        try:
            self.camera_resolution_combo.setCurrentIndex(target_index)
        finally:
            self.camera_resolution_combo.blockSignals(False)

    def _on_camera_resolution_changed(self, _index: int) -> None:
        camera_id = None
        try:
            camera_id = self.camera_combo.currentData()
        except Exception:
            camera_id = None

        if camera_id is None:
            try:
                camera_id = readme_settings_async(
                    "face_detector_settings", "camera_source"
                )
            except Exception:
                camera_id = None
            if camera_id is None:
                return

        raw = None
        try:
            raw = self.camera_resolution_combo.currentData()
        except Exception:
            raw = None
        if raw is None:
            try:
                raw = self.camera_resolution_combo.currentText()
            except Exception:
                raw = None
        normalized = self._normalize_resolution_text(raw)
        if not normalized:
            return

        self._set_camera_resolution_for_camera(camera_id, normalized)

    def _apply_saved_camera_selection(self) -> None:
        saved = readme_settings_async("face_detector_settings", "camera_source")
        if saved is None:
            if self.camera_combo.count() > 0:
                self.camera_combo.blockSignals(True)
                try:
                    self.camera_combo.setCurrentIndex(0)
                finally:
                    self.camera_combo.blockSignals(False)
                try:
                    value = self.camera_combo.currentData()
                except Exception:
                    value = None
                if value is not None:
                    update_settings("face_detector_settings", "camera_source", value)
            return

        target_index = -1
        for idx in range(self.camera_combo.count()):
            try:
                data = self.camera_combo.itemData(idx)
            except Exception:
                data = None

            if data == saved or str(data) == str(saved):
                target_index = idx
                break

        if target_index < 0:
            for idx, device in enumerate(self._camera_devices):
                try:
                    if (
                        device.source == saved
                        or str(device.source) == str(saved)
                        or device.qt_id == saved
                        or str(device.qt_id) == str(saved)
                    ):
                        target_index = idx
                        break
                except Exception:
                    continue

        if target_index >= 0:
            self.camera_combo.blockSignals(True)
            try:
                self.camera_combo.setCurrentIndex(target_index)
            finally:
                self.camera_combo.blockSignals(False)
            try:
                value = self.camera_combo.currentData()
            except Exception:
                value = None
            if value is not None:
                update_settings("face_detector_settings", "camera_source", value)
            return


class face_detector_advanced_settings(GroupHeaderCardWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setTitle(
            get_content_name_async("face_detector_settings", "advanced_settings")
        )
        self.setBorderRadius(8)

        self.detector_type_combo = _ModelComboBox(self._refresh_model_list)
        self._refresh_model_list()
        self._apply_saved_selection()

        self.detector_type_combo.currentTextChanged.connect(
            self._on_detector_type_changed
        )

        self.open_model_folder_button = PushButton(
            get_content_pushbutton_name_async(
                "face_detector_settings", "open_model_folder"
            )
        )
        self.open_model_folder_button.clicked.connect(self.open_model_folder)

        self.model_input_width_spin = SpinBox()
        self.model_input_width_spin.setFixedWidth(160)
        self.model_input_width_spin.setRange(0, 4096)
        self.model_input_width_spin.setSingleStep(16)
        self.model_input_width_spin.setSuffix("px")
        try:
            current = readme_settings_async(
                "face_detector_settings", "model_input_width"
            )
            self.model_input_width_spin.setValue(
                int(current) if current is not None else 0
            )
        except Exception:
            self.model_input_width_spin.setValue(0)
        self.model_input_width_spin.valueChanged.connect(
            lambda: update_settings(
                "face_detector_settings",
                "model_input_width",
                int(self.model_input_width_spin.value()),
            )
        )

        self.model_input_height_spin = SpinBox()
        self.model_input_height_spin.setFixedWidth(160)
        self.model_input_height_spin.setRange(0, 4096)
        self.model_input_height_spin.setSingleStep(16)
        self.model_input_height_spin.setSuffix("px")
        try:
            current = readme_settings_async(
                "face_detector_settings", "model_input_height"
            )
            self.model_input_height_spin.setValue(
                int(current) if current is not None else 0
            )
        except Exception:
            self.model_input_height_spin.setValue(0)
        self.model_input_height_spin.valueChanged.connect(
            lambda: update_settings(
                "face_detector_settings",
                "model_input_height",
                int(self.model_input_height_spin.value()),
            )
        )

        self.model_input_size_widget = QWidget(self)
        model_size_layout = QHBoxLayout(self.model_input_size_widget)
        model_size_layout.setContentsMargins(0, 0, 0, 0)
        model_size_layout.setSpacing(8)
        model_size_layout.addWidget(self.model_input_width_spin)
        model_size_layout.addWidget(BodyLabel("×"))
        model_size_layout.addWidget(self.model_input_height_spin)
        model_size_layout.addStretch(1)

        self.addGroup(
            get_theme_icon("ic_fluent_scan_object_20_filled"),
            get_content_name_async("face_detector_settings", "detector_type"),
            get_content_description_async("face_detector_settings", "detector_type"),
            self.detector_type_combo,
        )

        self.addGroup(
            get_theme_icon("ic_fluent_folder_open_20_filled"),
            get_content_name_async("face_detector_settings", "open_model_folder"),
            get_content_description_async(
                "face_detector_settings", "open_model_folder"
            ),
            self.open_model_folder_button,
        )

        self.addGroup(
            get_theme_icon("ic_fluent_resize_20_filled"),
            get_content_name_async("face_detector_settings", "model_input_size"),
            get_content_description_async("face_detector_settings", "model_input_size"),
            self.model_input_size_widget,
        )

    def _model_dir(self):
        return get_data_path("cv_models")

    def _list_model_names(self) -> list[str]:
        model_dir = self._model_dir()
        try:
            if not model_dir.exists():
                os.makedirs(model_dir, exist_ok=True)
        except Exception:
            pass

        try:
            items = []
            for p in sorted(model_dir.glob("*.onnx")):
                if p.is_file():
                    items.append(p.name)
            return items
        except Exception:
            return []

    def _refresh_model_list(self) -> None:
        current = (self.detector_type_combo.currentText() or "").strip()
        saved_text = ""
        try:
            saved = readme_settings_async("face_detector_settings", "detector_type")
            saved_text = str(saved).strip() if saved is not None else ""
        except Exception:
            saved_text = ""
        preferred = current or saved_text
        items = self._list_model_names()
        self.detector_type_combo.blockSignals(True)
        try:
            self.detector_type_combo.clear()
            self.detector_type_combo.addItems(items)
            if preferred:
                idx = self.detector_type_combo.findText(preferred)
                if idx >= 0:
                    self.detector_type_combo.setCurrentIndex(idx)
            if (
                self.detector_type_combo.count() > 0
                and self.detector_type_combo.currentIndex() < 0
            ):
                self.detector_type_combo.setCurrentIndex(0)
        finally:
            self.detector_type_combo.blockSignals(False)

    def _apply_saved_selection(self) -> None:
        saved = readme_settings_async("face_detector_settings", "detector_type")
        saved_text = ""
        try:
            if isinstance(saved, int):
                idx = int(saved)
                if 0 <= idx < self.detector_type_combo.count():
                    saved_text = self.detector_type_combo.itemText(idx)
            else:
                saved_text = str(saved).strip() if saved is not None else ""
        except Exception:
            saved_text = ""

        if saved_text:
            idx = self.detector_type_combo.findText(saved_text)
            if idx >= 0:
                self.detector_type_combo.blockSignals(True)
                try:
                    self.detector_type_combo.setCurrentIndex(idx)
                finally:
                    self.detector_type_combo.blockSignals(False)
                return

        if self.detector_type_combo.count() > 0:
            self.detector_type_combo.blockSignals(True)
            try:
                self.detector_type_combo.setCurrentIndex(0)
            finally:
                self.detector_type_combo.blockSignals(False)

    def _on_detector_type_changed(self, text: object) -> None:
        value = ""
        try:
            value = str(text).strip() if text is not None else ""
        except Exception:
            value = ""
        if not value or value.isdigit():
            return
        update_settings("face_detector_settings", "detector_type", value)

    def open_model_folder(self) -> None:
        folder_path = self._model_dir()
        try:
            if not folder_path.exists():
                os.makedirs(folder_path, exist_ok=True)
            QDesktopServices.openUrl(QUrl.fromLocalFile(str(folder_path)))
        except Exception:
            logger.exception("无法打开模型文件夹: {}", folder_path)
