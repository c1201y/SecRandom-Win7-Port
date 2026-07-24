# 班级名称设置窗口
set_class_name = {
    "ZH_CN": {
        "title": {"name": "班级名称设置", "description": "设置班级名称窗口标题"},
        "description": {
            "name": "在此窗口中，您可以设置班级名称\n每行输入一个班级名称，系统会将其存储到班级名单文件中\n\n请每行只输入一个班级名称，例如：\n高一1班\n高一2班\n高一3班",
            "description": "班级名称设置窗口描述",
        },
        "input_title": {"name": "班级名称列表", "description": "班级名称输入区域标题"},
        "input_placeholder": {
            "name": "请输入班级名称，每行一个班级名称",
            "description": "班级名称输入框占位符",
        },
        "save_button": {"name": "保存", "description": "保存按钮文本"},
        "cancel_button": {"name": "取消", "description": "取消按钮文本"},
        "error_title": {"name": "错误", "description": "错误消息标题"},
        "success_title": {"name": "成功", "description": "成功消息标题"},
        "info_title": {"name": "提示", "description": "信息消息标题"},
        "invalid_names_error": {
            "name": "以下班级名称包含非法字符或为保留字: {names}",
            "description": "班级名称验证失败时的错误提示",
        },
        "duplicate_names_title": {
            "name": "发现重复名称",
            "description": "名称重复对话框标题",
        },
        "duplicate_names_message": {
            "name": "检测到 {count} 个重复的班级名称：\n{names}\n\n请选择返回编辑，或自动将重复项重命名为“_1/_2…”格式。",
            "description": "名称重复对话框内容",
        },
        "duplicate_names_rename_button": {
            "name": "自动重命名",
            "description": "名称重复对话框自动重命名按钮文本",
        },
        "duplicate_names_edit_button": {
            "name": "返回编辑",
            "description": "名称重复对话框返回编辑按钮文本",
        },
        "save_error": {
            "name": "保存班级名称失败",
            "description": "保存班级名称时的错误提示",
        },
        "success_message": {
            "name": "成功创建 {count} 个新班级",
            "description": "成功创建班级时的提示消息",
        },
        "no_new_classes_message": {
            "name": "所有班级名称均已存在，未创建新的班级",
            "description": "没有创建新班级时的提示消息",
        },
        "unsaved_changes_title": {
            "name": "未保存的更改",
            "description": "未保存更改对话框标题",
        },
        "unsaved_changes_message": {
            "name": "您有未保存的更改，确定要关闭窗口吗？",
            "description": "未保存更改对话框内容",
        },
        "discard_button": {"name": "放弃更改", "description": "放弃更改按钮文本"},
        "continue_editing_button": {
            "name": "继续编辑",
            "description": "继续编辑按钮文本",
        },
        "delete_class_title": {"name": "删除班级", "description": "删除班级对话框标题"},
        "delete_class_message": {
            "name": "确定要删除班级 '{class_name}' 吗？此操作将删除该班级的所有学生数据，且不可恢复",
            "description": "删除班级确认对话框内容",
        },
        "delete_class_button": {"name": "删除班级", "description": "删除班级按钮文本"},
        "delete_multiple_classes_title": {
            "name": "删除多个班级",
            "description": "删除多个班级对话框标题",
        },
        "delete_multiple_classes_message": {
            "name": "确定要删除以下 {count} 个班级吗？此操作将删除这些班级的所有学生数据，且不可恢复\n\n{class_names}",
            "description": "删除多个班级确认对话框内容",
        },
        "delete_success_title": {"name": "删除成功", "description": "删除成功通知标题"},
        "delete_success_message": {
            "name": "成功删除 {count} 个班级",
            "description": "删除成功通知内容",
        },
        "delete_cancel_button": {"name": "取消删除", "description": "取消删除按钮文本"},
        "no_deletable_classes": {
            "name": "没有可删除的班级",
            "description": "没有可删除班级时的提示",
        },
        "select_class_to_delete": {
            "name": "请选择要删除的班级",
            "description": "选择删除班级的提示",
        },
        "select_class_dialog_title": {
            "name": "选择要删除的班级",
            "description": "选择删除班级对话框标题",
        },
        "select_class_dialog_message": {
            "name": "请选择要删除的班级：",
            "description": "选择删除班级对话框内容",
        },
        "delete_selected_button": {
            "name": "删除选中",
            "description": "删除选中按钮文本",
        },
        "delete_class_error": {
            "name": "删除班级失败: {error}",
            "description": "删除班级失败错误信息",
        },
        "class_disappeared_title": {
            "name": "班级消失提示",
            "description": "班级消失提示标题",
        },
        "class_disappeared_message": {
            "name": "检测到班级 '{class_name}' 已从输入框中移除，请保存更改以永久删除",
            "description": "单个班级消失提示内容",
        },
        "multiple_classes_disappeared_message": {
            "name": "检测到以下 {count} 个班级已从输入框中移除，请保存更改以永久删除：\n{class_names}",
            "description": "多个班级消失提示内容",
        },
    },
    "EN_US": {
        "title": {
            "name": "Class name settings",
            "description": "Set the title of the class name window",
        },
        "description": {
            "name": "In this window, you can set up the class name\nto enter a class name per line, and the system will store it in\n\nto enter only one class name per line, e.g.:\nClass 1, Senior 1\nClass 2, Senior 1\nClass 3, Senior 1",
            "description": "Class name settings window description",
        },
        "input_title": {
            "name": "Class name list",
            "description": "Class name enter area title",
        },
        "input_placeholder": {
            "name": "Please input class names here, one class name per line",
            "description": "Class name input placeholder",
        },
        "save_button": {"name": "Save", "description": "Button text of Save"},
        "cancel_button": {"name": "Cancel", "description": "Button text of Cancel"},
        "error_title": {"name": "Error", "description": "Message title of Error"},
        "success_title": {"name": "Success", "description": "Message title of Success"},
        "info_title": {"name": "Prompt", "description": "Message title of Info"},
        "no_class_names_error": {
            "name": "Please enter at least one class name",
            "description": "Incorrect reminder when the class name is not entered",
        },
        "invalid_names_error": {
            "name": "The following class names include invalid characters or reserved words: {names}",
            "description": "Error hint when pool validation failed",
        },
        "duplicate_names_title": {
            "name": "Duplicate names found",
            "description": "Dialog title when duplicate names are detected",
        },
        "duplicate_names_message": {
            "name": "Detected {count} duplicate class names:\n{names}\n\nChoose to go back and edit, or automatically rename duplicates with “_1/_2…” suffix.",
            "description": "Dialog content when duplicate names are detected",
        },
        "duplicate_names_rename_button": {
            "name": "Auto rename",
            "description": "Auto rename button text for duplicate names dialog",
        },
        "duplicate_names_edit_button": {
            "name": "Back to edit",
            "description": "Back to edit button text for duplicate names dialog",
        },
        "save_error": {
            "name": "Failed to save class name",
            "description": "Incorrect reminder when the class name is saving",
        },
        "success_message": {
            "name": "Succeed creating {count} classes",
            "description": "Message show when the classes saved successfully",
        },
        "no_new_classes_message": {
            "name": "All class names already exist, no new class names have been created",
            "description": "Notification message when no new class is created",
        },
        "unsaved_changes_title": {
            "name": "Unsaved changes",
            "description": "Dialog title of change not saved",
        },
        "unsaved_changes_message": {
            "name": "You have unsaved changes. Are you sure you want to close the window?",
            "description": "Dialog content of change not saved",
        },
        "discard_button": {
            "name": "Discard changes",
            "description": "Discard change button text",
        },
        "continue_editing_button": {
            "name": "Keep editing",
            "description": "Continue editing button text",
        },
        "delete_class_title": {
            "name": "Delete class",
            "description": "Delete class dialog title",
        },
        "delete_class_message": {
            "name": "Are you sure to delete the class '{class_name}'? This will delete all student data of this class and can NOT be restored",
            "description": "Delete class dialog message",
        },
        "delete_class_button": {
            "name": "Delete class",
            "description": "Delete class button text",
        },
        "delete_multiple_classes_title": {
            "name": "Delete multiple classes",
            "description": "Delete multiple class dialog title",
        },
        "delete_multiple_classes_message": {
            "name": "Are you sure to delete the following {count} classes? This will delete all student data of these classes and can NOT be restored\n\n{class_names}",
            "description": "Delete multiple class dialog message",
        },
        "delete_success_title": {
            "name": "Delete success",
            "description": "Delete success notification title",
        },
        "delete_success_message": {
            "name": "Succeed deleting {count} classes",
            "description": "Delete success notification content",
        },
        "delete_cancel_button": {
            "name": "Cancel delete",
            "description": "Button text of cancel delete",
        },
        "no_deletable_classes": {
            "name": "No class to delete",
            "description": "Tips when no class can be deleted",
        },
        "select_class_to_delete": {
            "name": "Please select the class to delete",
            "description": "Hint to select the class to delete",
        },
        "select_class_dialog_title": {
            "name": "Select class to delete",
            "description": "Dialog title of tips to choose classes to be deleted",
        },
        "select_class_dialog_message": {
            "name": "Please select the class to delete:",
            "description": "Dialog content of tips to choose classes to be deleted",
        },
        "delete_selected_button": {
            "name": "Delete selected",
            "description": "Delete selected button text",
        },
        "delete_class_error": {
            "name": "Failed to delete class: {error}",
            "description": "Failed to delete class error",
        },
        "class_disappeared_title": {
            "name": "Class disappeared",
            "description": "Class missing hint title",
        },
        "class_disappeared_message": {
            "name": "Detected that the class '{class_name}' have been removed from the input box. Please save your changes to permanently delete it",
            "description": "Class disappear tips",
        },
        "multiple_classes_disappeared_message": {
            "name": "Detected that following {count} classes have been removed from input box. Please save your changes to permanently delete them:\n{class_names}",
            "description": "Multiple classes disappear tips",
        },
    },
    "JA_JP": {
        "title": {
            "name": "クラス名設定",
            "description": "クラス名ウィンドウのタイトルを設定",
        },
        "description": {
            "name": "このウィンドウでクラス名を設定できます\n1行に1つのクラス名を入力すると、システムはクラス名簿ファイルに保存します\n\n1行に1つのクラス名のみを入力してください。例：\n1年1組\n1年2組\n1年3組",
            "description": "クラス名設定ウィンドウの説明",
        },
        "input_title": {
            "name": "クラス名リスト",
            "description": "クラス名入力エリアのタイトル",
        },
        "input_placeholder": {
            "name": "クラス名を入力してください、1行に1つのクラス名",
            "description": "クラス名入力ボックスのプレースホルダー",
        },
        "save_button": {"name": "保存", "description": "保存ボタンのテキスト"},
        "cancel_button": {
            "name": "キャンセル",
            "description": "キャンセルボタンのテキスト",
        },
        "error_title": {"name": "エラー", "description": "エラーメッセージのタイトル"},
        "success_title": {"name": "成功", "description": "成功メッセージのタイトル"},
        "info_title": {"name": "プロンプト", "description": "情報メッセージのタイトル"},
        "invalid_names_error": {
            "name": "以下のクラス名に不正な文字または予約語が含まれています: {names}",
            "description": "クラス名検証失敗時のエラーヒント",
        },
        "duplicate_names_title": {
            "name": "重複名が見つかりました",
            "description": "重複名検出ダイアログのタイトル",
        },
        "duplicate_names_message": {
            "name": "{count}個の重複したクラス名が検出されました：\n{names}\n\n編集に戻るか、重複項目を“_1/_2…”の形式で自動リネームしてください。",
            "description": "重複名検出ダイアログの内容",
        },
        "duplicate_names_rename_button": {
            "name": "自動リネーム",
            "description": "重複名検出ダイアログの自動リネームボタン",
        },
        "duplicate_names_edit_button": {
            "name": "編集に戻る",
            "description": "重複名検出ダイアログの編集に戻るボタン",
        },
        "save_error": {
            "name": "クラス名の保存に失敗しました",
            "description": "クラス名保存時のエラーヒント",
        },
        "success_message": {
            "name": "{count}個の新しいクラスを作成しました",
            "description": "クラス作成成功時のプロンプトメッセージ",
        },
        "no_new_classes_message": {
            "name": "すべてのクラス名が既に存在するため、新しいクラスは作成されませんでした",
            "description": "新しいクラスが作成されなかった場合のプロンプトメッセージ",
        },
        "unsaved_changes_title": {
            "name": "未保存の変更",
            "description": "未保存変更ダイアログのタイトル",
        },
        "unsaved_changes_message": {
            "name": "未保存の変更があります。ウィンドウを閉じますか？",
            "description": "未保存変更ダイアログの内容",
        },
        "discard_button": {
            "name": "変更を破棄",
            "description": "変更を破棄ボタンのテキスト",
        },
        "continue_editing_button": {
            "name": "編集を続ける",
            "description": "編集を続けるボタンのテキスト",
        },
        "delete_class_title": {
            "name": "クラスを削除",
            "description": "クラス削除ダイアログのタイトル",
        },
        "delete_class_message": {
            "name": "クラス '{class_name}' を削除しますか？この操作はこのクラスのすべての学生データを削除し、復元できません",
            "description": "クラス削除確認ダイアログの内容",
        },
        "delete_class_button": {
            "name": "クラスを削除",
            "description": "クラス削除ボタンのテキスト",
        },
        "delete_multiple_classes_title": {
            "name": "複数のクラスを削除",
            "description": "複数のクラス削除ダイアログのタイトル",
        },
        "delete_multiple_classes_message": {
            "name": "以下の{count}個のクラスを削除しますか？この操作はこれらのクラスのすべての学生データを削除し、復元できません\n\n{class_names}",
            "description": "複数のクラス削除確認ダイアログの内容",
        },
        "delete_success_title": {
            "name": "削除成功",
            "description": "削除成功通知のタイトル",
        },
        "delete_success_message": {
            "name": "{count}個のクラスを削除しました",
            "description": "削除成功通知の内容",
        },
        "delete_cancel_button": {
            "name": "削除をキャンセル",
            "description": "削除キャンセルボタンのテキスト",
        },
        "no_deletable_classes": {
            "name": "削除可能なクラスがありません",
            "description": "削除可能なクラスがない場合のヒント",
        },
        "select_class_to_delete": {
            "name": "削除するクラスを選択してください",
            "description": "削除クラス選択のヒント",
        },
        "select_class_dialog_title": {
            "name": "削除するクラスを選択",
            "description": "削除クラス選択ダイアログのタイトル",
        },
        "select_class_dialog_message": {
            "name": "削除するクラスを選択してください：",
            "description": "削除クラス選択ダイアログの内容",
        },
        "delete_selected_button": {
            "name": "選択を削除",
            "description": "選択削除ボタンのテキスト",
        },
        "delete_class_error": {
            "name": "クラスの削除に失敗しました: {error}",
            "description": "クラス削除失敗エラー情報",
        },
        "class_disappeared_title": {
            "name": "クラス消失ヒント",
            "description": "クラス消失ヒントのタイトル",
        },
        "class_disappeared_message": {
            "name": "クラス '{class_name}' が入力ボックスから削除されたことが検出されました。変更を保存して永久に削除してください",
            "description": "単一クラス消失ヒントの内容",
        },
        "multiple_classes_disappeared_message": {
            "name": "以下の{count}個のクラスが入力ボックスから削除されたことが検出されました。変更を保存して永久に削除してください：\n{class_names}",
            "description": "複数クラス消失ヒントの内容",
        },
    },
}

