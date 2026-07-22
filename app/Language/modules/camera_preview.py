camera_preview = {
    "ZH_CN": {
        "title": {"name": "人脸抽取", "description": "从摄像头抽取人脸"},
        "no_camera": {"name": "未检测到摄像头", "description": "未检测到摄像头设备"},
        "no_face_detected": {
            "name": "未识别到人脸",
            "description": "当前画面未识别到人脸，请调整距离/光线后重试。",
        },
        "diagnostic_title": {
            "name": "诊断信息",
            "description": "人脸识别失败时的诊断信息",
        },
        "start_button": {
            "name": "开始",
            "description": "开始随机框选人脸",
            "pushbutton_name": "开始",
        },
        "recognized_count": {
            "name": "识别到 {count} 人",
            "description": "识别模式下显示已识别人数",
        },
        "opencv_missing": {
            "name": "OpenCV 未安装",
            "description": "未检测到 OpenCV ，人脸识别不可用\n请安装 opencv-python。",
        },
        "numpy_missing": {
            "name": "NumPy 未安装",
            "description": "未检测到 NumPy ，人脸识别不可用\n请安装 numpy。",
        },
        "cascade_missing": {
            "name": "人脸模型缺失",
            "description": "未能加载 OpenCV 人脸模型文件，无法进行人脸识别\n请重新安装 opencv-python 或检查打包资源是否缺失。",
        },
        "camera_open_failed": {
            "name": "打开摄像头失败",
            "description": "无法打开摄像头，请检查是否被其它程序占用或权限受限。",
        },
        "model_missing": {
            "name": "检测模型缺失",
            "description": "未找到人脸检测模型文件，请将模型放到 data/cv_models 目录后重试。",
        },
        "model_incompatible": {
            "name": "模型不兼容",
            "description": "当前 ONNX 模型与现有人脸检测解析逻辑不兼容，请更换其它 ONNX 模型后重试。",
        },
        "detect_failed": {
            "name": "人脸检测失败",
            "description": "人脸检测过程中发生错误，请查看诊断信息。",
        },
        "unavailable": {
            "name": "摄像头不可用",
            "description": "当前环境不支持摄像头预览",
        },
    },
    "EN_US": {
        "title": {"name": "Camera", "description": "Camera preview"},
        "no_camera": {
            "name": "No camera detected",
            "description": "No camera devices found",
        },
        "no_face_detected": {
            "name": "No face detected",
            "description": "No face detected in the current frame. Adjust distance/lighting and try again.",
        },
        "diagnostic_title": {
            "name": "Diagnostics",
            "description": "Diagnostics shown when face detection fails",
        },
        "start_button": {
            "name": "Start",
            "description": "Randomly highlight a face",
            "pushbutton_name": "Start",
        },
        "recognized_count": {
            "name": "{count} face(s) detected",
            "description": "Detected face count shown in recognition mode",
        },
        "opencv_missing": {
            "name": "OpenCV not installed",
            "description": "OpenCV (cv2) is not available, so face recognition is disabled.\nRun uv sync or install opencv-python.",
        },
        "numpy_missing": {
            "name": "NumPy not installed",
            "description": "NumPy is not available, so face recognition is disabled.\nRun uv sync or install numpy.",
        },
        "cascade_missing": {
            "name": "Face model missing",
            "description": "Failed to load OpenCV face cascade data, so face recognition is disabled.\nReinstall opencv-python or ensure bundled resources include the cascade XML files.",
        },
        "camera_open_failed": {
            "name": "Failed to open camera",
            "description": "Unable to open the camera. It may be in use or blocked by permissions.",
        },
        "model_missing": {
            "name": "Model missing",
            "description": "Face detector model file was not found. Put the model into data/cv_models and try again.",
        },
        "model_incompatible": {
            "name": "Model incompatible",
            "description": "The selected ONNX model is not compatible with the current face detector implementation. Try another ONNX model.",
        },
        "detect_failed": {
            "name": "Detection failed",
            "description": "An error occurred during face detection. Check diagnostics for details.",
        },
        "unavailable": {
            "name": "Camera unavailable",
            "description": "Camera preview is not available",
        },
    },
    "JA_JP": {
        "title": {"name": "カメラ", "description": "カメラプレビュー"},
        "no_camera": {
            "name": "カメラが見つかりません",
            "description": "カメラデバイスが見つかりません",
        },
        "no_face_detected": {
            "name": "顔が検出されません",
            "description": "現在のフレームで顔が検出されません。距離や照明を調整して再試行してください。",
        },
        "diagnostic_title": {
            "name": "診断情報",
            "description": "顔検出に失敗した場合の診断情報",
        },
        "start_button": {
            "name": "開始",
            "description": "顔をランダムに強調表示",
            "pushbutton_name": "開始",
        },
        "recognized_count": {
            "name": "{count} 人を検出",
            "description": "認識モードで検出人数を表示",
        },
        "opencv_missing": {
            "name": "OpenCV が未インストール",
            "description": "OpenCV（cv2）が利用できないため、人顔認識は無効です。\nuv sync を実行するか opencv-python をインストールしてください。",
        },
        "numpy_missing": {
            "name": "NumPy が未インストール",
            "description": "NumPy が利用できないため、人顔認識は無効です。\nuv sync を実行するか numpy をインストールしてください。",
        },
        "cascade_missing": {
            "name": "顔モデルが見つかりません",
            "description": "OpenCV の顔モデル（カスケード）を読み込めないため、顔認識は無効です。\nopencv-python を再インストールするか、同梱リソースに XML が含まれているか確認してください。",
        },
        "camera_open_failed": {
            "name": "カメラを開けません",
            "description": "カメラを開けません。別のアプリで使用中、または権限が原因の可能性があります。",
        },
        "model_missing": {
            "name": "モデルが見つかりません",
            "description": "顔検出モデルが見つかりません。data/cv_models にモデルを配置して再試行してください。",
        },
        "model_incompatible": {
            "name": "モデル非対応",
            "description": "選択した ONNX モデルは現在の実装に対応していません。他の ONNX モデルをお試しください。",
        },
        "detect_failed": {
            "name": "検出に失敗しました",
            "description": "顔検出中にエラーが発生しました。診断情報をご確認ください。",
        },
        "unavailable": {
            "name": "カメラを利用できません",
            "description": "カメラプレビューを利用できません",
        },
    },
}
