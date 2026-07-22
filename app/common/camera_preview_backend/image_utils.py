from __future__ import annotations

from PySide2.QtGui import QImage


def bgr_frame_to_qimage(frame_bgr) -> QImage:
    """将 OpenCV BGR 帧（numpy 数组）转换为 QImage。"""
    import cv2

    rgb = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2RGB)
    height, width, channels = rgb.shape
    bytes_per_line = channels * width
    image = QImage(
        rgb.data,
        width,
        height,
        bytes_per_line,
        QImage.Format.Format_RGB888,
    )
    return image.copy()