# 导入学生姓名语言配置
import_student_name = {
    "ZH_CN": {
        "title": {
            "name": "导入学生姓名",
            "description": "从Excel或CSV文件导入学生姓名",
        },
        "initial_subtitle": {
            "name": "正在导入到：",
            "description": "正在导入到班级的提示",
        },
        "file_selection_title": {"name": "文件选择", "description": "文件选择区域标题"},
        "no_file_selected": {
            "name": "未选择文件",
            "description": "未选择文件时的提示文本",
        },
        "select_file": {"name": "选择文件", "description": "选择文件按钮文本"},
        "supported_formats": {
            "name": "支持的格式: Excel (.xlsx, .xls) 和 CSV (.csv)",
            "description": "支持的文件格式说明",
        },
        "file_filter": {
            "name": "Excel 文件 (*.xlsx *.xls);;CSV 文件 (*.csv)",
            "description": "文件选择对话框的文件过滤器",
        },
        "dialog_title": {"name": "选择文件", "description": "文件选择对话框标题"},
        "column_mapping_title": {"name": "列映射", "description": "列映射区域标题"},
        "column_mapping_description": {
            "name": "请选择包含学生信息的列",
            "description": "列映射区域说明",
        },
        "column_mapping_id_column": {
            "name": "学号列 (必选):",
            "description": "学号列标签",
        },
        "column_mapping_name_column": {
            "name": "姓名列 (必选):",
            "description": "姓名列标签",
        },
        "column_mapping_gender_column": {
            "name": "性别列 (可选):",
            "description": "性别列标签",
        },
        "column_mapping_group_column": {
            "name": "小组列 (可选):",
            "description": "小组列标签",
        },
        "column_mapping_tags_column": {
            "name": "标签列 (可选):",
            "description": "标签列标签",
        },
        "column_mapping_none": {"name": "无", "description": "无选项文本"},
        "data_preview_title": {"name": "数据预览", "description": "数据预览区域标题"},
        "student_id": {"name": "学号", "description": "学号列标题"},
        "name": {"name": "姓名", "description": "姓名列标题"},
        "gender": {"name": "性别", "description": "性别列标题"},
        "group": {"name": "小组", "description": "小组列标题"},
        "tags": {"name": "标签", "description": "标签列标题"},
        "buttons_import": {"name": "导入", "description": "导入按钮文本"},
        "file_loaded_title": {
            "name": "文件已加载",
            "description": "文件加载成功对话框标题",
        },
        "file_loaded_content": {
            "name": "文件加载成功",
            "description": "文件加载成功对话框内容",
        },
        "file_loaded_notification_title": {
            "name": "文件加载成功",
            "description": "文件加载成功通知标题",
        },
        "file_loaded_notification_content": {
            "name": "文件已成功加载，请检查数据预览",
            "description": "文件加载成功通知内容",
        },
        "error_title": {"name": "错误", "description": "错误对话框标题"},
        "load_failed": {"name": "加载文件失败", "description": "加载文件失败错误信息"},
        "load_failed_notification_title": {
            "name": "加载文件失败",
            "description": "加载文件失败通知标题",
        },
        "load_failed_notification_content": {
            "name": "无法加载文件，请检查文件格式和内容",
            "description": "加载文件失败通知内容",
        },
        "import_failed": {
            "name": "导入数据失败",
            "description": "导入数据失败错误信息",
        },
        "import_failed_notification_title": {
            "name": "导入数据失败",
            "description": "导入数据失败通知标题",
        },
        "import_failed_notification_content": {
            "name": "导入数据时发生错误，请检查数据格式和内容",
            "description": "导入数据失败通知内容",
        },
        "unsupported_format": {
            "name": "不支持的文件格式",
            "description": "不支持的文件格式错误信息",
        },
        "no_name_column": {
            "name": "请选择姓名列",
            "description": "未选择姓名列错误信息",
        },
        "no_id_column": {"name": "请选择学号列", "description": "未选择学号列错误信息"},
        "duplicate_names_title": {
            "name": "发现重复名称",
            "description": "导入时名称重复对话框标题",
        },
        "duplicate_names_message": {
            "name": "检测到 {count} 个重复的姓名：\n{names}\n\n请选择返回编辑，或自动将重复项重命名为“_1/_2…”格式。",
            "description": "导入时名称重复对话框内容",
        },
        "duplicate_names_rename_button": {
            "name": "自动重命名",
            "description": "导入时名称重复对话框自动重命名按钮文本",
        },
        "duplicate_names_edit_button": {
            "name": "返回编辑",
            "description": "导入时名称重复对话框返回编辑按钮文本",
        },
        "import_success_title": {
            "name": "导入成功",
            "description": "导入成功对话框标题",
        },
        "import_success_content_template": {
            "name": "成功导入 {count} 个学生信息到班级 '{class_name}'",
            "description": "导入成功对话框内容模板",
        },
        "import_success_notification_title": {
            "name": "导入成功",
            "description": "导入成功通知标题",
        },
        "import_success_notification_content_template": {
            "name": "成功导入 {count} 个学生信息到班级 '{class_name}'",
            "description": "导入成功通知内容模板",
        },
        "existing_data_title": {
            "name": "班级已有数据",
            "description": "班级已有数据对话框标题",
        },
        "existing_data_prompt": {
            "name": "班级 '{class_name}' 已包含 {count} 名学生，请选择处理方式:",
            "description": "班级已有数据对话框提示文本",
        },
        "existing_data_option_overwrite": {
            "name": "覆盖现有数据",
            "description": "覆盖现有数据选项",
        },
        "existing_data_option_cancel": {
            "name": "取消导入",
            "description": "取消导入选项",
        },
    },
    "EN_US": {
        "title": {
            "name": "Import student names",
            "description": "Import student names from Excel or CSV file",
        },
        "initial_subtitle": {
            "name": "Importing to:",
            "description": "Importing to class tips",
        },
        "file_selection_title": {
            "name": "File select",
            "description": "File selection area title",
        },
        "no_file_selected": {
            "name": "No file selected",
            "description": "Didn't select ant file hint text",
        },
        "select_file": {
            "name": "File select",
            "description": "Select file button text",
        },
        "supported_formats": {
            "name": "Supported formats: Excel (.xlsx, .xls) and CSV (.csv)",
            "description": "Supported file format description",
        },
        "file_filter": {
            "name": "Excel files (*.xlsx *.xls);;CSV files (*.csv)",
            "description": "File filter in the file selection dialog",
        },
        "dialog_title": {
            "name": "File select",
            "description": "File selection dialog title",
        },
        "column_mapping_title": {
            "name": "Column mapping",
            "description": "Column map area title",
        },
        "column_mapping_description": {
            "name": "Please select a column containing the student information",
            "description": "Column map area description",
        },
        "column_mapping_id_column": {
            "name": "Student ID column (required):",
            "description": "Column label of Student ID",
        },
        "column_mapping_name_column": {
            "name": "Name column (required):",
            "description": "Column label of name",
        },
        "column_mapping_gender_column": {
            "name": "Gender column (optional):",
            "description": "Column label of gender",
        },
        "column_mapping_group_column": {
            "name": "Group column (optional):",
            "description": "Column label of group",
        },
        "column_mapping_tags_column": {
            "name": "Tags column (optional):",
            "description": "Column label of tags",
        },
        "column_mapping_none": {"name": "Noneh", "description": "Text of None"},
        "data_preview_title": {
            "name": "Data preview",
            "description": "Preview area title",
        },
        "student_id": {
            "name": "Student ID",
            "description": "Column title of Student ID",
        },
        "name": {"name": "Name", "description": "Column title of Name"},
        "gender": {"name": "Gender", "description": "Column title of Gender"},
        "group": {"name": "Group", "description": "Column title of Group"},
        "tags": {"name": "Tags", "description": "Column title of Tags"},
        "buttons_import": {"name": "Import", "description": "Button text of Import"},
        "file_loaded_title": {
            "name": "File loaded",
            "description": "File load success dialog title",
        },
        "file_loaded_content": {
            "name": "Files loaded successfully",
            "description": "File load success dialog content",
        },
        "file_loaded_notification_title": {
            "name": "Files loaded successfully",
            "description": "File load success notification title",
        },
        "file_loaded_notification_content": {
            "name": "File loaded successfully, please check data preview",
            "description": "File load success notification content",
        },
        "error_title": {"name": "Error", "description": "Dialog title of Error"},
        "load_failed": {
            "name": "Failed to load files",
            "description": "Failed to load files error",
        },
        "load_failed_notification_title": {
            "name": "Failed to load files",
            "description": "Filed to load files notification title",
        },
        "load_failed_notification_content": {
            "name": "Unable to load files, please check file format and content",
            "description": "Failed to load files notification content",
        },
        "import_failed": {
            "name": "Failed to import data",
            "description": "Failed to import data name error",
        },
        "import_failed_notification_title": {
            "name": "Failed to import data",
            "description": "Filed to load data notification title",
        },
        "import_failed_notification_content": {
            "name": "Error importing data, please check data format and content",
            "description": "Failed to load data notification content",
        },
        "unsupported_format": {
            "name": "Unsupported file format",
            "description": "Unsupported file format error",
        },
        "no_name_column": {
            "name": "Please select the name column",
            "description": "Error: No name column selected",
        },
        "no_id_column": {
            "name": "Please select the Student ID column",
            "description": "Error: No Student ID column selected",
        },
        "duplicate_names_title": {
            "name": "Duplicate names found",
            "description": "Dialog title when duplicate names are detected during import",
        },
        "duplicate_names_message": {
            "name": "Detected {count} duplicate names:\n{names}\n\nChoose to go back and edit, or automatically rename duplicates with “_1/_2…” suffix.",
            "description": "Dialog content when duplicate names are detected during import",
        },
        "duplicate_names_rename_button": {
            "name": "Auto rename",
            "description": "Auto rename button text for duplicate names dialog during import",
        },
        "duplicate_names_edit_button": {
            "name": "Back to edit",
            "description": "Back to edit button text for duplicate names dialog during import",
        },
        "import_success_title": {
            "name": "Import success",
            "description": "Import success dialog title",
        },
        "import_success_content_template": {
            "name": "Succeed importing {count} students to class '{class_name}'",
            "description": "Import success dialog content template",
        },
        "import_success_notification_title": {
            "name": "Import success",
            "description": "Import successful notification title",
        },
        "import_success_notification_content_template": {
            "name": "Succeed importing {count} students to class '{class_name}'",
            "description": "Import success notification content template",
        },
        "existing_data_title": {
            "name": "Class data already available",
            "description": "Class data already available dialog title",
        },
        "existing_data_prompt": {
            "name": "Pool '{class_name}' has already contained {count} students, please select handling method:",
            "description": "Class data already available dialog tip text",
        },
        "existing_data_option_overwrite": {
            "name": "Overwrite existing data",
            "description": "Overwrite existing data option",
        },
        "existing_data_option_cancel": {
            "name": "Cancel import",
            "description": "Option of Cancel import",
        },
    },
    "JA_JP": {
        "title": {
            "name": "学生氏名をインポート",
            "description": "ExcelまたはCSVファイルから学生氏名をインポート",
        },
        "initial_subtitle": {
            "name": "インポート先：",
            "description": "クラスにインポート中のプロンプト",
        },
        "file_selection_title": {
            "name": "ファイル選択",
            "description": "ファイル選択エリアのタイトル",
        },
        "no_file_selected": {
            "name": "ファイルが選択されていません",
            "description": "ファイルが選択されていない場合のプロンプトテキスト",
        },
        "select_file": {
            "name": "ファイルを選択",
            "description": "ファイル選択ボタンのテキスト",
        },
        "supported_formats": {
            "name": "サポートする形式: Excel (.xlsx, .xls) と CSV (.csv)",
            "description": "サポートするファイル形式の説明",
        },
        "file_filter": {
            "name": "Excelファイル (*.xlsx *.xls);;CSVファイル (*.csv)",
            "description": "ファイル選択ダイアログのファイルフィルター",
        },
        "dialog_title": {
            "name": "ファイルを選択",
            "description": "ファイル選択ダイアログのタイトル",
        },
        "column_mapping_title": {
            "name": "列マッピング",
            "description": "列マッピングエリアのタイトル",
        },
        "column_mapping_description": {
            "name": "学生情報を含む列を選択してください",
            "description": "列マッピングエリアの説明",
        },
        "column_mapping_id_column": {
            "name": "学籍番号列（必須）:",
            "description": "学籍番号列ラベル",
        },
        "column_mapping_name_column": {
            "name": "氏名列（必須）:",
            "description": "氏名列ラベル",
        },
        "column_mapping_gender_column": {
            "name": "性別列（オプション）:",
            "description": "性別列ラベル",
        },
        "column_mapping_group_column": {
            "name": "グループ列（オプション）:",
            "description": "グループ列ラベル",
        },
        "column_mapping_tags_column": {
            "name": "タグ列（オプション）:",
            "description": "タグ列ラベル",
        },
        "column_mapping_none": {
            "name": "なし",
            "description": "なしオプションのテキスト",
        },
        "data_preview_title": {
            "name": "データプレビュー",
            "description": "データプレビューエリアのタイトル",
        },
        "student_id": {
            "name": "学籍番号",
            "description": "学籍番号列タイトル",
        },
        "name": {
            "name": "氏名",
            "description": "氏名列タイトル",
        },
        "gender": {
            "name": "性別",
            "description": "性別列タイトル",
        },
        "group": {
            "name": "グループ",
            "description": "グループ列タイトル",
        },
        "tags": {"name": "タグ", "description": "タグ列タイトル"},
        "buttons_import": {
            "name": "インポート",
            "description": "インポートボタンのテキスト",
        },
        "file_loaded_title": {
            "name": "ファイルがロードされました",
            "description": "ファイルロード成功ダイアログのタイトル",
        },
        "file_loaded_content": {
            "name": "ファイルが正常にロードされました",
            "description": "ファイルロード成功ダイアログの内容",
        },
        "file_loaded_notification_title": {
            "name": "ファイルが正常にロードされました",
            "description": "ファイルロード成功通知のタイトル",
        },
        "file_loaded_notification_content": {
            "name": "ファイルが正常にロードされました、データプレビューを確認してください",
            "description": "ファイルロード成功通知の内容",
        },
        "error_title": {
            "name": "エラー",
            "description": "エラーダイアログのタイトル",
        },
        "load_failed": {
            "name": "ファイルのロードに失敗しました",
            "description": "ファイルロード失敗エラー情報",
        },
        "load_failed_notification_title": {
            "name": "ファイルのロードに失敗しました",
            "description": "ファイルロード失敗通知のタイトル",
        },
        "load_failed_notification_content": {
            "name": "ファイルをロードできません、ファイル形式と内容を確認してください",
            "description": "ファイルロード失敗通知の内容",
        },
        "import_failed": {
            "name": "データのインポートに失敗しました",
            "description": "データインポート失敗エラー情報",
        },
        "import_failed_notification_title": {
            "name": "データのインポートに失敗しました",
            "description": "データインポート失敗通知のタイトル",
        },
        "import_failed_notification_content": {
            "name": "データのインポートエラー、データ形式と内容を確認してください",
            "description": "データインポート失敗通知の内容",
        },
        "unsupported_format": {
            "name": "サポートされていないファイル形式",
            "description": "サポートされていないファイル形式エラー情報",
        },
        "no_name_column": {
            "name": "氏名列を選択してください",
            "description": "氏名列が選択されていないエラー情報",
        },
        "no_id_column": {
            "name": "学籍番号列を選択してください",
            "description": "学籍番号列が選択されていないエラー情報",
        },
        "duplicate_names_title": {
            "name": "重複名が見つかりました",
            "description": "インポート時の重複名検出ダイアログのタイトル",
        },
        "duplicate_names_message": {
            "name": "{count}個の重複した氏名が検出されました：\n{names}\n\n編集に戻るか、重複項目を“_1/_2…”の形式で自動リネームしてください。",
            "description": "インポート時の重複名検出ダイアログの内容",
        },
        "duplicate_names_rename_button": {
            "name": "自動リネーム",
            "description": "インポート時の重複名検出ダイアログの自動リネームボタン",
        },
        "duplicate_names_edit_button": {
            "name": "編集に戻る",
            "description": "インポート時の重複名検出ダイアログの編集に戻るボタン",
        },
        "import_success_title": {
            "name": "インポート成功",
            "description": "インポート成功ダイアログのタイトル",
        },
        "import_success_content_template": {
            "name": "{count}人の学生情報をクラス '{class_name}' にインポートしました",
            "description": "インポート成功ダイアログの内容テンプレート",
        },
        "import_success_notification_title": {
            "name": "インポート成功",
            "description": "インポート成功通知のタイトル",
        },
        "import_success_notification_content_template": {
            "name": "{count}人の学生情報をクラス '{class_name}' にインポートしました",
            "description": "インポート成功通知の内容テンプレート",
        },
        "existing_data_title": {
            "name": "クラスに既にデータが存在します",
            "description": "クラスに既にデータが存在するダイアログのタイトル",
        },
        "existing_data_prompt": {
            "name": "クラス '{class_name}' は既に{count}人の学生を含んでいます、処理方法を選択してください：",
            "description": "クラスに既にデータが存在するダイアログのヒントテキスト",
        },
        "existing_data_option_overwrite": {
            "name": "既存のデータを上書き",
            "description": "既存のデータを上書きオプション",
        },
        "existing_data_option_cancel": {
            "name": "インポートをキャンセル",
            "description": "インポートキャンセルオプション",
        },
    },
}

