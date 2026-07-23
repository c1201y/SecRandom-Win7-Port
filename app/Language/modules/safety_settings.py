# 安全设置语言配置
safety_settings = {
    "ZH_CN": {"title": {"name": "安全设置", "description": "配置软件安全相关设置"}},
    "EN_US": {
        "title": {
            "name": "Security settings",
            "description": "Configure app safety related settings",
        }
    },
    "JA_JP": {
        "title": {
            "name": "セキュリティ設定",
            "description": "アプリのセキュリティ関連設定を設定",
        }
    },
}

# 基础安全设置语言配置
basic_safety_settings = {
    "ZH_CN": {
        "title": {"name": "基础安全设置", "description": "配置基础安全验证功能"},
        "verification_method": {
            "name": "验证方式",
            "description": "配置安全功能验证方式",
        },
        "verification_process": {
            "name": "安全验证步骤",
            "description": "选择安全验证组合方式",
            "combo_items": [
                "单步验证（任选一种方式）",
                "仅密码",
                "仅TOTP",
                "仅U盘解锁",
                "密码+TOTP",
                "密码+U盘解锁",
                "TOTP+U盘解锁",
                "密码+TOTP+U盘解锁",
            ],
        },
        "security_operations": {
            "name": "安全操作",
            "description": "配置需要安全验证的操作",
        },
        "safety_switch": {
            "name": "安全开关",
            "description": "启用后所有安全操作都需要验证密码",
            "switchbutton_name": {"enable": "", "disable": ""},
        },
        "set_password": {
            "name": "设置/修改密码",
            "description": "设置或修改安全验证密码",
        },
        "password_rules": {
            "name": "密码要求",
            "description": "长度≥8，且至少包含字母、数字、特殊字符中的任意两类（推荐三类）",
        },
        "current_password": {"name": "当前密码"},
        "password_input_placeholder": {"name": "输入密码进行校验"},
        "new_password": {"name": "新密码"},
        "confirm_password": {"name": "确认新密码"},
        "password_strength_title": {"name": "密码强度"},
        "strength_weak": {"name": "弱"},
        "strength_medium": {"name": "中"},
        "strength_strong": {"name": "强"},
        "save_button": {"name": "保存"},
        "cancel_button": {"name": "取消"},
        "error_current_password": {"name": "当前密码不正确"},
        "error_mismatch": {"name": "新密码与确认不一致"},
        "error_strength_insufficient": {"name": "密码强度不足"},
        "success_updated": {"name": "密码已更新"},
        "remove_password": {"name": "移除密码", "description": "取消当前安全验证密码"},
        "remove_password_confirm_title": {"name": "确认移除密码"},
        "remove_password_confirm_content": {
            "name": "移除密码后将禁用安全开关，是否继续？"
        },
        "remove_password_success": {"name": "已移除密码并关闭安全开关"},
        "error_title": {"name": "错误"},
        "dialog_yes_text": {"name": "确定"},
        "dialog_cancel_text": {"name": "取消"},
        "totp_switch": {
            "name": "TOTP验证",
            "description": "启用后可在安全操作中使用TOTP动态口令",
            "switchbutton_name": {"enable": "", "disable": ""},
        },
        "set_totp": {"name": "设置TOTP", "description": "配置TOTP动态口令验证"},
        "generate_totp_secret": {"name": "生成密钥"},
        "verify_totp_code": {"name": "校验验证码"},
        "totp_input_placeholder": {"name": "输入TOTP验证码进行校验"},
        "totp_secret_prefix": {"name": "密钥"},
        "totp_uri_prefix": {"name": "URI"},
        "totp_generated_saved": {"name": "已生成并保存TOTP密钥"},
        "totp_generated_error": {"name": "生成TOTP失败"},
        "totp_code_valid": {"name": "验证码有效"},
        "totp_code_invalid": {"name": "验证码无效"},
        "totp_save_success": {"name": "设置已保存"},
        "totp_verify_before_save": {"name": "请先校验验证码后再保存"},
        "totp_qr_unavailable": {"name": "未能显示二维码，请安装二维码库"},
        "usb_switch": {
            "name": "U盘验证",
            "description": "启用后可在安全操作中使用U盘验证",
            "switchbutton_name": {"enable": "", "disable": ""},
        },
        "bind_usb": {"name": "绑定U盘", "description": "绑定用于验证的U盘设备"},
        "unbind_usb": {"name": "解绑U盘", "description": "解除U盘设备绑定"},
        "usb_refresh": {"name": "刷新"},
        "usb_bind": {"name": "绑定"},
        "usb_unbind_all": {"name": "解绑全部"},
        "usb_no_removable": {"name": "未检测到可移动盘"},
        "usb_bind_success": {"name": "已绑定 U盘"},
        "usb_unbind_all_success": {"name": "已解绑全部 U盘"},
        "usb_require_key_file": {"name": "需要 .key 文件验证"},
        "totp_secret_generated": {"name": "已生成密钥，请完成验证后再保存"},
        "error_set_password_first": {"name": "请先设置密码"},
        "error_set_totp_first": {"name": "请先设置TOTP"},
        "error_bind_usb_first": {"name": "请先绑定U盘"},
        "verify_in_progress": {"name": "正在验证，请稍候"},
        "verify_failed_generic": {"name": "验证未通过，请检查输入"},
        "usb_unbind_selected": {"name": "解绑选中"},
        "usb_unbind_selected_success": {"name": "已解绑选中 U盘"},
        "usb_select_bound_hint": {"name": "请选择一个已绑定设备"},
        "usb_bound_devices": {"name": "已绑定设备"},
        "usb_status_connected": {"name": "U盘已连接"},
        "usb_status_disconnected": {"name": "U盘未连接"},
        "show_hide_floating_window_switch": {
            "name": "显示/隐藏浮窗验证",
            "description": "启用后显示或隐藏浮窗时需要安全验证",
            "switchbutton_name": {"enable": "", "disable": ""},
        },
        "restart_switch": {
            "name": "重启验证",
            "description": "启用后重启软件时需要安全验证",
            "switchbutton_name": {"enable": "", "disable": ""},
        },
        "exit_switch": {
            "name": "退出验证",
            "description": "启用后退出软件时需要安全验证",
            "switchbutton_name": {"enable": "", "disable": ""},
        },
        "open_settings_switch": {
            "name": "打开设置验证",
            "description": "启用后打开设置窗口时需要安全验证",
            "switchbutton_name": {"enable": "", "disable": ""},
        },
        "preview_settings": {"name": "预览设置"},
        "preview_settings_switch": {
            "name": "设置预览开关",
            "description": "进入设置的验证时允许预览设置",
            "switchbutton_name": {"enable": "", "disable": ""},
        },
    },
    "EN_US": {
        "title": {
            "name": "Basic security settings",
            "description": "Configure basic safety verification function",
        },
        "verification_method": {
            "name": "Verification method",
            "description": "Configure basic safety verification method",
        },
        "verification_process": {
            "name": "Verification process",
            "description": "Choose basic safety combination method",
            "combo_items": {
                "0": "One-step verification method (choose anyone)",
                "1": "Password only",
                "2": "TOTP only",
                "3": "USB drives only",
                "4": "Password + TOTP",
                "5": "Password + USB drives",
                "6": "TOTP + USB drives",
                "7": "Password + TOTP + USB drives",
            },
        },
        "security_operations": {
            "name": "Security operations",
            "description": "Configure actions need basic safety verification",
        },
        "safety_switch": {
            "name": "Safety switch",
            "description": "When enabled, all safety actions require password",
        },
        "set_password": {
            "name": "Set password",
            "description": "Set safety verification password",
        },
        "totp_switch": {
            "name": "TOTP verification",
            "description": "Enable to use the TOTP dynamic password in secure operations",
        },
        "set_totp": {
            "name": "Set TOTP",
            "description": "Configure TOTP one-time password verification",
        },
        "usb_switch": {
            "name": "USB drive verification",
            "description": "Enable to use USB drive verification in secure operations",
        },
        "bind_usb": {
            "name": "Bind USB drive",
            "description": "Bind the USB drive to verify",
        },
        "unbind_usb": {"name": "Unbind USB drive", "description": "Unbind USB drive"},
        "show_hide_floating_window_switch": {
            "name": "Show/hide float window verification",
            "description": "When enabled, showing or hiding float window will need verification",
        },
        "restart_switch": {
            "name": "Restart Verification",
            "description": "When enabled, restarting app will need verification",
        },
        "exit_switch": {
            "name": "Exit Verification",
            "description": "When enabled, exiting app will need verification",
        },
        "password_rules": {
            "name": "Password requirements",
            "description": "Length > 8, with at least two categories of letters, numbers, and special characters (recommended three categories)",
        },
        "current_password": {"name": "Current password"},
        "password_input_placeholder": {"name": "Enter password to verify"},
        "new_password": {"name": "New password"},
        "confirm_password": {"name": "Confirm new password"},
        "password_strength_title": {"name": "Password strength"},
        "strength_weak": {"name": "Weak"},
        "strength_medium": {"name": "Mid"},
        "strength_strong": {"name": "Strong"},
        "save_button": {"name": "Save"},
        "cancel_button": {"name": "Cancel"},
        "error_current_password": {"name": "Current password is incorrect"},
        "error_mismatch": {"name": "New password does not match confirmation"},
        "error_strength_insufficient": {"name": "Not enough password"},
        "success_updated": {"name": "Password updated"},
        "remove_password": {
            "name": "Remove password",
            "description": "Cancel current security verification password",
        },
        "remove_password_confirm_title": {"name": "Confirm Password Removal"},
        "remove_password_confirm_content": {
            "name": "Removing passwords will disable secure switches, continue?"
        },
        "remove_password_success": {
            "name": "Password removed and security switch closed"
        },
        "error_title": {"name": "Error"},
        "dialog_yes_text": {"name": "OK"},
        "dialog_cancel_text": {"name": "Cancel"},
        "generate_totp_secret": {"name": "Generate key"},
        "verify_totp_code": {"name": "Verify verification code"},
        "totp_input_placeholder": {"name": "Enter TOTP verification code to verify"},
        "totp_secret_prefix": {"name": "Key"},
        "totp_uri_prefix": {"name": "URI"},
        "totp_generated_saved": {"name": "Generated and saved TOTP key"},
        "totp_generated_error": {"name": "Failed to generate TOTP"},
        "totp_code_valid": {"name": "Valid code"},
        "totp_code_invalid": {"name": "Invalid code"},
        "totp_save_success": {"name": "Settings saved"},
        "totp_verify_before_save": {"name": "Please verify the code before saving"},
        "totp_qr_unavailable": {
            "name": "Failed to display QR code, please install QR library"
        },
        "usb_refresh": {"name": "Refresh"},
        "usb_bind": {"name": "Bind"},
        "usb_unbind_all": {"name": "Unbind All"},
        "usb_no_removable": {"name": "No removable disk detected"},
        "usb_bind_success": {"name": "USB drive binded"},
        "usb_unbind_all_success": {"name": "Unbound all USB drives"},
        "usb_require_key_file": {"name": ".key file verification required"},
        "totp_secret_generated": {
            "name": "Key generated, please complete validation before saving"
        },
        "error_set_password_first": {"name": "Please set password first"},
        "error_set_totp_first": {"name": "Please set TOTP first"},
        "error_bind_usb_first": {"name": "Please bind to a disk first"},
        "verify_in_progress": {"name": "Verifying, please wait"},
        "verify_failed_generic": {
            "name": "Verification not passed, please check input"
        },
        "usb_unbind_selected": {"name": "Unbind selected"},
        "usb_unbind_selected_success": {"name": "Unbound USB drives"},
        "usb_select_bound_hint": {"name": "Please select a bound device"},
        "usb_bound_devices": {"name": "Bind device"},
        "usb_status_connected": {"name": "USB drive connected"},
        "usb_status_disconnected": {"name": "USB drive unconnected"},
        "open_settings_switch": {
            "name": "Open settings validation",
            "description": "Secure authentication is required when opening settings",
        },
        "preview_settings": {"name": "Preview settings"},
        "preview_settings_switch": {
            "name": "Preview settings switch",
            "description": "Enable preview settings switch",
            "switchbutton_name": {"enable": "", "disable": ""},
        },
    },
    "JA_JP": {
        "title": {
            "name": "基本セキュリティ設定",
            "description": "基本セキュリティ認証機能を設定",
        },
        "verification_method": {
            "name": "認証方法",
            "description": "セキュリティ機能認証方法を設定",
        },
        "verification_process": {
            "name": "セキュリティ認証手順",
            "description": "セキュリティ認証の組み合わせ方法を選択",
            "combo_items": {
                "0": "単一ステップ認証（いずれか1つ選択）",
                "1": "パスワードのみ",
                "2": "TOTPのみ",
                "3": "USBドライブのみ",
                "4": "パスワード+TOTP",
                "5": "パスワード+USBドライブ",
                "6": "TOTP+USBドライブ",
                "7": "パスワード+TOTP+USBドライブ",
            },
        },
        "security_operations": {
            "name": "セキュリティ操作",
            "description": "セキュリティ認証が必要な操作を設定",
        },
        "safety_switch": {
            "name": "セキュリティスイッチ",
            "description": "有効にすると、すべてのセキュリティ操作にパスワード認証が必要",
            "switchbutton_name": {"enable": "", "disable": ""},
        },
        "set_password": {
            "name": "パスワードを設定/変更",
            "description": "セキュリティ認証パスワードを設定または変更",
        },
        "password_rules": {
            "name": "パスワード要件",
            "description": "長さ≥8、かつ文字、数字、特殊文字のうち少なくとも2種類を含む（3種類推奨）",
        },
        "current_password": {"name": "現在のパスワード"},
        "password_input_placeholder": {"name": "パスワードを入力して認証"},
        "new_password": {"name": "新しいパスワード"},
        "confirm_password": {"name": "新しいパスワードを確認"},
        "password_strength_title": {"name": "パスワード強度"},
        "strength_weak": {"name": "弱"},
        "strength_medium": {"name": "中"},
        "strength_strong": {"name": "強"},
        "save_button": {"name": "保存"},
        "cancel_button": {"name": "キャンセル"},
        "error_current_password": {"name": "現在のパスワードが正しくありません"},
        "error_mismatch": {"name": "新しいパスワードと確認が一致しません"},
        "error_strength_insufficient": {"name": "パスワード強度が不足しています"},
        "success_updated": {"name": "パスワードを更新しました"},
        "remove_password": {
            "name": "パスワードを削除",
            "description": "現在のセキュリティ認証パスワードをキャンセル",
        },
        "remove_password_confirm_title": {"name": "パスワード削除の確認"},
        "remove_password_confirm_content": {
            "name": "パスワードを削除するとセキュリティスイッチが無効になります。続行しますか？"
        },
        "remove_password_success": {
            "name": "パスワードを削除し、セキュリティスイッチを閉じました"
        },
        "error_title": {"name": "エラー"},
        "dialog_yes_text": {"name": "確定"},
        "dialog_cancel_text": {"name": "キャンセル"},
        "totp_switch": {
            "name": "TOTP認証",
            "description": "有効にすると、セキュリティ操作でTOTP動的パスワードを使用可能",
            "switchbutton_name": {"enable": "", "disable": ""},
        },
        "set_totp": {
            "name": "TOTPを設定",
            "description": "TOTPワンタイムパスワード認証を設定",
        },
        "generate_totp_secret": {"name": "秘密鍵を生成"},
        "verify_totp_code": {"name": "認証コードを検証"},
        "totp_input_placeholder": {"name": "TOTP認証コードを入力して検証"},
        "totp_secret_prefix": {"name": "秘密鍵"},
        "totp_uri_prefix": {"name": "URI"},
        "totp_generated_saved": {"name": "TOTP秘密鍵を生成して保存しました"},
        "totp_generated_error": {"name": "TOTPの生成に失敗しました"},
        "totp_code_valid": {"name": "認証コードが有効です"},
        "totp_code_invalid": {"name": "認証コードが無効です"},
        "totp_save_success": {"name": "設定を保存しました"},
        "totp_verify_before_save": {"name": "保存前に認証コードを検証してください"},
        "totp_qr_unavailable": {
            "name": "QRコードを表示できません。QRライブラリをインストールしてください"
        },
        "usb_switch": {
            "name": "USBドライブ認証",
            "description": "有効にすると、セキュリティ操作でUSBドライブ認証を使用可能",
            "switchbutton_name": {"enable": "", "disable": ""},
        },
        "bind_usb": {
            "name": "USBドライブをバインド",
            "description": "認証用USBドライブデバイスをバインド",
        },
        "unbind_usb": {
            "name": "USBドライブをアンバインド",
            "description": "USBドライブデバイスのバインドを解除",
        },
        "usb_refresh": {"name": "更新"},
        "usb_bind": {"name": "バインド"},
        "usb_unbind_all": {"name": "すべてアンバインド"},
        "usb_no_removable": {"name": "リムーバブルディスクが検出されません"},
        "usb_bind_success": {"name": "USBドライブをバインドしました"},
        "usb_unbind_all_success": {"name": "すべてのUSBドライブをアンバインドしました"},
        "usb_require_key_file": {"name": ".keyファイル認証が必要です"},
        "totp_secret_generated": {
            "name": "秘密鍵を生成しました。保存前に認証を完了してください"
        },
        "error_set_password_first": {"name": "まずパスワードを設定してください"},
        "error_set_totp_first": {"name": "まずTOTPを設定してください"},
        "error_bind_usb_first": {"name": "まずUSBドライブをバインドしてください"},
        "verify_in_progress": {"name": "認証中、お待ちください"},
        "verify_failed_generic": {
            "name": "認証が通過しませんでした。入力を確認してください"
        },
        "usb_unbind_selected": {"name": "選択をアンバインド"},
        "usb_unbind_selected_success": {
            "name": "選択したUSBドライブをアンバインドしました"
        },
        "usb_select_bound_hint": {"name": "バインド済みデバイスを1つ選択してください"},
        "usb_bound_devices": {"name": "バインド済みデバイス"},
        "usb_status_connected": {"name": "USBドライブが接続されています"},
        "usb_status_disconnected": {"name": "USBドライブが接続されていません"},
        "show_hide_floating_window_switch": {
            "name": "フローティングウィンドウ表示/非表示認証",
            "description": "有効にすると、フローティングウィンドウの表示または非表示時に認証が必要",
            "switchbutton_name": {"enable": "", "disable": ""},
        },
        "restart_switch": {
            "name": "再起動認証",
            "description": "有効にすると、アプリの再起動時に認証が必要",
            "switchbutton_name": {"enable": "", "disable": ""},
        },
        "exit_switch": {
            "name": "終了認証",
            "description": "有効にすると、アプリの終了時に認証が必要",
            "switchbutton_name": {"enable": "", "disable": ""},
        },
        "open_settings_switch": {
            "name": "設定を開く認証",
            "description": "有効にすると、設定ウィンドウを開く時に認証が必要",
            "switchbutton_name": {"enable": "", "disable": ""},
        },
        "preview_settings": {"name": "プレビュー設定"},
        "preview_settings_switch": {
            "name": "プレビュー設定スイッチ",
            "description": "設定認証時にプレビュー設定を許可",
            "switchbutton_name": {"enable": "", "disable": ""},
        },
    },
}
