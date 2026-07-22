# 奖池名称设置窗口
set_prize_name = {
    "ZH_CN": {
        "title": {"name": "奖池名称设置", "description": "设置奖池名称窗口标题"},
        "description": {
            "name": "在此窗口中，您可以设置奖池名称\n每行输入一个奖池名称，系统会将其存储到奖池名单文件中\n\n请每行只输入一个奖池名称，例如：\n奖池一\n奖池二\n奖池三",
            "description": "奖池名称设置窗口描述",
        },
        "input_title": {"name": "奖池名称列表", "description": "奖池名称输入区域标题"},
        "input_placeholder": {
            "name": "请输入奖池名称，每行一个奖池名称",
            "description": "奖池名称输入框占位符",
        },
        "save_button": {"name": "保存", "description": "保存按钮文本"},
        "cancel_button": {"name": "取消", "description": "取消按钮文本"},
        "error_title": {"name": "错误", "description": "错误消息标题"},
        "success_title": {"name": "成功", "description": "成功消息标题"},
        "info_title": {"name": "提示", "description": "信息消息标题"},
        "invalid_names_error": {
            "name": "以下奖池名称包含非法字符或为保留字: {names}",
            "description": "奖池名称验证失败时的错误提示",
        },
        "duplicate_names_title": {
            "name": "发现重复名称",
            "description": "名称重复对话框标题",
        },
        "duplicate_names_message": {
            "name": "检测到 {count} 个重复的奖池名称：\n{names}\n\n请选择返回编辑，或自动将重复项重命名为“_1/_2…”格式。",
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
            "name": "保存奖池名称失败",
            "description": "保存奖池名称时的错误提示",
        },
        "success_message": {
            "name": "成功创建 {count} 个新奖池",
            "description": "成功创建奖池时的提示消息",
        },
        "no_new_prizes_message": {
            "name": "所有奖池名称均已存在，未创建新的奖池",
            "description": "没有创建新奖池时的提示消息",
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
        "delete_prize_title": {"name": "删除奖池", "description": "删除奖池对话框标题"},
        "delete_prize_message": {
            "name": "确定要删除奖池 '{prize_name}' 吗？此操作将删除该奖池的所有数据，且不可恢复",
            "description": "删除奖池确认对话框内容",
        },
        "delete_prize_button": {"name": "删除奖池", "description": "删除奖池按钮文本"},
        "delete_multiple_prizes_title": {
            "name": "删除多个奖池",
            "description": "删除多个奖池对话框标题",
        },
        "delete_multiple_prizes_message": {
            "name": "确定要删除以下 {count} 个奖池吗？此操作将删除这些奖池的所有数据，且不可恢复\n\n{prize_names}",
            "description": "删除多个奖池确认对话框内容",
        },
        "delete_success_title": {"name": "删除成功", "description": "删除成功通知标题"},
        "delete_success_message": {
            "name": "成功删除 {count} 个奖池",
            "description": "删除成功通知内容",
        },
        "delete_cancel_button": {"name": "取消删除", "description": "取消删除按钮文本"},
        "no_deletable_prizes": {
            "name": "没有可删除的奖池",
            "description": "没有可删除奖池时的提示",
        },
        "select_prize_to_delete": {
            "name": "请选择要删除的奖池",
            "description": "选择删除奖池的提示",
        },
        "select_prize_dialog_title": {
            "name": "选择要删除的奖池",
            "description": "选择删除奖池对话框标题",
        },
        "select_prize_dialog_message": {
            "name": "请选择要删除的奖池：",
            "description": "选择删除奖池对话框内容",
        },
        "delete_selected_button": {
            "name": "删除选中",
            "description": "删除选中按钮文本",
        },
        "delete_prize_error": {
            "name": "删除奖池失败: {error}",
            "description": "删除奖池失败错误信息",
        },
        "prize_disappeared_title": {
            "name": "奖池消失提示",
            "description": "奖池消失提示标题",
        },
        "prize_disappeared_message": {
            "name": "检测到奖池 '{prize_name}' 已从输入框中移除，请保存更改以永久删除",
            "description": "单个奖池消失提示内容",
        },
        "multiple_prizes_disappeared_message": {
            "name": "检测到以下 {count} 个奖池已从输入框中移除，请保存更改以永久删除：\n{prize_names}",
            "description": "多个奖池消失提示内容",
        },
    },
    "EN_US": {
        "title": {
            "name": "Pool name settings",
            "description": "Set the pool name window title",
        },
        "description": {
            "name": "In this window, you can set up the pool name\nto enter a pool name per line, and the system will store it in\n\nto enter only one pool name per line, e.g.:\nPool I\nPool II\nPool III",
            "description": "Pool name settings window description",
        },
        "input_title": {
            "name": "List of prize names",
            "description": "Pool name enter area title",
        },
        "input_placeholder": {
            "name": "Please enter the pool name, one pool name per row",
            "description": "Pool name input placeholder",
        },
        "save_button": {"name": "Save", "description": "Button text of Save"},
        "cancel_button": {"name": "Cancel", "description": "Button text of Cancel"},
        "error_title": {"name": "Error", "description": "Message title of Error"},
        "success_title": {"name": "Success", "description": "Message title of Success"},
        "info_title": {"name": "Prompt", "description": "Message title of Info"},
        "invalid_names_error": {
            "name": "The following pool names include invalid characters or reserved words: {names}",
            "description": "Error hint when prize name validation failed",
        },
        "duplicate_names_title": {
            "name": "Duplicate names found",
            "description": "Dialog title when duplicate names are detected",
        },
        "duplicate_names_message": {
            "name": "Detected {count} duplicate pool names:\n{names}\n\nChoose to go back and edit, or automatically rename duplicates with “_1/_2…” suffix.",
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
            "name": "Failed to save pool name",
            "description": "Error hint when saving pool name",
        },
        "success_message": {
            "name": "Succeed creating {count} prize pools",
            "description": "Alert message when creating prize pool successfully",
        },
        "no_new_prizes_message": {
            "name": "All pool names already exist, no new pool has been created",
            "description": "Tips when not created a new pool",
        },
        "unsaved_changes_title": {
            "name": "Unsaved changes",
            "description": "Change dialog title is not saved",
        },
        "unsaved_changes_message": {
            "name": "You have unsaved changes. Are you sure you want to close the window?",
            "description": "Change dialog content not saved",
        },
        "discard_button": {
            "name": "Discard changes",
            "description": "Discard change button text",
        },
        "continue_editing_button": {
            "name": "Keep editing",
            "description": "Continue editing button text",
        },
        "delete_prize_title": {
            "name": "Delete pool",
            "description": "Delete pool dialog title",
        },
        "delete_prize_message": {
            "name": "Are you sure to delete the pool '{prize_name}'? This will delete all data of this pool and can NOT be restored",
            "description": "Delete pool confirmation dialog",
        },
        "delete_prize_button": {
            "name": "Delete pool",
            "description": "Delete hole button text",
        },
        "delete_multiple_prizes_title": {
            "name": "Delete multiple pool",
            "description": "Delete multiple pool dialog title",
        },
        "delete_multiple_prizes_message": {
            "name": "Are you sure to delete the following {count} pools? This will delete all data of these pools and can NOT be restored\n\n{prize_names}",
            "description": "Delete multiple pool confirmation dialog content",
        },
        "delete_success_title": {
            "name": "Delete success",
            "description": "Delete successful notification title",
        },
        "delete_success_message": {
            "name": "Succeed deleting {count} prize pools",
            "description": "Delete successful notifications",
        },
        "delete_cancel_button": {
            "name": "Cancel delete",
            "description": "Cancel button text",
        },
        "no_deletable_prizes": {
            "name": "No pool to delete",
            "description": "Tips when no prize pool can be deleted",
        },
        "select_prize_to_delete": {
            "name": "Please select a pool to delete",
            "description": "Hint to select the prize pool to delete",
        },
        "select_prize_dialog_title": {
            "name": "Select the pool to delete",
            "description": "Select to delete the pool dialog title",
        },
        "select_prize_dialog_message": {
            "name": "Please select the prize pool to delete:",
            "description": "Select to delete the pool dialog",
        },
        "delete_selected_button": {
            "name": "Delete selected",
            "description": "Delete selected button text",
        },
        "delete_prize_error": {
            "name": "Failed to delete prize pool: {error}",
            "description": "Failed to delete pool error",
        },
        "prize_disappeared_title": {
            "name": "Prizes lost hint",
            "description": "Pool missing hint title",
        },
        "prize_disappeared_message": {
            "name": "Detected that the pool '{prize_name}' have been removed from the input box. Please save your changes to permanently delete it",
            "description": "Dismiss prompt content for individual prizes",
        },
        "multiple_prizes_disappeared_message": {
            "name": "Detected that following {count} prize pools have been removed from the input box. Please save your changes to permanently delete them:\n{prize_names}",
            "description": "Multiple pool disappear tips",
        },
    },
    "JA_JP": {
        "title": {
            "name": "賞プール名設定",
            "description": "賞プール名ウィンドウのタイトルを設定",
        },
        "description": {
            "name": "このウィンドウで賞プール名を設定できます\n1行に1つの賞プール名を入力すると、システムは賞プール名簿ファイルに保存します\n\n1行に1つの賞プール名のみを入力してください。例：\n賞プール一\n賞プール二\n賞プール三",
            "description": "賞プール名設定ウィンドウの説明",
        },
        "input_title": {
            "name": "賞プール名リスト",
            "description": "賞プール名入力エリアのタイトル",
        },
        "input_placeholder": {
            "name": "賞プール名を入力してください、1行に1つの賞プール名",
            "description": "賞プール名入力ボックスのプレースホルダー",
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
            "name": "以下の賞プール名に不正な文字または予約語が含まれています: {names}",
            "description": "賞プール名検証失敗時のエラーヒント",
        },
        "duplicate_names_title": {
            "name": "重複名が見つかりました",
            "description": "重複名検出ダイアログのタイトル",
        },
        "duplicate_names_message": {
            "name": "{count}個の重複した賞プール名が検出されました：\n{names}\n\n編集に戻るか、重複項目を“_1/_2…”の形式で自動リネームしてください。",
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
            "name": "賞プール名の保存に失敗しました",
            "description": "賞プール名保存時のエラーヒント",
        },
        "success_message": {
            "name": "{count}個の新しい賞プールを作成しました",
            "description": "賞プール作成成功時のプロンプトメッセージ",
        },
        "no_new_prizes_message": {
            "name": "すべての賞プール名が既に存在するため、新しい賞プールは作成されませんでした",
            "description": "新しい賞プールが作成されなかった場合のプロンプトメッセージ",
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
        "delete_prize_title": {
            "name": "賞プールを削除",
            "description": "賞プール削除ダイアログのタイトル",
        },
        "delete_prize_message": {
            "name": "賞プール '{prize_name}' を削除しますか？この操作はこの賞プールのすべてのデータを削除し、復元できません",
            "description": "賞プール削除確認ダイアログの内容",
        },
        "delete_prize_button": {
            "name": "賞プールを削除",
            "description": "賞プール削除ボタンのテキスト",
        },
        "delete_multiple_prizes_title": {
            "name": "複数の賞プールを削除",
            "description": "複数の賞プール削除ダイアログのタイトル",
        },
        "delete_multiple_prizes_message": {
            "name": "以下の{count}個の賞プールを削除しますか？この操作はこれらの賞プールのすべてのデータを削除し、復元できません\n\n{prize_names}",
            "description": "複数の賞プール削除確認ダイアログの内容",
        },
        "delete_success_title": {
            "name": "削除成功",
            "description": "削除成功通知のタイトル",
        },
        "delete_success_message": {
            "name": "{count}個の賞プールを削除しました",
            "description": "削除成功通知の内容",
        },
        "delete_cancel_button": {
            "name": "削除をキャンセル",
            "description": "削除キャンセルボタンのテキスト",
        },
        "no_deletable_prizes": {
            "name": "削除可能な賞プールがありません",
            "description": "削除可能な賞プールがない場合のヒント",
        },
        "select_prize_to_delete": {
            "name": "削除する賞プールを選択してください",
            "description": "削除賞プール選択のヒント",
        },
        "select_prize_dialog_title": {
            "name": "削除する賞プールを選択",
            "description": "削除賞プール選択ダイアログのタイトル",
        },
        "select_prize_dialog_message": {
            "name": "削除する賞プールを選択してください：",
            "description": "削除賞プール選択ダイアログの内容",
        },
        "delete_selected_button": {
            "name": "選択を削除",
            "description": "選択削除ボタンのテキスト",
        },
        "delete_prize_error": {
            "name": "賞プールの削除に失敗しました: {error}",
            "description": "賞プール削除失敗エラー情報",
        },
        "prize_disappeared_title": {
            "name": "賞プール消失ヒント",
            "description": "賞プール消失ヒントのタイトル",
        },
        "prize_disappeared_message": {
            "name": "賞プール '{prize_name}' が入力ボックスから削除されたことが検出されました。変更を保存して永久に削除してください",
            "description": "単一賞プール消失ヒントの内容",
        },
        "multiple_prizes_disappeared_message": {
            "name": "以下の{count}個の賞プールが入力ボックスから削除されたことが検出されました。変更を保存して永久に削除してください：\n{prize_names}",
            "description": "複数賞プール消失ヒントの内容",
        },
    },
}

# 导入奖池名称语言配置
import_prize_name = {
    "ZH_CN": {
        "title": {
            "name": "导入奖池名称",
            "description": "从Excel或CSV文件导入奖池名称",
        },
        "initial_subtitle": {
            "name": "正在导入到：",
            "description": "正在导入到奖池的提示",
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
            "name": "请选择包含奖池信息的列",
            "description": "列映射区域说明",
        },
        "column_mapping_id_column": {
            "name": "序号列 (必选):",
            "description": "序号列标签",
        },
        "column_mapping_name_column": {
            "name": "奖池名称列 (必选):",
            "description": "奖池名称列标签",
        },
        "column_mapping_weight_column": {
            "name": "权重列 (可选):",
            "description": "权重列标签",
        },
        "column_mapping_count_column": {
            "name": "数量列 (可选):",
            "description": "数量列标签",
        },
        "column_mapping_tags_column": {
            "name": "标签列 (可选):",
            "description": "标签列标签",
        },
        "column_mapping_none": {"name": "无", "description": "无选项文本"},
        "data_preview_title": {"name": "数据预览", "description": "数据预览区域标题"},
        "prize_id": {"name": "序号", "description": "序号列标题"},
        "prize_name": {"name": "奖池名称", "description": "奖池名称列标题"},
        "weight": {"name": "权重", "description": "权重列标题"},
        "count": {"name": "数量", "description": "数量列标题"},
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
            "name": "请选择奖池名称列",
            "description": "未选择奖池名称列错误信息",
        },
        "no_id_column": {"name": "请选择序号列", "description": "未选择序号列错误信息"},
        "duplicate_names_title": {
            "name": "发现重复名称",
            "description": "导入时名称重复对话框标题",
        },
        "duplicate_names_message": {
            "name": "检测到 {count} 个重复的奖池名称：\n{names}\n\n请选择返回编辑，或自动将重复项重命名为“_1/_2…”格式。",
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
            "name": "成功导入 {count} 个奖池信息到奖池 '{prize_name}'",
            "description": "导入成功对话框内容模板",
        },
        "import_success_notification_title": {
            "name": "导入成功",
            "description": "导入成功通知标题",
        },
        "import_success_notification_content_template": {
            "name": "成功导入 {count} 个奖池信息到奖池 '{prize_name}'",
            "description": "导入成功通知内容模板",
        },
        "existing_data_title": {
            "name": "奖池已有数据",
            "description": "奖池已有数据对话框标题",
        },
        "existing_data_prompt": {
            "name": "奖池 '{prize_name}' 已包含 {count} 个奖池信息，请选择处理方式:",
            "description": "奖池已有数据对话框提示文本",
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
            "name": "Import pool name",
            "description": "Import pool name from Excel or CSV file",
        },
        "initial_subtitle": {
            "name": "Importing to:",
            "description": "Importing to the prize pool tips",
        },
        "file_selection_title": {
            "name": "File select",
            "description": "File selection area title",
        },
        "no_file_selected": {
            "name": "No file selected",
            "description": "Hint text when no file is selected",
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
            "description": "File selection dialog filters",
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
            "name": "Please select a column containing the pool information",
            "description": "Column map area description",
        },
        "column_mapping_id_column": {
            "name": "Serial column (required):",
            "description": "Serial Number Label",
        },
        "column_mapping_name_column": {
            "name": "Pool name column (required):",
            "description": "Label of Pool name list",
        },
        "column_mapping_weight_column": {
            "name": "Weight column (optional):",
            "description": "Column label of Weight",
        },
        "column_mapping_count_column": {
            "name": "Count column (optional):",
            "description": "Column label of Count",
        },
        "column_mapping_tags_column": {
            "name": "Tags column (optional):",
            "description": "Column label of Tags",
        },
        "column_mapping_none": {"name": "None", "description": "Text of None"},
        "data_preview_title": {
            "name": "Data preview",
            "description": "Preview area title",
        },
        "prize_id": {"name": "Serial", "description": "Serial Number Title"},
        "prize_name": {"name": "Pool name", "description": "Title of Pool name list"},
        "weight": {"name": "Weight", "description": "Column title of Weight"},
        "count": {"name": "Count", "description": "Column title of Count"},
        "tags": {"name": "Tags", "description": "Column title of Tags"},
        "buttons_import": {"name": "Import", "description": "Button text of Import"},
        "file_loaded_title": {
            "name": "File loaded",
            "description": "File loaded successfully dialog title",
        },
        "file_loaded_content": {
            "name": "Files loaded successfully",
            "description": "File loaded successfully dialog content",
        },
        "file_loaded_notification_title": {
            "name": "Files loaded successfully",
            "description": "File loaded with successful notification header",
        },
        "file_loaded_notification_content": {
            "name": "File successfully loaded, please check data preview",
            "description": "File loaded with successful notifications",
        },
        "error_title": {"name": "Error", "description": "Dialog title of Error"},
        "load_failed": {
            "name": "Failed to load files",
            "description": "Failed to load file error",
        },
        "load_failed_notification_title": {
            "name": "Failed to load files",
            "description": "Failed to load file notification title",
        },
        "load_failed_notification_content": {
            "name": "Could not load file. Please check file format and content",
            "description": "Failed to load notification content",
        },
        "import_failed": {
            "name": "Failed to import data",
            "description": "Error importing data",
        },
        "import_failed_notification_title": {
            "name": "Failed to import data",
            "description": "Failed to import data notification title",
        },
        "import_failed_notification_content": {
            "name": "Error importing data, please check data format and content",
            "description": "Failed to import data content",
        },
        "unsupported_format": {
            "name": "Unsupported file format",
            "description": "Unsupported file format error",
        },
        "no_name_column": {
            "name": "Please select a pool name column",
            "description": "List of prize names not selected",
        },
        "no_id_column": {
            "name": "Please select serial number column",
            "description": "Error: No serial number column selected",
        },
        "duplicate_names_title": {
            "name": "Duplicate names found",
            "description": "Dialog title when duplicate names are detected during import",
        },
        "duplicate_names_message": {
            "name": "Detected {count} duplicate pool names:\n{names}\n\nChoose to go back and edit, or automatically rename duplicates with “_1/_2…” suffix.",
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
            "description": "Import successful dialog title",
        },
        "import_success_content_template": {
            "name": "Succeed importing {count} prizes to pool '{prize_name}'",
            "description": "Import successful dialog content template",
        },
        "import_success_notification_title": {
            "name": "Import success",
            "description": "Import successful notification title",
        },
        "import_success_notification_content_template": {
            "name": "Succeed importing {count} prizes to pool '{prize_name}'",
            "description": "Import successful notification content template",
        },
        "existing_data_title": {
            "name": "Pool already has data",
            "description": "Holds already have data dialog title",
        },
        "existing_data_prompt": {
            "name": "Pool '{prize_name}' has already contained {count} prizes, please select handling method:",
            "description": "Pool already has data dialog tip text",
        },
        "existing_data_option_overwrite": {
            "name": "Overwrite existing data",
            "description": "Overwrite existing data options",
        },
        "existing_data_option_cancel": {
            "name": "Cancel import",
            "description": "Option of Cancel import",
        },
    },
    "JA_JP": {
        "title": {
            "name": "賞プール名をインポート",
            "description": "ExcelまたはCSVファイルから賞プール名をインポート",
        },
        "initial_subtitle": {
            "name": "インポート先：",
            "description": "賞プールにインポート中のプロンプト",
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
            "name": "賞プール情報を含む列を選択してください",
            "description": "列マッピングエリアの説明",
        },
        "column_mapping_id_column": {
            "name": "番号列（必須）:",
            "description": "番号列ラベル",
        },
        "column_mapping_name_column": {
            "name": "賞プール名列（必須）:",
            "description": "賞プール名列ラベル",
        },
        "column_mapping_weight_column": {
            "name": "重み列（オプション）:",
            "description": "重み列ラベル",
        },
        "column_mapping_count_column": {
            "name": "数量列（オプション）:",
            "description": "数量列ラベル",
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
        "prize_id": {"name": "番号", "description": "番号列タイトル"},
        "prize_name": {"name": "賞プール名", "description": "賞プール名列タイトル"},
        "weight": {"name": "重み", "description": "重み列タイトル"},
        "count": {"name": "数量", "description": "数量列タイトル"},
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
        "error_title": {"name": "エラー", "description": "エラーダイアログのタイトル"},
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
            "name": "賞プール名列を選択してください",
            "description": "賞プール名列が選択されていないエラー情報",
        },
        "no_id_column": {
            "name": "番号列を選択してください",
            "description": "番号列が選択されていないエラー情報",
        },
        "duplicate_names_title": {
            "name": "重複名が見つかりました",
            "description": "インポート時の重複名検出ダイアログのタイトル",
        },
        "duplicate_names_message": {
            "name": "{count}個の重複した賞プール名が検出されました：\n{names}\n\n編集に戻るか、重複項目を“_1/_2…”の形式で自動リネームしてください。",
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
            "name": "{count}個の賞プール情報を賞プール '{prize_name}' にインポートしました",
            "description": "インポート成功ダイアログの内容テンプレート",
        },
        "import_success_notification_title": {
            "name": "インポート成功",
            "description": "インポート成功通知のタイトル",
        },
        "import_success_notification_content_template": {
            "name": "{count}個の賞プール情報を賞プール '{prize_name}' にインポートしました",
            "description": "インポート成功通知の内容テンプレート",
        },
        "existing_data_title": {
            "name": "賞プールに既にデータが存在します",
            "description": "賞プールに既にデータが存在するダイアログのタイトル",
        },
        "existing_data_prompt": {
            "name": "賞プール '{prize_name}' は既に{count}個の賞プール情報を含んでいます、処理方法を選択してください：",
            "description": "賞プールに既にデータが存在するダイアログのヒントテキスト",
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

# 名称设置窗口
lottery_name_setting = {
    "ZH_CN": {
        "title": {"name": "奖品名称设置", "description": "设置奖品名称窗口标题"},
        "description": {
            "name": "在此窗口中，您可以设置奖品名称\n每行输入一个奖品名称，系统会将其存储到奖品名单文件中\n\n请每行只输入一个奖品名称，例如：\n一等奖\n二等奖\n三等奖",
            "description": "奖品名称设置窗口描述",
        },
        "input_title": {"name": "奖品名称列表", "description": "奖品名称输入区域标题"},
        "input_placeholder": {
            "name": "请输入奖品名称，每行一个奖品名称",
            "description": "奖品名称输入框占位符",
        },
        "save_button": {"name": "保存", "description": "保存按钮文本"},
        "cancel_button": {"name": "取消", "description": "取消按钮文本"},
        "error_title": {"name": "错误", "description": "错误消息标题"},
        "success_title": {"name": "成功", "description": "成功消息标题"},
        "info_title": {"name": "提示", "description": "信息消息标题"},
        "no_names_error": {
            "name": "请至少输入一个奖品名称",
            "description": "未输入奖品名称时的错误提示",
        },
        "invalid_names_error": {
            "name": "以下奖品名称包含非法字符或为保留字: {names}",
            "description": "奖品名称验证失败时的错误提示",
        },
        "duplicate_names_title": {
            "name": "发现重复名称",
            "description": "名称重复对话框标题",
        },
        "duplicate_names_message": {
            "name": "检测到 {count} 个重复的奖品名称：\n{names}\n\n请选择返回编辑，或自动将重复项重命名为“_1/_2…”格式。",
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
            "name": "保存奖品名称失败",
            "description": "保存奖品名称时的错误提示",
        },
        "success_message": {
            "name": "成功创建 {count} 个新奖品名称",
            "description": "成功创建奖品名称时的提示消息",
        },
        "no_new_names_message": {
            "name": "所有奖品名称均已存在，未创建新的奖品名称",
            "description": "没有创建新奖品名称时的提示消息",
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
        "delete_name_title": {
            "name": "删除奖品名称",
            "description": "删除奖品名称对话框标题",
        },
        "delete_name_message": {
            "name": "确定要删除名称 '{name}' 吗？此操作将删除该名称的所有信息，且不可恢复",
            "description": "删除奖品名称确认对话框内容",
        },
        "delete_multiple_names_title": {
            "name": "删除多个奖品名称",
            "description": "删除多个奖品名称对话框标题",
        },
        "delete_multiple_names_message": {
            "name": "确定要删除以下 {count} 个奖品名称吗？此操作将删除这些奖品名称的所有信息，且不可恢复\n\n{names}",
            "description": "删除多个名称确认对话框内容",
        },
        "delete_name_success_title": {
            "name": "删除成功",
            "description": "删除奖品名称成功通知标题",
        },
        "delete_name_success_message": {
            "name": "成功删除 {count} 个奖品名称",
            "description": "删除奖品名称成功通知内容",
        },
        "delete_name_cancel_button": {
            "name": "取消删除",
            "description": "取消删除奖品名称按钮文本",
        },
        "no_deletable_names": {
            "name": "没有可删除的奖品名称",
            "description": "没有可删除奖品名称时的提示",
        },
        "select_name_to_delete": {
            "name": "请选择要删除的奖品名称",
            "description": "选择删除奖品名称的提示",
        },
        "select_name_dialog_title": {
            "name": "选择要删除的奖品名称",
            "description": "选择删除奖品名称对话框标题",
        },
        "select_name_dialog_message": {
            "name": "请选择要删除的奖品名称：",
            "description": "选择删除奖品名称对话框内容",
        },
        "delete_selected_names_button": {
            "name": "删除选中",
            "description": "删除选中奖品名称按钮文本",
        },
        "delete_name_error": {
            "name": "删除奖品名称失败: {error}",
            "description": "删除奖品名称失败错误信息",
        },
        "name_deleted_title": {
            "name": "奖品名称已删除",
            "description": "删除奖品名称提示标题",
        },
        "name_deleted_message": {
            "name": "奖品名称 '{name}' 已从输入框中删除，请保存更改以永久删除",
            "description": "删除奖品名称提示内容",
        },
    },
    "EN_US": {
        "title": {
            "name": "Prize name settings",
            "description": "Set the title of the prize name window",
        },
        "description": {
            "name": "In this window, you can set the prize name\nto enter one prize name per line, and the system will store it in\n\nto enter only one prize name per line, e.g.:\nFirst prize\nSecond prize\nThird prize",
            "description": "Prize name setting window description",
        },
        "input_title": {
            "name": "List of prizes names",
            "description": "Enter the area title of the prize name",
        },
        "input_placeholder": {
            "name": "Please enter the prize name, one prize name per row",
            "description": "Prize Name Input Placeholder",
        },
        "save_button": {"name": "Save", "description": "Button text of Save"},
        "cancel_button": {"name": "Cancel", "description": "Button text of Cancel"},
        "error_title": {"name": "Error", "description": "Message title of Error"},
        "success_title": {"name": "Success", "description": "Message title of Success"},
        "info_title": {"name": "Prompt", "description": "Message title of Info"},
        "no_names_error": {
            "name": "Please enter at least one prize name",
            "description": "Incorrect reminder when the prize name is not entered",
        },
        "invalid_names_error": {
            "name": "The following prize names include invalid characters or reserved words: {names}",
            "description": "Error hint when the prize name validation failed",
        },
        "duplicate_names_title": {
            "name": "Duplicate names found",
            "description": "Dialog title when duplicate names are detected",
        },
        "duplicate_names_message": {
            "name": "Detected {count} duplicate prize names:\n{names}\n\nChoose to go back and edit, or automatically rename duplicates with “_1/_2…” suffix.",
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
            "name": "Failed to save prize name",
            "description": "Error hint when saving prize name",
        },
        "success_message": {
            "name": "Succeed creating {count} prize names",
            "description": "Notification message when prize name is created successfully",
        },
        "no_new_names_message": {
            "name": "All prize names already exist, no new prize names have been created",
            "description": "Notification message when no new prize name is created",
        },
        "unsaved_changes_title": {
            "name": "Unsaved changes",
            "description": "Change dialog title is not saved",
        },
        "unsaved_changes_message": {
            "name": "You have unsaved changes. Are you sure you want to close the window?",
            "description": "Change dialog content not saved",
        },
        "discard_button": {
            "name": "Discard changes",
            "description": "Discard Change Button Text",
        },
        "continue_editing_button": {
            "name": "Keep editing",
            "description": "Continue editing button text",
        },
        "delete_button": {"name": "Delete", "description": "Button text of Delete"},
        "delete_name_title": {
            "name": "Delete prize name",
            "description": "Remove Prize name dialog title",
        },
        "delete_name_message": {
            "name": "Are you sure to delete the name '{name}'? This will delete all information of this name and can NOT be restored",
            "description": "Delete prize name confirmation dialog",
        },
        "delete_multiple_names_title": {
            "name": "Delete multiple prize names",
            "description": "Delete multiple prize name dialog title",
        },
        "delete_multiple_names_message": {
            "name": "Are you sure to delete the following {count} prize names? This will delete all information of these prize names and can NOT be restored\n\n{names}",
            "description": "Delete multiple name confirmation dialog content",
        },
        "delete_name_success_title": {
            "name": "Delete success",
            "description": "Successfully deleted prize name notification title",
        },
        "delete_name_success_message": {
            "name": "Succeed deleting {count} prize names",
            "description": "Successfully deleted prize name",
        },
        "delete_name_cancel_button": {
            "name": "Cancel delete",
            "description": "Cancel prize name button text",
        },
        "no_deletable_names": {
            "name": "There are no prizes names to delete",
            "description": "Tips when no prize name can be deleted",
        },
        "select_name_to_delete": {
            "name": "Please select the name of the prize to delete",
            "description": "Tips to choose prize name to be deleted",
        },
        "select_name_dialog_title": {
            "name": "Select the name of the prize to delete",
            "description": "Dialog title of tips to choose prize name to be deleted",
        },
        "select_name_dialog_message": {
            "name": "Please select the prize name to delete：",
            "description": "Select item to delete the prize name dialog",
        },
        "delete_selected_names_button": {
            "name": "Delete selected",
            "description": "Delete selected prize name button text",
        },
        "delete_name_error": {
            "name": "Failed to delete prize name: {error}",
            "description": "Failed to delete prize name error",
        },
        "name_deleted_title": {
            "name": "Prize name deleted",
            "description": "Delete prize name tip title",
        },
        "name_deleted_message": {
            "name": "Detected that the prize '{name}' have been removed from the input box. Please save your changes to permanently delete it",
            "description": "Delete prize name hint",
        },
    },
    "JA_JP": {
        "title": {
            "name": "賞品名設定",
            "description": "賞品名ウィンドウのタイトルを設定",
        },
        "description": {
            "name": "このウィンドウで賞品名を設定できます\n1行に1つの賞品名を入力すると、システムは賞品名簿ファイルに保存します\n\n1行に1つの賞品名のみを入力してください。例：\n一等賞\n二等賞\n三等賞",
            "description": "賞品名設定ウィンドウの説明",
        },
        "input_title": {
            "name": "賞品名リスト",
            "description": "賞品名入力エリアのタイトル",
        },
        "input_placeholder": {
            "name": "賞品名を入力してください、1行に1つの賞品名",
            "description": "賞品名入力ボックスのプレースホルダー",
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
            "name": "少なくとも1つの賞品名を入力してください",
            "description": "賞品名が入力されていない場合のエラーヒント",
        },
        "invalid_names_error": {
            "name": "以下の賞品名に不正な文字または予約語が含まれています: {names}",
            "description": "賞品名検証失敗時のエラーヒント",
        },
        "duplicate_names_title": {
            "name": "重複名が見つかりました",
            "description": "重複名検出ダイアログのタイトル",
        },
        "duplicate_names_message": {
            "name": "{count}個の重複した賞品名が検出されました：\n{names}\n\n編集に戻るか、重複項目を“_1/_2…”の形式で自動リネームしてください。",
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
            "name": "賞品名の保存に失敗しました",
            "description": "賞品名保存時のエラーヒント",
        },
        "success_message": {
            "name": "{count}個の新しい賞品名を作成しました",
            "description": "賞品名作成成功時のプロンプトメッセージ",
        },
        "no_new_names_message": {
            "name": "すべての賞品名が既に存在するため、新しい賞品名は作成されませんでした",
            "description": "新しい賞品名が作成されなかった場合のプロンプトメッセージ",
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
            "name": "賞品名を削除",
            "description": "賞品名削除ダイアログのタイトル",
        },
        "delete_name_message": {
            "name": "賞品名 '{name}' を削除しますか？この操作はこの賞品名のすべての情報を削除し、復元できません",
            "description": "賞品名削除確認ダイアログの内容",
        },
        "delete_multiple_names_title": {
            "name": "複数の賞品名を削除",
            "description": "複数の賞品名削除ダイアログのタイトル",
        },
        "delete_multiple_names_message": {
            "name": "以下の{count}個の賞品名を削除しますか？この操作はこれらの賞品名のすべての情報を削除し、復元できません\n\n{names}",
            "description": "複数の賞品名削除確認ダイアログの内容",
        },
        "delete_name_success_title": {
            "name": "削除成功",
            "description": "賞品名削除成功通知のタイトル",
        },
        "delete_name_success_message": {
            "name": "{count}個の賞品名を削除しました",
            "description": "賞品名削除成功通知の内容",
        },
        "delete_name_cancel_button": {
            "name": "削除をキャンセル",
            "description": "賞品名削除キャンセルボタンのテキスト",
        },
        "no_deletable_names": {
            "name": "削除可能な賞品名がありません",
            "description": "削除可能な賞品名がない場合のヒント",
        },
        "select_name_to_delete": {
            "name": "削除する賞品名を選択してください",
            "description": "削除賞品名選択のヒント",
        },
        "select_name_dialog_title": {
            "name": "削除する賞品名を選択",
            "description": "削除賞品名選択ダイアログのタイトル",
        },
        "select_name_dialog_message": {
            "name": "削除する賞品名を選択してください：",
            "description": "削除賞品名選択ダイアログの内容",
        },
        "delete_selected_names_button": {
            "name": "選択を削除",
            "description": "選択削除ボタンのテキスト",
        },
        "delete_name_error": {
            "name": "賞品名の削除に失敗しました: {error}",
            "description": "賞品名削除失敗エラー情報",
        },
        "name_deleted_title": {
            "name": "賞品名が削除されました",
            "description": "賞品名削除ヒントのタイトル",
        },
        "name_deleted_message": {
            "name": "賞品名 '{name}' が入力ボックスから削除されたことが検出されました。変更を保存して永久に削除してください",
            "description": "賞品名削除ヒントの内容",
        },
    },
}

# 权重设置窗口
weight_setting = {
    "ZH_CN": {
        "title": {"name": "权重设置", "description": "设置权重窗口标题"},
        "description": {
            "name": "在此窗口中，您可以设置奖品的权重\n每行输入一个权重值，系统会将其存储到奖品名单文件中\n\n请每行只输入一个权重值，例如：\n10\n20\n30",
            "description": "权重设置窗口描述",
        },
        "input_title": {"name": "权重列表", "description": "权重输入区域标题"},
        "input_placeholder": {
            "name": "请输入权重，每行一个权重",
            "description": "权重输入框占位符",
        },
        "save_button": {"name": "保存", "description": "保存按钮文本"},
        "cancel_button": {"name": "取消", "description": "取消按钮文本"},
        "error_title": {"name": "错误", "description": "错误消息标题"},
        "success_title": {"name": "成功", "description": "成功消息标题"},
        "info_title": {"name": "提示", "description": "信息消息标题"},
        "no_genders_error": {
            "name": "请至少输入一个权重值",
            "description": "未输入权重时的错误提示",
        },
        "invalid_weights_error": {
            "name": "以下权重包含非法字符或为保留字: {weights}",
            "description": "权重验证失败时的错误提示",
        },
        "save_error": {
            "name": "保存权重选项失败",
            "description": "保存权重选项时的错误提示",
        },
        "success_message": {
            "name": "成功创建 {count} 个新权重选项",
            "description": "成功创建权重选项时的提示消息",
        },
        "no_new_weights_message": {
            "name": "所有权重选项均已存在，未创建新的权重选项",
            "description": "没有创建新权重选项时的提示消息",
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
        "delete_weight_title": {
            "name": "删除权重选项",
            "description": "删除权重选项对话框标题",
        },
        "delete_weight_message": {
            "name": "确定要删除权重选项 '{weight}' 吗？此操作将删除该权重选项的所有信息，且不可恢复",
            "description": "删除权重选项确认对话框内容",
        },
        "delete_multiple_weights_title": {
            "name": "删除多个权重选项",
            "description": "删除多个权重选项对话框标题",
        },
        "delete_multiple_weights_message": {
            "name": "确定要删除以下 {count} 个权重选项吗？此操作将删除这些权重选项的所有信息，且不可恢复\n\n{weights}",
            "description": "删除多个权重选项确认对话框内容",
        },
        "delete_weight_success_title": {
            "name": "删除成功",
            "description": "删除权重选项成功通知标题",
        },
        "delete_weight_success_message": {
            "name": "成功删除 {count} 个权重选项",
            "description": "删除权重选项成功通知内容",
        },
        "delete_weight_cancel_button": {
            "name": "取消删除",
            "description": "取消删除权重选项按钮文本",
        },
        "no_deletable_weights": {
            "name": "没有可删除的权重选项",
            "description": "没有可删除权重选项时的提示",
        },
        "select_weight_to_delete": {
            "name": "请选择要删除的权重选项",
            "description": "选择删除权重选项的提示",
        },
        "select_weight_dialog_title": {
            "name": "选择要删除的权重选项",
            "description": "选择删除权重选项对话框标题",
        },
        "select_weight_dialog_message": {
            "name": "请选择要删除的权重选项：",
            "description": "选择删除权重选项对话框内容",
        },
        "delete_selected_weights_button": {
            "name": "删除选中",
            "description": "删除选中权重选项按钮文本",
        },
        "delete_weight_error": {
            "name": "删除权重选项失败: {error}",
            "description": "删除权重选项失败错误信息",
        },
        "weight_deleted_title": {
            "name": "权重选项已删除",
            "description": "删除权重选项提示标题",
        },
        "weight_deleted_message": {
            "name": "权重选项 '{weight}' 已从输入框中移除，请保存更改以永久删除",
            "description": "删除权重选项提示内容",
        },
    },
    "EN_US": {
        "title": {
            "name": "Weight settings",
            "description": "Set the title of the replay window",
        },
        "description": {
            "name": "In this window, you can set the weight of the prize\nto enter a weight per line, and the system will store it in\n\nPlease enter only one weight per line, e.g.:\n10\n20\n30",
            "description": "Reset window description",
        },
        "input_title": {
            "name": "Weight list",
            "description": "Weight input area title",
        },
        "input_placeholder": {
            "name": "Please enter weight, one weight per row",
            "description": "Weight input box placeholder",
        },
        "save_button": {"name": "Save", "description": "Button text of Save"},
        "cancel_button": {"name": "Cancel", "description": "Button text of Cancel"},
        "error_title": {"name": "Error", "description": "Message title of Error"},
        "success_title": {"name": "Success", "description": "Message title of Success"},
        "info_title": {"name": "Prompt", "description": "Message title of Info"},
        "no_genders_error": {
            "name": "Please enter at least one weight value",
            "description": "Error hint when no weight entered",
        },
        "invalid_weights_error": {
            "name": "The following weights include invalid characters or reserved words: {weights}",
            "description": "Error reminders when reauthenticating failed",
        },
        "save_error": {
            "name": "Failed to save weights",
            "description": "Error hint when saving weights",
        },
        "success_message": {
            "name": "Succeed creating {count} weight options",
            "description": "Notification message when weighting is created successfully",
        },
        "no_new_weights_message": {
            "name": "All weight options already exist, no new weight options have been created",
            "description": "Tips when not created new weights",
        },
        "unsaved_changes_title": {
            "name": "Unsaved changes",
            "description": "Change dialog title is not saved",
        },
        "unsaved_changes_message": {
            "name": "You have unsaved changes. Are you sure you want to close the window?",
            "description": "Change dialog content not saved",
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
        "delete_weight_title": {
            "name": "Delete weight options",
            "description": "Remove option dialog title",
        },
        "delete_weight_message": {
            "name": "Are you sure to delete the weight option '{weight}'? This will delete all information of this weight option and can NOT be restored",
            "description": "Delete permission to select confirmation dialog",
        },
        "delete_multiple_weights_title": {
            "name": "Delete multiple weight options",
            "description": "Delete multiple weight dialog titles",
        },
        "delete_multiple_weights_message": {
            "name": "Are you sure to delete the following {count} weight options? This will delete all information of these weight options and can NOT be restored\n\n{weights}",
            "description": "Delete multiple weight options confirmation dialog content",
        },
        "delete_weight_success_title": {
            "name": "Delete success",
            "description": "Successfully deleted priority option notification title",
        },
        "delete_weight_success_message": {
            "name": "Succeed deleting {count} weight options",
            "description": "Notification of Delete the permission weight option successfully",
        },
        "delete_weight_cancel_button": {
            "name": "Cancel delete",
            "description": "Undelete weight button text",
        },
        "no_deletable_weights": {
            "name": "There are no weight options to delete",
            "description": "There are no tips to delete the weights",
        },
        "select_weight_to_delete": {
            "name": "Please select the weight option to delete",
            "description": "Select a notification to delete the weight option",
        },
        "select_weight_dialog_title": {
            "name": "Select the weight option to delete",
            "description": "Select the title of the weight option dialog to delete",
        },
        "select_weight_dialog_message": {
            "name": "Please select the weight option to delete：",
            "description": "Select what to delete the weight option dialog",
        },
        "delete_selected_weights_button": {
            "name": "Delete selected",
            "description": "Delete selected weights button text",
        },
        "delete_weight_error": {
            "name": "Failed to delete weight option: {error}",
            "description": "Failed to delete weight option error",
        },
        "weight_deleted_title": {
            "name": "The weight option has been deleted",
            "description": "Remove the weighted option tip header",
        },
        "weight_deleted_message": {
            "name": "Detected that the weight option '{weight}' have been removed from the input box. Please save your changes to permanently delete it",
            "description": "Remove the weight selection tips",
        },
    },
    "JA_JP": {
        "title": {
            "name": "重み設定",
            "description": "重みウィンドウのタイトルを設定",
        },
        "description": {
            "name": "このウィンドウで賞品の重みを設定できます\n1行に1つの重みを入力すると、システムは賞品名簿ファイルに保存します\n\n1行に1つの重みのみを入力してください。例：\n10\n20\n30",
            "description": "重み設定ウィンドウの説明",
        },
        "input_title": {
            "name": "重みリスト",
            "description": "重み入力エリアのタイトル",
        },
        "input_placeholder": {
            "name": "重みを入力してください、1行に1つの重み",
            "description": "重み入力ボックスのプレースホルダー",
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
            "name": "少なくとも1つの重みを入力してください",
            "description": "重みが入力されていない場合のエラーヒント",
        },
        "invalid_weights_error": {
            "name": "以下の重みに不正な文字または予約語が含まれています: {weights}",
            "description": "重み検証失敗時のエラーヒント",
        },
        "save_error": {
            "name": "重みオプションの保存に失敗しました",
            "description": "重みオプション保存時のエラーヒント",
        },
        "success_message": {
            "name": "{count}個の新しい重みオプションを作成しました",
            "description": "重みオプション作成成功時のプロンプトメッセージ",
        },
        "no_new_weights_message": {
            "name": "すべての重みオプションが既に存在するため、新しい重みオプションは作成されませんでした",
            "description": "新しい重みオプションが作成されなかった場合のプロンプトメッセージ",
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
        "delete_weight_title": {
            "name": "重みオプションを削除",
            "description": "重みオプション削除ダイアログのタイトル",
        },
        "delete_weight_message": {
            "name": "重みオプション '{weight}' を削除しますか？この操作はこの重みオプションのすべての情報を削除し、復元できません",
            "description": "重みオプション削除確認ダイアログの内容",
        },
        "delete_multiple_weights_title": {
            "name": "複数の重みオプションを削除",
            "description": "複数の重みオプション削除ダイアログのタイトル",
        },
        "delete_multiple_weights_message": {
            "name": "以下の{count}個の重みオプションを削除しますか？この操作はこれらの重みオプションのすべての情報を削除し、復元できません\n\n{weights}",
            "description": "複数の重みオプション削除確認ダイアログの内容",
        },
        "delete_weight_success_title": {
            "name": "削除成功",
            "description": "重みオプション削除成功通知のタイトル",
        },
        "delete_weight_success_message": {
            "name": "{count}個の重みオプションを削除しました",
            "description": "重みオプション削除成功通知の内容",
        },
        "delete_weight_cancel_button": {
            "name": "削除をキャンセル",
            "description": "重みオプション削除キャンセルボタンのテキスト",
        },
        "no_deletable_weights": {
            "name": "削除可能な重みオプションがありません",
            "description": "削除可能な重みオプションがない場合のヒント",
        },
        "select_weight_to_delete": {
            "name": "削除する重みオプションを選択してください",
            "description": "削除重みオプション選択のヒント",
        },
        "select_weight_dialog_title": {
            "name": "削除する重みオプションを選択",
            "description": "削除重みオプション選択ダイアログのタイトル",
        },
        "select_weight_dialog_message": {
            "name": "削除する重みオプションを選択してください：",
            "description": "削除重みオプション選択ダイアログの内容",
        },
        "delete_selected_weights_button": {
            "name": "選択を削除",
            "description": "選択削除ボタンのテキスト",
        },
        "delete_weight_error": {
            "name": "重みオプションの削除に失敗しました: {error}",
            "description": "重みオプション削除失敗エラー情報",
        },
        "weight_deleted_title": {
            "name": "重みオプションが削除されました",
            "description": "重みオプション削除ヒントのタイトル",
        },
        "weight_deleted_message": {
            "name": "重みオプション '{weight}' が入力ボックスから削除されたことが検出されました。変更を保存して永久に削除してください",
            "description": "重みオプション削除ヒントの内容",
        },
    },
}

# 数量设置窗口
count_setting = {
    "ZH_CN": {
        "title": {"name": "数量设置", "description": "设置数量窗口标题"},
        "description": {
            "name": "在此窗口中，您可以设置奖品的数量\n每行输入一个数量值，系统会将其存储到奖品名单文件中\n\n请每行只输入一个数量值，例如：\n1\n2\n3",
            "description": "数量设置窗口描述",
        },
        "input_title": {"name": "数量列表", "description": "数量输入区域标题"},
        "input_placeholder": {
            "name": "请输入数量，每行一个数量",
            "description": "数量输入框占位符",
        },
        "save_button": {"name": "保存", "description": "保存按钮文本"},
        "cancel_button": {"name": "取消", "description": "取消按钮文本"},
        "error_title": {"name": "错误", "description": "错误消息标题"},
        "success_title": {"name": "成功", "description": "成功消息标题"},
        "info_title": {"name": "提示", "description": "信息消息标题"},
        "no_counts_error": {
            "name": "请至少输入一个数量值",
            "description": "未输入数量时的错误提示",
        },
        "invalid_counts_error": {
            "name": "以下数量包含非法字符或无法解析: {counts}",
            "description": "数量输入校验失败提示",
        },
        "save_error": {"name": "保存数量失败", "description": "保存数量失败提示"},
        "success_message": {
            "name": "成功创建 {count} 个数量选项",
            "description": "数量创建成功提示",
        },
        "no_new_counts_message": {
            "name": "所有数量选项已存在，未创建新的数量选项",
            "description": "未创建新数量提示",
        },
        "unsaved_changes_title": {
            "name": "未保存的更改",
            "description": "未保存更改标题",
        },
        "unsaved_changes_message": {
            "name": "您有未保存的更改。确定要关闭窗口吗？",
            "description": "未保存更改提示内容",
        },
        "discard_button": {"name": "放弃更改", "description": "放弃更改按钮文本"},
        "continue_editing_button": {
            "name": "继续编辑",
            "description": "继续编辑按钮文本",
        },
        "count_deleted_title": {
            "name": "数量选项已删除",
            "description": "删除数量提示标题",
        },
        "count_deleted_message": {
            "name": "数量选项 '{count}' 已从输入框中移除，请保存更改以永久删除",
            "description": "删除数量提示内容",
        },
    },
    "EN_US": {
        "title": {"name": "Count settings", "description": "Set count window title"},
        "description": {
            "name": "In this window, you can set the count of prizes\nEnter one count per line, and the system will store it in the prize list file\n\nPlease enter only one count per line, e.g.:\n1\n2\n3",
            "description": "Count settings window description",
        },
        "input_title": {"name": "Count list", "description": "Count input area title"},
        "input_placeholder": {
            "name": "Please enter count, one per row",
            "description": "Count input placeholder",
        },
        "save_button": {"name": "Save", "description": "Button text of Save"},
        "cancel_button": {"name": "Cancel", "description": "Button text of Cancel"},
        "error_title": {"name": "Error", "description": "Message title of Error"},
        "success_title": {"name": "Success", "description": "Message title of Success"},
        "info_title": {"name": "Prompt", "description": "Message title of Info"},
        "no_counts_error": {
            "name": "Please enter at least one count value",
            "description": "Error hint when no count entered",
        },
        "invalid_counts_error": {
            "name": "The following counts include invalid characters or can not be parsed: {counts}",
            "description": "Error hint when count validation failed",
        },
        "save_error": {
            "name": "Failed to save counts",
            "description": "Save error hint",
        },
        "success_message": {
            "name": "Succeed creating {count} count options",
            "description": "Success message of count creation",
        },
        "no_new_counts_message": {
            "name": "All count options already exist, no new count options have been created",
            "description": "Tips when not created new counts",
        },
        "unsaved_changes_title": {
            "name": "Unsaved changes",
            "description": "Unsaved change dialog title",
        },
        "unsaved_changes_message": {
            "name": "You have unsaved changes. Are you sure you want to close the window?",
            "description": "Unsaved change dialog content",
        },
        "discard_button": {"name": "Discard changes", "description": "Discard button"},
        "continue_editing_button": {
            "name": "Keep editing",
            "description": "Continue button",
        },
        "count_deleted_title": {
            "name": "Count option deleted",
            "description": "Deleted count option title",
        },
        "count_deleted_message": {
            "name": "Detected that the count option '{count}' have been removed from the input box. Please save your changes to permanently delete it",
            "description": "Deleted count option content",
        },
    },
    "JA_JP": {
        "title": {"name": "数量設定", "description": "数量ウィンドウのタイトルを設定"},
        "description": {
            "name": "このウィンドウで賞品の数量を設定できます\n1行に1つの数量を入力すると、システムは賞品名簿ファイルに保存します\n\n1行に1つの数量のみを入力してください。例：\n1\n2\n3",
            "description": "数量設定ウィンドウの説明",
        },
        "input_title": {
            "name": "数量リスト",
            "description": "数量入力エリアのタイトル",
        },
        "input_placeholder": {
            "name": "数量を入力してください、1行に1つの数量",
            "description": "数量入力ボックスのプレースホルダー",
        },
        "save_button": {"name": "保存", "description": "保存ボタンのテキスト"},
        "cancel_button": {
            "name": "キャンセル",
            "description": "キャンセルボタンのテキスト",
        },
        "error_title": {"name": "エラー", "description": "エラーメッセージのタイトル"},
        "success_title": {"name": "成功", "description": "成功メッセージのタイトル"},
        "info_title": {"name": "プロンプト", "description": "情報メッセージのタイトル"},
        "no_counts_error": {
            "name": "少なくとも1つの数量を入力してください",
            "description": "数量が入力されていない場合のエラーヒント",
        },
        "invalid_counts_error": {
            "name": "以下の数量に不正な文字が含まれているか、解析できません: {counts}",
            "description": "数量検証失敗時のエラーヒント",
        },
        "save_error": {
            "name": "数量の保存に失敗しました",
            "description": "数量保存時のエラーヒント",
        },
        "success_message": {
            "name": "{count}個の新しい数量オプションを作成しました",
            "description": "数量作成成功時のメッセージ",
        },
        "no_new_counts_message": {
            "name": "すべての数量オプションが既に存在するため、新しい数量オプションは作成されませんでした",
            "description": "新しい数量が作成されなかった場合のメッセージ",
        },
        "unsaved_changes_title": {
            "name": "未保存の変更",
            "description": "未保存変更ダイアログのタイトル",
        },
        "unsaved_changes_message": {
            "name": "未保存の変更があります。ウィンドウを閉じますか？",
            "description": "未保存変更ダイアログの内容",
        },
        "discard_button": {"name": "変更を破棄", "description": "破棄ボタンのテキスト"},
        "continue_editing_button": {
            "name": "編集を続ける",
            "description": "継続ボタンのテキスト",
        },
        "count_deleted_title": {
            "name": "数量が削除されました",
            "description": "数量削除ヒントのタイトル",
        },
        "count_deleted_message": {
            "name": "数量 '{count}' が入力ボックスから削除されたことが検出されました。変更を保存して永久に削除してください",
            "description": "数量削除ヒントの内容",
        },
    },
}

# 奖品标签设置窗口
prize_tag_setting = {
    "ZH_CN": {
        "title": {"name": "标签设置", "description": "奖品标签设置窗口标题"},
        "description": {
            "name": "在此窗口中，您可以为奖品设置标签\n双击“标签”列进行编辑，多个标签可用空格或逗号分隔",
            "description": "奖品标签设置窗口描述",
        },
        "header_labels": {
            "name": ["序号", "奖品", "标签"],
            "description": "表格表头",
        },
        "save_button": {"name": "保存", "description": "保存按钮文本"},
        "error_title": {"name": "错误", "description": "错误消息标题"},
        "success_title": {"name": "成功", "description": "成功消息标题"},
        "no_list_selected": {
            "name": "请先选择奖池",
            "description": "未选择奖池提示",
        },
        "list_file_missing": {
            "name": "奖池名单文件不存在",
            "description": "名单文件不存在提示",
        },
        "success_message": {"name": "标签已保存", "description": "保存成功提示"},
        "save_error": {"name": "保存标签失败", "description": "保存失败前缀"},
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
        "title": {"name": "Tag settings", "description": "Prize tag settings title"},
        "description": {
            "name": "Edit prize tags in this window\nDouble click the “Tags” column to edit. Separate multiple tags with spaces or commas",
            "description": "Prize tag settings description",
        },
        "header_labels": {
            "name": ["ID", "Prize", "Tags"],
            "description": "Table headers",
        },
        "save_button": {"name": "Save", "description": "Save button text"},
        "error_title": {"name": "Error", "description": "Error title"},
        "success_title": {"name": "Success", "description": "Success title"},
        "no_list_selected": {
            "name": "Please select a pool first",
            "description": "No pool selected hint",
        },
        "list_file_missing": {
            "name": "Pool list file not found",
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
            "description": "賞品タグ設定ウィンドウのタイトル",
        },
        "description": {
            "name": "このウィンドウでは賞品のタグを設定できます\n「タグ」列をダブルクリックして編集し、複数のタグは空白またはカンマで区切ります",
            "description": "賞品タグ設定ウィンドウの説明",
        },
        "header_labels": {
            "name": ["ID", "賞品", "タグ"],
            "description": "テーブルヘッダー",
        },
        "save_button": {"name": "保存", "description": "保存ボタンのテキスト"},
        "error_title": {"name": "エラー", "description": "エラータイトル"},
        "success_title": {"name": "成功", "description": "成功タイトル"},
        "no_list_selected": {
            "name": "先に賞プールを選択してください",
            "description": "賞プール未選択のヒント",
        },
        "list_file_missing": {
            "name": "賞プールリストファイルが見つかりません",
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