# 姓名设置窗口
name_setting = {
    "ZH_CN": {
        "title": {"name": "姓名设置", "description": "设置姓名窗口标题"},
        "description": {
            "name": "在此窗口中，您可以设置学生姓名\n每行输入一个学生姓名，系统会将其存储到班级名单文件中\n\n请每行只输入一个姓名，例如：\n张三\n李四\n王五",
            "description": "姓名设置窗口描述",
        },
        "input_title": {"name": "姓名列表", "description": "姓名输入区域标题"},
        "input_placeholder": {
            "name": "请输入姓名，每行一个姓名",
            "description": "姓名输入框占位符",
        },
        "save_button": {"name": "保存", "description": "保存按钮文本"},
        "cancel_button": {"name": "取消", "description": "取消按钮文本"},
        "error_title": {"name": "错误", "description": "错误消息标题"},
        "success_title": {"name": "成功", "description": "成功消息标题"},
        "info_title": {"name": "提示", "description": "信息消息标题"},
        "no_names_error": {
            "name": "请至少输入一个姓名",
            "description": "未输入姓名时的错误提示",
        },
        "invalid_names_error": {
            "name": "以下姓名包含非法字符或为保留字: {names}",
            "description": "姓名验证失败时的错误提示",
        },
        "duplicate_names_title": {
            "name": "发现重复名称",
            "description": "名称重复对话框标题",
        },
        "duplicate_names_message": {
            "name": "检测到 {count} 个重复的姓名：\n{names}\n\n请选择返回编辑，或自动将重复项重命名为“_1/_2…”格式。",
            "description": "名称重复对话框内容",
        },
        "duplicate_names_rename_button": {
            "name": "自动重命名",
            "description": "名称重复对话框自动重命名按钮文本",
        },
        "duplicate_names_edit_button": {
            "name": "返回编辑",
            "description": "名称重复对话框返回编辑按钮文本",
        },
        "save_error": {"name": "保存姓名失败", "description": "保存姓名时的错误提示"},
        "success_message": {
            "name": "成功创建 {count} 个新姓名",
            "description": "成功创建姓名时的提示消息",
        },
        "no_new_names_message": {
            "name": "所有姓名均已存在，未创建新的姓名",
            "description": "没有创建新姓名时的提示消息",
        },
        "unsaved_changes_title": {
            "name": "未保存的更改",
            "description": "未保存更改对话框标题",
        },
        "unsaved_changes_message": {
            "name": "您有未保存的更改，确定要关闭窗口吗？",
            "description": "未保存更改对话框内容",
        },
        "discard_button": {"name": "放弃更改", "description": "放弃更改按钮文本"},
        "continue_editing_button": {
            "name": "继续编辑",
            "description": "继续编辑按钮文本",
        },
        "delete_button": {"name": "删除", "description": "删除按钮文本"},
        "delete_name_title": {"name": "删除姓名", "description": "删除姓名对话框标题"},
        "delete_name_message": {
            "name": "确定要删除姓名 '{name}' 吗？此操作将删除该姓名的所有信息，且不可恢复",
            "description": "删除姓名确认对话框内容",
        },
        "delete_multiple_names_title": {
            "name": "删除多个姓名",
            "description": "删除多个姓名对话框标题",
        },
        "delete_multiple_names_message": {
            "name": "确定要删除以下 {count} 个姓名吗？此操作将删除这些姓名的所有信息，且不可恢复\n\n{names}",
            "description": "删除多个姓名确认对话框内容",
        },
        "delete_name_success_title": {
            "name": "删除成功",
            "description": "删除姓名成功通知标题",
        },
        "delete_name_success_message": {
            "name": "成功删除 {count} 个姓名",
            "description": "删除姓名成功通知内容",
        },
        "delete_name_cancel_button": {
            "name": "取消删除",
            "description": "取消删除姓名按钮文本",
        },
        "no_deletable_names": {
            "name": "没有可删除的姓名",
            "description": "没有可删除姓名时的提示",
        },
        "select_name_to_delete": {
            "name": "请选择要删除的姓名",
            "description": "选择删除姓名的提示",
        },
        "select_name_dialog_title": {
            "name": "选择要删除的姓名",
            "description": "选择删除姓名对话框标题",
        },
        "select_name_dialog_message": {
            "name": "请选择要删除的姓名：",
            "description": "选择删除姓名对话框内容",
        },
        "delete_selected_names_button": {
            "name": "删除选中",
            "description": "删除选中姓名按钮文本",
        },
        "delete_name_error": {
            "name": "删除姓名失败: {error}",
            "description": "删除姓名失败错误信息",
        },
        "name_deleted_title": {"name": "姓名已删除", "description": "删除姓名提示标题"},
        "name_deleted_message": {
            "name": "姓名 '{name}' 已从输入框中移除，请保存更改以永久删除",
            "description": "删除姓名提示内容",
        },
    },
    "EN_US": {
        "title": {"name": "Name settings", "description": "Set name window title"},
        "description": {
            "name": "In this window, you can set up student names\nto enter a student name per line, and the system will store it in\n\nto enter only one student name per line, e.g.:\nTom\nDick\nHarry",
            "description": "Name settings window description",
        },
        "input_title": {"name": "Name list", "description": "Name input area title"},
        "input_placeholder": {
            "name": "Please input names here, one name per line",
            "description": "Name input box placeholder",
        },
        "save_button": {"name": "Save", "description": "Button text of Save"},
        "cancel_button": {"name": "Cancel", "description": "Button text of Cancel"},
        "error_title": {"name": "Error", "description": "Message title of Error"},
        "success_title": {"name": "Success", "description": "Message title of Success"},
        "info_title": {"name": "Prompt", "description": "Message title of Info"},
        "no_names_error": {
            "name": "Please enter at least one name",
            "description": "Error hint shown on no name is input",
        },
        "invalid_names_error": {
            "name": "The following names include invalid characters or reserved words: {names}",
            "description": "Error hint when name validation failed",
        },
        "duplicate_names_title": {
            "name": "Duplicate names found",
            "description": "Dialog title when duplicate names are detected",
        },
        "duplicate_names_message": {
            "name": "Detected {count} duplicate names:\n{names}\n\nChoose to go back and edit, or automatically rename duplicates with “_1/_2…” suffix.",
            "description": "Dialog content when duplicate names are detected",
        },
        "duplicate_names_rename_button": {
            "name": "Auto rename",
            "description": "Auto rename button text for duplicate names dialog",
        },
        "duplicate_names_edit_button": {
            "name": "Back to edit",
            "description": "Back to edit button text for duplicate names dialog",
        },
        "save_error": {
            "name": "Failed to save names",
            "description": "Error hint when name saved failed",
        },
        "success_message": {
            "name": "Succeed creating {count} names",
            "description": "Message show when the names saved successfully",
        },
        "no_new_names_message": {
            "name": "All names already exist, no new names have been created",
            "description": "Notification message when no new name is created",
        },
        "unsaved_changes_title": {
            "name": "Unsaved changes",
            "description": "Dialog title of change not saved",
        },
        "unsaved_changes_message": {
            "name": "You have unsaved changes. Are you sure you want to close the window?",
            "description": "Dialog content of change not saved",
        },
        "discard_button": {
            "name": "Discard changes",
            "description": "Discard change button text",
        },
        "continue_editing_button": {
            "name": "Keep editing",
            "description": "Continue editing button text",
        },
        "delete_button": {"name": "Delete", "description": "Button text of Delete"},
        "delete_name_title": {
            "name": "Delete name",
            "description": "Delete name dialog title",
        },
        "delete_name_message": {
            "name": "Are you sure to delete the name '{name}'? This will delete all information of this name and can NOT be restored",
            "description": "Delete name dialog message",
        },
        "delete_multiple_names_title": {
            "name": "Delete multiple names",
            "description": "Delete multiple name dialog title",
        },
        "delete_multiple_names_message": {
            "name": "Are you sure to delete the following {count} names? This will delete all information of these names and can NOT be restored\n\n{names}",
            "description": "Delete multiple name dialog message",
        },
        "delete_name_success_title": {
            "name": "Delete success",
            "description": "Delete name success notification title",
        },
        "delete_name_success_message": {
            "name": "Succeed deleting {count} names",
            "description": "Delete name success notification content",
        },
        "delete_name_cancel_button": {
            "name": "Cancel delete",
            "description": "Button text of cancel delete name",
        },
        "no_deletable_names": {
            "name": "No name to delete",
            "description": "Tips when no name can be deleted",
        },
        "select_name_to_delete": {
            "name": "Please select name to delete",
            "description": "Hint to select the name to delete",
        },
        "select_name_dialog_title": {
            "name": "Select names to delete",
            "description": "Dialog title of tips to choose name to be deleted",
        },
        "select_name_dialog_message": {
            "name": "Please select the name to delete:",
            "description": "Dialog content of tips to choose names to be deleted",
        },
        "delete_selected_names_button": {
            "name": "Delete selected",
            "description": "Delete selected names button text",
        },
        "delete_name_error": {
            "name": "Failed to delete name: {error}",
            "description": "Failed to delete name error",
        },
        "name_deleted_title": {
            "name": "Name deleted",
            "description": "Delete name tip title",
        },
        "name_deleted_message": {
            "name": "Detected that the name '{name}' have been removed from the input box. Please save your changes to permanently delete it",
            "description": "Delete name hint",
        },
    },
    "JA_JP": {
        "title": {
            "name": "氏名設定",
            "description": "氏名ウィンドウのタイトルを設定",
        },
        "description": {
            "name": "このウィンドウで学生氏名を設定できます\n1行に1つの学生氏名を入力すると、システムはクラス名簿ファイルに保存します\n\n1行に1つの氏名のみを入力してください。例：\n田中\n鈴木\n山田",
            "description": "氏名設定ウィンドウの説明",
        },
        "input_title": {
            "name": "氏名リスト",
            "description": "氏名入力エリアのタイトル",
        },
        "input_placeholder": {
            "name": "氏名を入力してください、1行に1つの氏名",
            "description": "氏名入力ボックスのプレースホルダー",
        },
        "save_button": {"name": "保存", "description": "保存ボタンのテキスト"},
        "cancel_button": {
            "name": "キャンセル",
            "description": "キャンセルボタンのテキスト",
        },
        "error_title": {"name": "エラー", "description": "エラーメッセージのタイトル"},
        "success_title": {"name": "成功", "description": "成功メッセージのタイトル"},
        "info_title": {"name": "プロンプト", "description": "情報メッセージのタイトル"},
        "no_names_error": {
            "name": "少なくとも1つの氏名を入力してください",
            "description": "氏名が入力されていない場合のエラーヒント",
        },
        "invalid_names_error": {
            "name": "以下の氏名に不正な文字または予約語が含まれています: {names}",
            "description": "氏名検証失敗時のエラーヒント",
        },
        "duplicate_names_title": {
            "name": "重複名が見つかりました",
            "description": "重複名検出ダイアログのタイトル",
        },
        "duplicate_names_message": {
            "name": "{count}個の重複した氏名が検出されました：\n{names}\n\n編集に戻るか、重複項目を“_1/_2…”の形式で自動リネームしてください。",
            "description": "重複名検出ダイアログの内容",
        },
        "duplicate_names_rename_button": {
            "name": "自動リネーム",
            "description": "重複名検出ダイアログの自動リネームボタン",
        },
        "duplicate_names_edit_button": {
            "name": "編集に戻る",
            "description": "重複名検出ダイアログの編集に戻るボタン",
        },
        "save_error": {
            "name": "氏名の保存に失敗しました",
            "description": "氏名保存時のエラーヒント",
        },
        "success_message": {
            "name": "{count}個の新しい氏名を作成しました",
            "description": "氏名作成成功時のプロンプトメッセージ",
        },
        "no_new_names_message": {
            "name": "すべての氏名が既に存在するため、新しい氏名は作成されませんでした",
            "description": "新しい氏名が作成されなかった場合のプロンプトメッセージ",
        },
        "unsaved_changes_title": {
            "name": "未保存の変更",
            "description": "未保存変更ダイアログのタイトル",
        },
        "unsaved_changes_message": {
            "name": "未保存の変更があります。ウィンドウを閉じますか？",
            "description": "未保存変更ダイアログの内容",
        },
        "discard_button": {
            "name": "変更を破棄",
            "description": "変更を破棄ボタンのテキスト",
        },
        "continue_editing_button": {
            "name": "編集を続ける",
            "description": "編集を続けるボタンのテキスト",
        },
        "delete_button": {"name": "削除", "description": "削除ボタンのテキスト"},
        "delete_name_title": {
            "name": "氏名を削除",
            "description": "氏名削除ダイアログのタイトル",
        },
        "delete_name_message": {
            "name": "氏名 '{name}' を削除しますか？この操作はこの氏名のすべての情報を削除し、復元できません",
            "description": "氏名削除確認ダイアログの内容",
        },
        "delete_multiple_names_title": {
            "name": "複数の氏名を削除",
            "description": "複数の氏名削除ダイアログのタイトル",
        },
        "delete_multiple_names_message": {
            "name": "以下の{count}個の氏名を削除しますか？この操作はこれらの氏名のすべての情報を削除し、復元できません\n\n{names}",
            "description": "複数の氏名削除確認ダイアログの内容",
        },
        "delete_name_success_title": {
            "name": "削除成功",
            "description": "氏名削除成功通知のタイトル",
        },
        "delete_name_success_message": {
            "name": "{count}個の氏名を削除しました",
            "description": "氏名削除成功通知の内容",
        },
        "delete_name_cancel_button": {
            "name": "削除をキャンセル",
            "description": "氏名削除キャンセルボタンのテキスト",
        },
        "no_deletable_names": {
            "name": "削除可能な氏名がありません",
            "description": "削除可能な氏名がない場合のヒント",
        },
        "select_name_to_delete": {
            "name": "削除する氏名を選択してください",
            "description": "削除氏名選択のヒント",
        },
        "select_name_dialog_title": {
            "name": "削除する氏名を選択",
            "description": "削除氏名選択ダイアログのタイトル",
        },
        "select_name_dialog_message": {
            "name": "削除する氏名を選択してください：",
            "description": "削除氏名選択ダイアログの内容",
        },
        "delete_selected_names_button": {
            "name": "選択を削除",
            "description": "選択削除ボタンのテキスト",
        },
        "delete_name_error": {
            "name": "氏名の削除に失敗しました: {error}",
            "description": "氏名削除失敗エラー情報",
        },
        "name_deleted_title": {
            "name": "氏名が削除されました",
            "description": "氏名削除ヒントのタイトル",
        },
        "name_deleted_message": {
            "name": "氏名 '{name}' が入力ボックスから削除されたことが検出されました。変更を保存して永久に削除してください",
            "description": "氏名削除ヒントの内容",
        },
    },
}

