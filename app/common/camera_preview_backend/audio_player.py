from __future__ import annotations

import os
import threading
from typing import Optional

from loguru import logger


try:
    import sounddevice as sd
except Exception as e:
    sd = None
    logger.warning(f"sounddevice 不可用: {e}")

try:
    import soundfile as sf
except Exception as e:
    sf = None
    logger.warning(f"soundfile 不可用: {e}")

try:
    import numpy as np
except Exception as e:
    np = None
    logger.warning(f"numpy 不可用: {e}")


class CameraPreviewAudioPlayer:
    def __init__(self) -> None:
        self._lock = threading.Lock()
        self._last_error: Optional[str] = None
        self._is_playing: bool = False
        self._stop_flag: threading.Event = threading.Event()
        self._play_thread: Optional[threading.Thread] = None
        self._current_audio_path: Optional[str] = None
        self._volume: float = 1.0
        self._loop: bool = False
        self._qt_player: Optional[object] = None
        self._qt_audio_out: Optional[object] = None

    def play(
        self, audio_relative_path: str, loop: bool = False, volume: float = 1.0
    ) -> bool:
        audio_relative_path = str(audio_relative_path or "").strip()
        if not audio_relative_path:
            return False

        audio_path_str = audio_relative_path
        if not os.path.isabs(audio_path_str):
            from app.tools.path_utils import get_audio_path

            audio_path_str = str(get_audio_path(audio_relative_path))

        if not os.path.exists(audio_path_str):
            logger.error(f"音频文件不存在: {audio_path_str}")
            return False

        if not os.path.isfile(audio_path_str):
            logger.error(f"音频路径不是文件: {audio_path_str}")
            return False

        self.stop(wait=False)

        vol = max(0.0, min(float(volume), 1.0))
        if sd is not None and sf is not None and np is not None:
            try:
                with sf.SoundFile(audio_path_str):
                    pass
                with self._lock:
                    self._last_error = None
                    self._current_audio_path = audio_path_str
                    self._volume = vol
                    self._loop = bool(loop)
                    self._stop_flag.clear()
                    self._is_playing = True

                self._play_thread = threading.Thread(
                    target=self._play_audio_worker,
                    args=(audio_path_str, bool(loop)),
                    daemon=True,
                )
                self._play_thread.start()
                return True
            except Exception:
                pass

        return self._play_with_qt(audio_path_str, loop=bool(loop), volume=vol)

    def stop(self, wait: bool = False) -> None:
        logger.debug("停止播放音频")
        self._stop_flag.set()
        self._is_playing = False

        if self._play_thread and self._play_thread.is_alive():
            timeout = None if wait else 2.0
            self._play_thread.join(timeout=timeout)

        self._stop_qt()
        self._current_audio_path = None
        logger.debug("音频已停止")

    def is_playing(self) -> bool:
        if self._is_playing:
            return True
        with self._lock:
            return self._qt_player is not None

    def get_last_error(self) -> Optional[str]:
        with self._lock:
            return self._last_error

    def _play_audio_worker(self, audio_path: str, loop: bool) -> None:
        stream = None
        try:
            try:
                with sf.SoundFile(audio_path) as audio_file:
                    fs = int(audio_file.samplerate)
                    channels = int(audio_file.channels)
                    if fs <= 0 or channels <= 0:
                        with self._lock:
                            self._last_error = "Invalid audio format"
                        logger.error(f"音频文件参数无效: fs={fs}, channels={channels}")
                        return

                    try:
                        stream = sd.OutputStream(
                            samplerate=fs,
                            channels=1,
                            dtype="float32",
                            blocksize=4096,
                        )
                        stream.start()
                    except Exception as e:
                        with self._lock:
                            self._last_error = str(e)
                        logger.exception(f"初始化音频流失败: {e}")
                        return

                    chunk_size = 8192
                    while not self._stop_flag.is_set():
                        audio_file.seek(0)
                        while not self._stop_flag.is_set():
                            chunk = audio_file.read(
                                frames=chunk_size, dtype="float32", always_2d=True
                            )
                            if chunk.size == 0:
                                break

                            if channels > 1 and chunk.shape[1] > 1:
                                chunk = np.mean(chunk, axis=1, keepdims=True)
                            elif chunk.shape[1] != 1:
                                chunk = chunk[:, :1]

                            chunk *= self._volume

                            try:
                                stream.write(chunk)
                            except Exception as e:
                                with self._lock:
                                    self._last_error = str(e)
                                logger.exception(f"写入音频流失败: {e}")
                                return

                        if not loop or self._stop_flag.is_set():
                            break
            except Exception as e:
                with self._lock:
                    self._last_error = str(e)
                logger.exception(f"读取音频文件失败: {e}")
                return

        except Exception as e:
            with self._lock:
                self._last_error = str(e)
            logger.exception(f"音频播放工作线程异常: {e}")
        finally:
            if stream:
                try:
                    stream.stop()
                    stream.close()
                except Exception as e:
                    with self._lock:
                        self._last_error = str(e)
                    logger.exception(f"关闭音频流失败: {e}")
            self._is_playing = False

    def _stop_qt(self) -> None:
        player = None
        audio_out = None
        with self._lock:
            player = self._qt_player
            audio_out = self._qt_audio_out
            self._qt_player = None
            self._qt_audio_out = None

        if player is None:
            return

        try:
            player.stop()
        except Exception:
            pass
        try:
            player.deleteLater()
        except Exception:
            pass
        if audio_out is not None:
            try:
                audio_out.deleteLater()
            except Exception:
                pass

    def _play_with_qt(self, audio_path_str: str, loop: bool, volume: float) -> bool:
        try:
            from PySide2.QtCore import QUrl
            from PySide2.QtMultimedia import QAudioOutput, QMediaPlayer
        except Exception as e:
            with self._lock:
                self._last_error = str(e)
            return False

        self._stop_qt()

        vol = max(0.0, min(float(volume), 1.0))
        audio_out = QAudioOutput()
        try:
            audio_out.setVolume(vol)
        except Exception:
            pass

        player = QMediaPlayer()
        player.setAudioOutput(audio_out)
        try:
            setattr(player, "_cp_should_stop", False)  # noqa: B010
        except Exception:
            pass

        def cleanup() -> None:
            with self._lock:
                if self._qt_player is player:
                    self._qt_player = None
                    self._qt_audio_out = None
            try:
                player.stop()
            except Exception:
                pass
            try:
                player.deleteLater()
            except Exception:
                pass
            try:
                audio_out.deleteLater()
            except Exception:
                pass

        def on_error(*args) -> None:
            try:
                msg = ""
                if args:
                    msg = str(args[-1] or "")
                with self._lock:
                    self._last_error = msg or "qt playback error"
            except Exception:
                pass
            cleanup()

        try:

            def on_status_changed(status) -> None:
                try:
                    is_end = (
                        getattr(status, "name", "") == "EndOfMedia" or int(status) == 7
                    )
                except Exception:
                    is_end = False
                if not is_end:
                    return
                try:
                    should_stop = bool(getattr(player, "_cp_should_stop", False))
                except Exception:
                    should_stop = False
                if loop and not should_stop:
                    try:
                        player.setPosition(0)
                        player.play()
                        return
                    except Exception:
                        pass
                cleanup()

            player.mediaStatusChanged.connect(on_status_changed)
        except Exception:
            pass
        try:
            player.errorOccurred.connect(on_error)
        except Exception:
            pass

        try:
            player.setSource(QUrl.fromLocalFile(audio_path_str))
            player.play()
        except Exception as e:
            with self._lock:
                self._last_error = str(e)
            cleanup()
            return False

        with self._lock:
            self._last_error = None
            self._qt_player = player
            self._qt_audio_out = audio_out

        self._is_playing = True
        return True


camera_preview_audio_player = CameraPreviewAudioPlayer()