# 性别设置窗口
gender_setting = {
    "ZH_CN": {
        "title": {"name": "性别设置", "description": "设置性别窗口标题"},
        "description": {
            "name": "在此窗口中，您可以设置学生性别\n每行输入一个性别，系统会将其存储到班级名单文件中\n\n请每行只输入一个性别，例如：\n男\n女\n其他",
            "description": "性别设置窗口描述",
        },
        "input_title": {"name": "性别列表", "description": "性别输入区域标题"},
        "input_placeholder": {
            "name": "请输入性别，每行一个性别",
            "description": "性别输入框占位符",
        },
        "save_button": {"name": "保存", "description": "保存按钮文本"},
        "cancel_button": {"name": "取消", "description": "取消按钮文本"},
        "error_title": {"name": "错误", "description": "错误消息标题"},
        "success_title": {"name": "成功", "description": "成功消息标题"},
        "info_title": {"name": "提示", "description": "信息消息标题"},
        "no_genders_error": {
            "name": "请至少输入一个性别",
            "description": "未输入性别时的错误提示",
        },
        "invalid_genders_error": {
            "name": "以下性别包含非法字符或为保留字: {genders}",
            "description": "性别验证失败时的错误提示",
        },
        "save_error": {
            "name": "保存性别选项失败",
            "description": "保存性别选项时的错误提示",
        },
        "success_message": {
            "name": "成功创建 {count} 个新性别选项",
            "description": "成功创建性别选项时的提示消息",
        },
        "no_new_genders_message": {
            "name": "所有性别选项均已存在，未创建新的性别选项",
            "description": "没有创建新性别选项时的提示消息",
        },
        "unsaved_changes_title": {
            "name": "未保存的更改",
            "description": "未保存更改对话框标题",
        },
        "unsaved_changes_message": {
            "name": "您有未保存的更改，确定要关闭窗口吗？",
            "description": "未保存更改对话框内容",
        },
        "discard_button": {"name": "放弃更改", "description": "放弃更改按钮文本"},
        "continue_editing_button": {
            "name": "继续编辑",
            "description": "继续编辑按钮文本",
        },
        "delete_button": {"name": "删除", "description": "删除按钮文本"},
        "delete_gender_title": {
            "name": "删除性别选项",
            "description": "删除性别选项对话框标题",
        },
        "delete_gender_message": {
            "name": "确定要删除性别选项 '{gender}' 吗？此操作将删除该性别选项的所有信息，且不可恢复",
            "description": "删除性别选项确认对话框内容",
        },
        "delete_multiple_genders_title": {
            "name": "删除多个性别选项",
            "description": "删除多个性别选项对话框标题",
        },
        "delete_multiple_genders_message": {
            "name": "确定要删除以下 {count} 个性别选项吗？此操作将删除这些性别选项的所有信息，且不可恢复\n\n{genders}",
            "description": "删除多个性别选项确认对话框内容",
        },
        "delete_gender_success_title": {
            "name": "删除成功",
            "description": "删除性别选项成功通知标题",
        },
        "delete_gender_success_message": {
            "name": "成功删除 {count} 个性别选项",
            "description": "删除性别选项成功通知内容",
        },
        "delete_gender_cancel_button": {
            "name": "取消删除",
            "description": "取消删除性别选项按钮文本",
        },
        "no_deletable_genders": {
            "name": "没有可删除的性别选项",
            "description": "没有可删除性别选项时的提示",
        },
        "select_gender_to_delete": {
            "name": "请选择要删除的性别选项",
            "description": "选择删除性别选项的提示",
        },
        "select_gender_dialog_title": {
            "name": "选择要删除的性别选项",
            "description": "选择删除性别选项对话框标题",
        },
        "select_gender_dialog_message": {
            "name": "请选择要删除的性别选项：",
            "description": "选择删除性别选项对话框内容",
        },
        "delete_selected_genders_button": {
            "name": "删除选中",
            "description": "删除选中性别选项按钮文本",
        },
        "delete_gender_error": {
            "name": "删除性别选项失败: {error}",
            "description": "删除性别选项失败错误信息",
        },
        "gender_deleted_title": {
            "name": "性别选项已删除",
            "description": "删除性别选项提示标题",
        },
        "gender_deleted_message": {
            "name": "性别选项 '{gender}' 已从输入框中移除，请保存更改以永久删除",
            "description": "删除性别选项提示内容",
        },
    },
    "EN_US": {
        "title": {
            "name": "Gender settings",
            "description": "Set title of Gender settings window",
        },
        "description": {
            "name": "In this window, you can set up student genders\nto enter a gender per line, and the system will store it in\n\nto enter only one gender per line, e.g.:\nMale\nFemale\nNon-binary",
            "description": "Gender settings window description",
        },
        "input_title": {
            "name": "Gender list",
            "description": "Gender input area title",
        },
        "input_placeholder": {
            "name": "Please input genders here, one gender per line",
            "description": "Gender input box placeholder",
        },
        "save_button": {"name": "Save", "description": "Save button text"},
        "cancel_button": {"name": "Cancel", "description": "Button text of Cancel"},
        "error_title": {"name": "Error", "description": "Message title of Error"},
        "success_title": {"name": "Success", "description": "Message title of Success"},
        "info_title": {"name": "Prompt", "description": "Message title of Info"},
        "no_genders_error": {
            "name": "Please enter at least one gender",
            "description": "Error hint shown on no gender is input",
        },
        "invalid_genders_error": {
            "name": "The following genders include invalid characters or reserved words: {genders}",
            "description": "Error hint when gender validation failed",
        },
        "save_error": {
            "name": "Failed to save gender option",
            "description": "Error hint when gender saved failed",
        },
        "success_message": {
            "name": "Succeed creating {count} genders",
            "description": "Message show when the gender settings saved successfully",
        },
        "no_new_genders_message": {
            "name": "All gender options already exist, no new gender options have been created",
            "description": "Notification message when no new gender is created",
        },
        "unsaved_changes_title": {
            "name": "Unsaved changes",
            "description": "Dialog title of change not saved",
        },
        "unsaved_changes_message": {
            "name": "You have unsaved changes. Are you sure you want to close the window?",
            "description": "Dialog content of change not saved",
        },
        "discard_button": {
            "name": "Discard changes",
            "description": "Discard change button text",
        },
        "continue_editing_button": {
            "name": "Keep editing",
            "description": "Continue editing button text",
        },
        "delete_button": {"name": "Delete", "description": "Button text of delete"},
        "delete_gender_title": {
            "name": "Option of delete gender",
            "description": "Delete gender option dialog title",
        },
        "delete_gender_message": {
            "name": "Are you sure to delete the gender option '{gender}'? This will delete all information of this gender and can NOT be restored",
            "description": "Delete gender option dialog message",
        },
        "delete_multiple_genders_title": {
            "name": "Delete multiple gender option",
            "description": "Delete multiple gender dialog titles",
        },
        "delete_multiple_genders_message": {
            "name": "Are you sure to delete the following {count} genders? This will delete all information of these genders and can NOT be restored\n\n{genders}",
            "description": "Delete multiple gender dialog message",
        },
        "delete_gender_success_title": {
            "name": "Delete success",
            "description": "Delete multiple gender dialog success titles",
        },
        "delete_gender_success_message": {
            "name": "Succeed deleting {count} gender options",
            "description": "Notification of delete the gender option successfully",
        },
        "delete_gender_cancel_button": {
            "name": "Cancel delete",
            "description": "Button text of cancel delete gender option",
        },
        "no_deletable_genders": {
            "name": "Option of no gender to delete",
            "description": "Tips when no gender option can be deleted",
        },
        "select_gender_to_delete": {
            "name": "Select gender option to delete",
            "description": "Hint to select the gender option to delete",
        },
        "select_gender_dialog_title": {
            "name": "Option of select gender to delete",
            "description": "Dialog title of tips to choose gender options to be deleted",
        },
        "select_gender_dialog_message": {
            "name": "Select gender option to delete:",
            "description": "Select gender option to delete dialog message",
        },
        "delete_selected_genders_button": {
            "name": "Delete selected",
            "description": "Delete selected gender button text",
        },
        "delete_gender_error": {
            "name": "Failed to delete gender option: {error}",
            "description": "Failed to delete gender error",
        },
        "gender_deleted_title": {
            "name": "Gender option deleted",
            "description": "Delete gender option tip title",
        },
        "gender_deleted_message": {
            "name": "Detected that the gender option '{gender}' have been removed from the input box. Please save your changes to permanently delete it",
            "description": "Delete gender option hint",
        },
    },
    "JA_JP": {
        "title": {
            "name": "性別設定",
            "description": "性別ウィンドウのタイトルを設定",
        },
        "description": {
            "name": "このウィンドウで学生性別を設定できます\n1行に1つの性別を入力すると、システムはクラス名簿ファイルに保存します\n\n1行に1つの性別のみを入力してください。例：\n男性\n女性\nその他",
            "description": "性別設定ウィンドウの説明",
        },
        "input_title": {
            "name": "性別リスト",
            "description": "性別入力エリアのタイトル",
        },
        "input_placeholder": {
            "name": "性別を入力してください、1行に1つの性別",
            "description": "性別入力ボックスのプレースホルダー",
        },
        "save_button": {"name": "保存", "description": "保存ボタンのテキスト"},
        "cancel_button": {
            "name": "キャンセル",
            "description": "キャンセルボタンのテキスト",
        },
        "error_title": {"name": "エラー", "description": "エラーメッセージのタイトル"},
        "success_title": {"name": "成功", "description": "成功メッセージのタイトル"},
        "info_title": {"name": "プロンプト", "description": "情報メッセージのタイトル"},
        "no_genders_error": {
            "name": "少なくとも1つの性別を入力してください",
            "description": "性別が入力されていない場合のエラーヒント",
        },
        "invalid_genders_error": {
            "name": "以下の性別に不正な文字または予約語が含まれています: {genders}",
            "description": "性別検証失敗時のエラーヒント",
        },
        "save_error": {
            "name": "性別オプションの保存に失敗しました",
            "description": "性別オプション保存時のエラーヒント",
        },
        "success_message": {
            "name": "{count}個の新しい性別オプションを作成しました",
            "description": "性別オプション作成成功時のプロンプトメッセージ",
        },
        "no_new_genders_message": {
            "name": "すべての性別オプションが既に存在するため、新しい性別オプションは作成されませんでした",
            "description": "新しい性別オプションが作成されなかった場合のプロンプトメッセージ",
        },
        "unsaved_changes_title": {
            "name": "未保存の変更",
            "description": "未保存変更ダイアログのタイトル",
        },
        "unsaved_changes_message": {
            "name": "未保存の変更があります。ウィンドウを閉じますか？",
            "description": "未保存変更ダイアログの内容",
        },
        "discard_button": {
            "name": "変更を破棄",
            "description": "変更を破棄ボタンのテキスト",
        },
        "continue_editing_button": {
            "name": "編集を続ける",
            "description": "編集を続けるボタンのテキスト",
        },
        "delete_button": {"name": "削除", "description": "削除ボタンのテキスト"},
        "delete_gender_title": {
            "name": "性別オプションを削除",
            "description": "性別オプション削除ダイアログのタイトル",
        },
        "delete_gender_message": {
            "name": "性別オプション '{gender}' を削除しますか？この操作はこの性別オプションのすべての情報を削除し、復元できません",
            "description": "性別オプション削除確認ダイアログの内容",
        },
        "delete_multiple_genders_title": {
            "name": "複数の性別オプションを削除",
            "description": "複数の性別オプション削除ダイアログのタイトル",
        },
        "delete_multiple_genders_message": {
            "name": "以下の{count}個の性別オプションを削除しますか？この操作はこれらの性別オプションのすべての情報を削除し、復元できません\n\n{genders}",
            "description": "複数の性別オプション削除確認ダイアログの内容",
        },
        "delete_gender_success_title": {
            "name": "削除成功",
            "description": "性別オプション削除成功通知のタイトル",
        },
        "delete_gender_success_message": {
            "name": "{count}個の性別オプションを削除しました",
            "description": "性別オプション削除成功通知の内容",
        },
        "delete_gender_cancel_button": {
            "name": "削除をキャンセル",
            "description": "性別オプション削除キャンセルボタンのテキスト",
        },
        "no_deletable_genders": {
            "name": "削除可能な性別オプションがありません",
            "description": "削除可能な性別オプションがない場合のヒント",
        },
        "select_gender_to_delete": {
            "name": "削除する性別オプションを選択してください",
            "description": "削除性別オプション選択のヒント",
        },
        "select_gender_dialog_title": {
            "name": "削除する性別オプションを選択",
            "description": "削除性別オプション選択ダイアログのタイトル",
        },
        "select_gender_dialog_message": {
            "name": "削除する性別オプションを選択してください：",
            "description": "削除性別オプション選択ダイアログの内容",
        },
        "delete_selected_genders_button": {
            "name": "選択を削除",
            "description": "選択削除ボタンのテキスト",
        },
        "delete_gender_error": {
            "name": "性別オプションの削除に失敗しました: {error}",
            "description": "性別オプション削除失敗エラー情報",
        },
        "gender_deleted_title": {
            "name": "性別オプションが削除されました",
            "description": "性別オプション削除ヒントのタイトル",
        },
        "gender_deleted_message": {
            "name": "性別オプション '{gender}' が入力ボックスから削除されたことが検出されました。変更を保存して永久に削除してください",
            "description": "性別オプション削除ヒントの内容",
        },
    },
}

# 小组设置窗口
group_setting = {
    "ZH_CN": {
        "title": {"name": "小组设置", "description": "设置小组窗口标题"},
        "description": {
            "name": "在此窗口中，您可以设置学生小组\n每行输入一个小组，系统会将其存储到班级名单文件中\n\n请每行只输入一个小组，例如：\nA组\nB组\nC组",
            "description": "小组设置窗口描述",
        },
        "input_title": {"name": "小组列表", "description": "小组输入区域标题"},
        "input_placeholder": {
            "name": "请输入小组，每行一个小组",
            "description": "小组输入框占位符",
        },
        "save_button": {"name": "保存", "description": "保存按钮文本"},
        "cancel_button": {"name": "取消", "description": "取消按钮文本"},
        "error_title": {"name": "错误", "description": "错误消息标题"},
        "success_title": {"name": "成功", "description": "成功消息标题"},
        "info_title": {"name": "提示", "description": "信息消息标题"},
        "no_groups_error": {
            "name": "请至少输入一个小组",
            "description": "未输入小组时的错误提示",
        },
        "invalid_groups_error": {
            "name": "以下小组包含非法字符或为保留字: {groups}",
            "description": "小组验证失败时的错误提示",
        },
        "save_error": {
            "name": "保存小组选项失败",
            "description": "保存小组选项时的错误提示",
        },
        "success_message": {
            "name": "成功创建 {count} 个新小组选项",
            "description": "成功创建小组选项时的提示消息",
        },
        "no_new_groups_message": {
            "name": "所有小组选项均已存在，未创建新的小组选项",
            "description": "没有创建新小组选项时的提示消息",
        },
        "unsaved_changes_title": {
            "name": "未保存的更改",
            "description": "未保存更改对话框标题",
        },
        "unsaved_changes_message": {
            "name": "您有未保存的更改，确定要关闭窗口吗？",
            "description": "未保存更改对话框内容",
        },
        "discard_button": {"name": "放弃更改", "description": "放弃更改按钮文本"},
        "continue_editing_button": {
            "name": "继续编辑",
            "description": "继续编辑按钮文本",
        },
        "delete_button": {"name": "删除", "description": "删除按钮文本"},
        "delete_group_title": {
            "name": "删除小组选项",
            "description": "删除小组选项对话框标题",
        },
        "delete_group_message": {
            "name": "确定要删除小组选项 '{group}' 吗？此操作将删除该小组选项的所有信息，且不可恢复",
            "description": "删除小组选项确认对话框内容",
        },
        "delete_multiple_groups_title": {
            "name": "删除多个小组选项",
            "description": "删除多个小组选项对话框标题",
        },
        "delete_multiple_groups_message": {
            "name": "确定要删除以下 {count} 个小组选项吗？此操作将删除这些小组选项的所有信息，且不可恢复\n\n{groups}",
            "description": "删除多个小组选项确认对话框内容",
        },
        "delete_group_success_title": {
            "name": "删除成功",
            "description": "删除小组选项成功通知标题",
        },
        "delete_group_success_message": {
            "name": "成功删除 {count} 个小组选项",
            "description": "删除小组选项成功通知内容",
        },
        "delete_group_cancel_button": {
            "name": "取消删除",
            "description": "取消删除小组选项按钮文本",
        },
        "no_deletable_groups": {
            "name": "没有可删除的小组选项",
            "description": "没有可删除小组选项时的提示",
        },
        "select_group_to_delete": {
            "name": "请选择要删除的小组选项",
            "description": "选择删除小组选项的提示",
        },
        "select_group_dialog_title": {
            "name": "选择要删除的小组选项",
            "description": "选择删除小组选项对话框标题",
        },
        "select_group_dialog_message": {
            "name": "请选择要删除的小组选项：",
            "description": "选择删除小组选项对话框内容",
        },
        "delete_selected_groups_button": {
            "name": "删除选中",
            "description": "删除选中小组选项按钮文本",
        },
        "delete_group_error": {
            "name": "删除小组选项失败: {error}",
            "description": "删除小组选项失败错误信息",
        },
        "group_deleted_title": {
            "name": "小组选项已删除",
            "description": "删除小组选项提示标题",
        },
        "group_deleted_message": {
            "name": "小组选项 '{group}' 已从输入框中移除，请保存更改以永久删除",
            "description": "删除小组选项提示内容",
        },
    },
    "EN_US": {
        "title": {
            "name": "Group Settings",
            "description": "Group settings window title",
        },
        "description": {
            "name": "In this window, you can set up the group name\nto enter a group name per line, and the system will store it in\n\nto enter only one group name per line, e.g.:\nGroup A\nGroup B\nGroup C",
            "description": "Group settings window description",
        },
        "input_title": {"name": "Group list", "description": "Group input area title"},
        "input_placeholder": {
            "name": "Please input group name, one per line. ",
            "description": "Group input box placeholder",
        },
        "save_button": {"name": "Save", "description": "Button text of Save"},
        "cancel_button": {"name": "Cancel", "description": "Button text of Cancel"},
        "error_title": {"name": "Error", "description": "Message title of Error"},
        "success_title": {"name": "Success", "description": "Message title of Success"},
        "info_title": {"name": "Prompt", "description": "Message title of Info"},
        "no_groups_error": {
            "name": "Please enter at least one group",
            "description": "Error hint shown on no group is input",
        },
        "invalid_groups_error": {
            "name": "The following groups include invalid characters or reserved words: {groups}",
            "description": "Error hint when group name validation failed",
        },
        "save_error": {
            "name": "Failed to save group option",
            "description": "Error hint when group saved failed",
        },
        "success_message": {
            "name": "Succeed creating {count} group options",
            "description": "Message show when the group settings saved successfully",
        },
        "no_new_groups_message": {
            "name": "All group options already exist, no new group options have been created",
            "description": "Notification message when no new group is created",
        },
        "unsaved_changes_title": {
            "name": "Unsaved changes",
            "description": "Dialog title of change not saved",
        },
        "unsaved_changes_message": {
            "name": "You have unsaved changes. Are you sure you want to close the window?",
            "description": "Dialog content of change not saved",
        },
        "discard_button": {
            "name": "Discard changes",
            "description": "Discard change button text",
        },
        "continue_editing_button": {
            "name": "Keep editing",
            "description": "Continue editing button text",
        },
        "delete_button": {"name": "Delete", "description": "Button text of Delete"},
        "delete_group_title": {
            "name": "Option of Delete group",
            "description": "Delete group option dialog title",
        },
        "delete_group_message": {
            "name": "Are you sure to delete the group option '{group}'? This will delete all information of this group and can NOT be restored",
            "description": "Delete group dialog message",
        },
        "delete_multiple_groups_title": {
            "name": "Delete multiple group option",
            "description": "Delete multiple group option dialog title",
        },
        "delete_multiple_groups_message": {
            "name": "Are you sure to delete the following {count} groups? This will delete all information of these groups and can NOT be restored\n\n{groups}",
            "description": "Delete multiple group dialog message",
        },
        "delete_group_success_title": {
            "name": "Delete success",
            "description": "Delete group dialog success titles",
        },
        "delete_group_success_message": {
            "name": "Succeed deleting {count} group options",
            "description": "Notification of delete the group option successfully",
        },
        "delete_group_cancel_button": {
            "name": "Cancel delete",
            "description": "Button text of cancel delete group option",
        },
        "no_deletable_groups": {
            "name": "Option of no group to delete",
            "description": "Tips when no group option can be deleted",
        },
        "select_group_to_delete": {
            "name": "Please select the group option to delete",
            "description": "Hint to select the group option to delete",
        },
        "select_group_dialog_title": {
            "name": "Option of select group to delete",
            "description": "Dialog title of tips to choose group options to be deleted",
        },
        "select_group_dialog_message": {
            "name": "Please select the group option to delete:",
            "description": "Dialog content of tips to choose group options to be deleted",
        },
        "delete_selected_groups_button": {
            "name": "Delete selected",
            "description": "Delete selected names button text",
        },
        "delete_group_error": {
            "name": "Failed to delete group option: {error}",
            "description": "Failed to delete prize name error",
        },
        "group_deleted_title": {
            "name": "Group option deleted",
            "description": "Delete group options tip title",
        },
        "group_deleted_message": {
            "name": "Detected that the group option '{group}' have been removed from the input box. Please save your changes to permanently delete it",
            "description": "Delete group options hint",
        },
    },
    "JA_JP": {
        "title": {
            "name": "グループ設定",
            "description": "グループウィンドウのタイトルを設定",
        },
        "description": {
            "name": "このウィンドウで学生グループを設定できます\n1行に1つのグループを入力すると、システムはクラス名簿ファイルに保存します\n\n1行に1つのグループのみを入力してください。例：\nAグループ\nBグループ\nCグループ",
            "description": "グループ設定ウィンドウの説明",
        },
        "input_title": {
            "name": "グループリスト",
            "description": "グループ入力エリアのタイトル",
        },
        "input_placeholder": {
            "name": "グループを入力してください、1行に1つのグループ",
            "description": "グループ入力ボックスのプレースホルダー",
        },
        "save_button": {"name": "保存", "description": "保存ボタンのテキスト"},
        "cancel_button": {
            "name": "キャンセル",
            "description": "キャンセルボタンのテキスト",
        },
        "error_title": {"name": "エラー", "description": "エラーメッセージのタイトル"},
        "success_title": {"name": "成功", "description": "成功メッセージのタイトル"},
        "info_title": {"name": "プロンプト", "description": "情報メッセージのタイトル"},
        "no_groups_error": {
            "name": "少なくとも1つのグループを入力してください",
            "description": "グループが入力されていない場合のエラーヒント",
        },
        "invalid_groups_error": {
            "name": "以下のグループに不正な文字または予約語が含まれています: {groups}",
            "description": "グループ検証失敗時のエラーヒント",
        },
        "save_error": {
            "name": "グループオプションの保存に失敗しました",
            "description": "グループオプション保存時のエラーヒント",
        },
        "success_message": {
            "name": "{count}個の新しいグループオプションを作成しました",
            "description": "グループオプション作成成功時のプロンプトメッセージ",
        },
        "no_new_groups_message": {
            "name": "すべてのグループオプションが既に存在するため、新しいグループオプションは作成されませんでした",
            "description": "新しいグループオプションが作成されなかった場合のプロンプトメッセージ",
        },
        "unsaved_changes_title": {
            "name": "未保存の変更",
            "description": "未保存変更ダイアログのタイトル",
        },
        "unsaved_changes_message": {
            "name": "未保存の変更があります。ウィンドウを閉じますか？",
            "description": "未保存変更ダイアログの内容",
        },
        "discard_button": {
            "name": "変更を破棄",
            "description": "変更を破棄ボタンのテキスト",
        },
        "continue_editing_button": {
            "name": "編集を続ける",
            "description": "編集を続けるボタンのテキスト",
        },
        "delete_button": {"name": "削除", "description": "削除ボタンのテキスト"},
        "delete_group_title": {
            "name": "グループオプションを削除",
            "description": "グループオプション削除ダイアログのタイトル",
        },
        "delete_group_message": {
            "name": "グループオプション '{group}' を削除しますか？この操作はこのグループオプションのすべての情報を削除し、復元できません",
            "description": "グループオプション削除確認ダイアログの内容",
        },
        "delete_multiple_groups_title": {
            "name": "複数のグループオプションを削除",
            "description": "複数のグループオプション削除ダイアログのタイトル",
        },
        "delete_multiple_groups_message": {
            "name": "以下の{count}個のグループオプションを削除しますか？この操作はこれらのグループオプションのすべての情報を削除し、復元できません\n\n{groups}",
            "description": "複数のグループオプション削除確認ダイアログの内容",
        },
        "delete_group_success_title": {
            "name": "削除成功",
            "description": "グループオプション削除成功通知のタイトル",
        },
        "delete_group_success_message": {
            "name": "{count}個のグループオプションを削除しました",
            "description": "グループオプション削除成功通知の内容",
        },
        "delete_group_cancel_button": {
            "name": "削除をキャンセル",
            "description": "グループオプション削除キャンセルボタンのテキスト",
        },
        "no_deletable_groups": {
            "name": "削除可能なグループオプションがありません",
            "description": "削除可能なグループオプションがない場合のヒント",
        },
        "select_group_to_delete": {
            "name": "削除するグループオプションを選択してください",
            "description": "削除グループオプション選択のヒント",
        },
        "select_group_dialog_title": {
            "name": "削除するグループオプションを選択",
            "description": "削除グループオプション選択ダイアログのタイトル",
        },
        "select_group_dialog_message": {
            "name": "削除するグループオプションを選択してください：",
            "description": "削除グループオプション選択ダイアログの内容",
        },
        "delete_selected_groups_button": {
            "name": "選択を削除",
            "description": "選択削除ボタンのテキスト",
        },
        "delete_group_error": {
            "name": "グループオプションの削除に失敗しました: {error}",
            "description": "グループオプション削除失敗エラー情報",
        },
        "group_deleted_title": {
            "name": "グループオプションが削除されました",
            "description": "グループオプション削除ヒントのタイトル",
        },
        "group_deleted_message": {
            "name": "グループオプション '{group}' が入力ボックスから削除されたことが検出されました。変更を保存して永久に削除してください",
            "description": "グループオプション削除ヒントの内容",
        },
    },
}

# 标签设置窗口
tag_setting = {
    "ZH_CN": {
        "title": {"name": "标签设置", "description": "学生标签设置窗口标题"},
        "description": {
            "name": "在此窗口中，您可以为学生设置标签\n双击“标签”列进行编辑，多个标签可用空格或逗号分隔",
            "description": "学生标签设置窗口描述",
        },
        "header_labels": {
            "name": ["学号", "姓名", "标签"],
            "description": "表格表头",
        },
        "save_button": {"name": "保存", "description": "保存按钮文本"},
        "error_title": {"name": "错误", "description": "错误消息标题"},
        "success_title": {"name": "成功", "description": "成功消息标题"},
        "no_list_selected": {
            "name": "请先选择班级",
            "description": "未选择班级提示",
        },
        "list_file_missing": {
            "name": "班级名单文件不存在",
            "description": "名单文件不存在提示",
        },
        "success_message": {
            "name": "标签已保存",
            "description": "保存成功提示",
        },
        "save_error": {
            "name": "保存标签失败",
            "description": "保存失败前缀",
        },
        "unsaved_changes_title": {
            "name": "未保存的更改",
            "description": "未保存更改对话框标题",
        },
        "unsaved_changes_message": {
            "name": "您有未保存的更改，确定要关闭窗口吗？",
            "description": "未保存更改对话框内容",
        },
        "discard_button": {"name": "放弃更改", "description": "放弃更改按钮文本"},
        "continue_editing_button": {
            "name": "继续编辑",
            "description": "继续编辑按钮文本",
        },
    },
    "EN_US": {
        "title": {"name": "Tag settings", "description": "Student tag settings title"},
        "description": {
            "name": "Edit student tags in this window\nDouble click the “Tags” column to edit. Separate multiple tags with spaces or commas",
            "description": "Student tag settings description",
        },
        "header_labels": {
            "name": ["ID", "Name", "Tags"],
            "description": "Table headers",
        },
        "save_button": {"name": "Save", "description": "Save button text"},
        "error_title": {"name": "Error", "description": "Error title"},
        "success_title": {"name": "Success", "description": "Success title"},
        "no_list_selected": {
            "name": "Please select a class first",
            "description": "No class selected hint",
        },
        "list_file_missing": {
            "name": "Class list file not found",
            "description": "Missing list file hint",
        },
        "success_message": {"name": "Tags saved", "description": "Save success hint"},
        "save_error": {
            "name": "Failed to save tags",
            "description": "Save error prefix",
        },
        "unsaved_changes_title": {
            "name": "Unsaved changes",
            "description": "Unsaved changes dialog title",
        },
        "unsaved_changes_message": {
            "name": "You have unsaved changes. Close this window?",
            "description": "Unsaved changes dialog content",
        },
        "discard_button": {"name": "Discard", "description": "Discard button text"},
        "continue_editing_button": {
            "name": "Continue editing",
            "description": "Continue editing button text",
        },
    },
    "JA_JP": {
        "title": {
            "name": "タグ設定",
            "description": "学生タグ設定ウィンドウのタイトル",
        },
        "description": {
            "name": "このウィンドウでは学生のタグを設定できます\n「タグ」列をダブルクリックして編集し、複数のタグは空白またはカンマで区切ります",
            "description": "学生タグ設定ウィンドウの説明",
        },
        "header_labels": {
            "name": ["ID", "氏名", "タグ"],
            "description": "テーブルヘッダー",
        },
        "save_button": {"name": "保存", "description": "保存ボタンのテキスト"},
        "error_title": {"name": "エラー", "description": "エラータイトル"},
        "success_title": {"name": "成功", "description": "成功タイトル"},
        "no_list_selected": {
            "name": "先にクラスを選択してください",
            "description": "クラス未選択のヒント",
        },
        "list_file_missing": {
            "name": "クラスリストファイルが見つかりません",
            "description": "リストファイル不存在のヒント",
        },
        "success_message": {
            "name": "タグを保存しました",
            "description": "保存成功のヒント",
        },
        "save_error": {
            "name": "タグの保存に失敗しました",
            "description": "保存失敗の前置き",
        },
        "unsaved_changes_title": {
            "name": "未保存の変更",
            "description": "未保存変更ダイアログのタイトル",
        },
        "unsaved_changes_message": {
            "name": "未保存の変更があります。ウィンドウを閉じますか？",
            "description": "未保存変更ダイアログの内容",
        },
        "discard_button": {"name": "破棄", "description": "破棄ボタンのテキスト"},
        "continue_editing_button": {
            "name": "編集を続ける",
            "description": "編集を続けるボタンのテキスト",
        },
    },
}
