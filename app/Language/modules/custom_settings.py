# 个性设置页面的语言文件
custom_settings = {
    "ZH_CN": {"title": {"name": "个性设置", "description": "个性化设置选项"}},
    "EN_US": {
        "title": {
            "name": "Personal Settings",
            "description": "Personalized Settings Options",
        }
    },
    "JA_JP": {
        "title": {
            "name": "パーソナル設定",
            "description": "パーソナライズ設定オプション",
        }
    },
}

# 页面管理语言配置
page_management = {
    "ZH_CN": {
        "title": {"name": "页面管理", "description": "页面管理设置选项"},
        "roll_call": {"name": "点名设置", "description": "点名功能设置"},
        "lottery": {"name": "抽奖设置", "description": "抽奖功能设置"},
        "roll_call_method": {
            "name": "点名控制面板位置",
            "description": "设置点名控制面板显示位置",
            "combo_items": ["左侧", "右侧"],
        },
        "roll_call_reset_button": {
            "name": "重置点名按钮",
            "description": "开启后显示重置点名按钮",
            "switchbutton_name": {"enable": "", "disable": ""},
        },
        "roll_call_quantity_control": {
            "name": "抽取数量控制条",
            "description": "控制是否显示抽取数量调整控件",
            "switchbutton_name": {"enable": "", "disable": ""},
        },
        "roll_call_start_button": {
            "name": "开始按钮",
            "description": "控制是否显示点名开始按钮",
            "switchbutton_name": {"enable": "", "disable": ""},
        },
        "roll_call_list": {
            "name": "点名名单切换下拉框",
            "description": "控制是否显示点名名单切换框",
            "switchbutton_name": {"enable": "", "disable": ""},
        },
        "roll_call_range": {
            "name": "点名范围下拉框",
            "description": "控制是否显示点名范围选择框",
            "switchbutton_name": {"enable": "", "disable": ""},
        },
        "roll_call_gender": {
            "name": "点名性别范围下拉框",
            "description": "控制是否显示点名性别范围选择框",
            "switchbutton_name": {"enable": "", "disable": ""},
        },
        "roll_call_quantity_label": {
            "name": "数量标签",
            "description": "设置抽取人数/组数标签的显示方式",
            "combo_items": ["总人/组数+剩余人数", "总人/组数", "剩余人/组数", "不显示"],
        },
        "roll_call_remaining_button": {
            "name": "查看剩余名单按钮",
            "description": "控制是否显示查看剩余名单按钮",
            "switchbutton_name": {"enable": "", "disable": ""},
        },
        "lottery_method": {
            "name": "抽奖控制面板位置",
            "description": "设置抽奖控制面板显示位置",
            "combo_items": ["左侧", "右侧"],
        },
        "lottery_reset_button": {
            "name": "重置抽奖按钮",
            "description": "控制是否显示抽奖重置按钮",
            "switchbutton_name": {"enable": "", "disable": ""},
        },
        "lottery_quantity_control": {
            "name": "抽取数量控制条",
            "description": "控制是否显示抽奖数量调整控件",
            "switchbutton_name": {"enable": "", "disable": ""},
        },
        "lottery_start_button": {
            "name": "开始按钮",
            "description": "控制是否显示抽奖开始按钮",
            "switchbutton_name": {"enable": "", "disable": ""},
        },
        "lottery_list": {
            "name": "抽奖名单切换下拉框",
            "description": "控制是否显示抽奖名单切换框",
            "switchbutton_name": {"enable": "", "disable": ""},
        },
        "lottery_roll_call_list": {
            "name": "抽奖中的学生名单切换下拉框",
            "description": "控制是否显示抽奖中的学生名单切换框",
            "switchbutton_name": {"enable": "", "disable": ""},
        },
        "lottery_roll_call_range": {
            "name": "抽奖中的学生点名范围下拉框",
            "description": "控制是否显示抽奖中的学生点名范围选择框",
            "switchbutton_name": {"enable": "", "disable": ""},
        },
        "lottery_roll_call_gender": {
            "name": "抽奖中的学生点名性别范围下拉框",
            "description": "控制是否显示抽奖中的学生点名性别范围选择框",
            "switchbutton_name": {"enable": "", "disable": ""},
        },
        "lottery_quantity_label": {
            "name": "数量标签",
            "description": "设置中奖数量标签的显示方式",
            "combo_items": ["总奖数+剩余奖数", "总奖数", "剩余奖数", "不显示"],
        },
        "lottery_remaining_button": {
            "name": "查看剩余名单按钮",
            "description": "控制是否显示查看剩余名单按钮",
            "switchbutton_name": {"enable": "", "disable": ""},
        },
    },
    "EN_US": {
        "title": {"name": "Page management", "description": "Page management settings"},
        "roll_call": {"name": "Pick settings", "description": "Pick function settings"},
        "lottery": {
            "name": "Lottery settings",
            "description": "Lottery function settings",
        },
        "custom": {
            "name": "Custom pick settings",
            "description": "Custom pick function settings",
        },
        "roll_call_method": {
            "name": "Picking control panel position",
            "description": "Set the location of the picking control panel",
            "combo_items": {"0": "Left", "1": "Right"},
        },
        "show_name": {
            "name": "Name setting button",
            "description": "When enabled, the software will display the name setting button",
            "switchbutton_name": {"enable": "Show", "disable": "Hide"},
        },
        "reset_roll_call": {
            "name": "Picking reset button",
            "description": "When enabled, the software will display the picking reset button",
            "switchbutton_name": {"enable": "Show", "disable": "Hide"},
        },
        "roll_call_quantity_control": {
            "name": "Control bar of Picking quantity",
            "description": "Control whether to display the control bar that adjusts the picking count",
        },
        "roll_call_start_button": {
            "name": "Start button",
            "description": "Control whether to display a button to start the name",
        },
        "roll_call_list": {
            "name": "Name list switching down",
            "description": "Control whether to display a name list switching down",
        },
        "roll_call_range": {
            "name": "Dropdown box of Picking range",
            "description": "Controls whether to display the name range selection dropdown",
        },
        "roll_call_gender": {
            "name": "Dropdown box of picking gender range",
            "description": "Control if you want to display the name gender range selection dropdown",
        },
        "roll_call_quantity_label": {
            "name": "Quantity label",
            "description": "Set the display mode of picked numbers/groups label",
            "combo_items": ["Total+Remaining", "Total", "Remaining", "Hidden"],
        },
        "roll_call_remaining_button": {
            "name": "View remaining list button",
            "description": "Control whether to display a button to view the remaining list",
        },
        "lottery_method": {
            "name": "Lottery control panel position",
            "description": "Set the location of the lottery control panel",
            "combo_items": {"0": "Left", "1": "Right"},
        },
        "show_lottery_name": {
            "name": "Name set button",
            "description": "Control whether to display the prize name setting button",
            "switchbutton_name": {"enable": "Show", "disable": "Hide"},
        },
        "reset_lottery": {
            "name": "Reset lottery button",
            "description": "Control whether to display the lottery resetting button",
            "switchbutton_name": {"enable": "Show", "disable": "Hide"},
        },
        "lottery_quantity_control": {
            "name": "Control bar of Picking quantity",
            "description": "Control whether to display the control bar that adjusts the number of lottery",
        },
        "lottery_start_button": {
            "name": "Start button",
            "description": "Control whether to display a button to start the lottery",
        },
        "lottery_list": {
            "name": "Lottery list switching down",
            "description": "Control whether to display a lottery list switching down",
        },
        "lottery_quantity_label": {
            "name": "Quantity label",
            "description": "Set the display mode of the number of prizes",
            "combo_items": ["Total+Remaining", "Total", "Remaining", "Hidden"],
        },
        "lottery_remaining_button": {
            "name": "View remaining list button",
            "description": "Control whether to display a button to view the remaining list",
        },
        "custom_method": {
            "name": "Custom pick control panel position",
            "description": "Set the custom pick control panel display position",
            "combo_items": {"0": "Left", "1": "Right"},
        },
        "reset_custom": {
            "name": "Reset custom pick button",
            "description": "Control whether to display the custom pick resetting button",
            "switchbutton_name": {"enable": "Show", "disable": "Hide"},
        },
        "custom_quantity_control": {
            "name": "Control bar of Picking quantity",
            "description": "Control whether to display the control bar that adjusts the custom picking count",
        },
        "custom_start_button": {
            "name": "Start button",
            "description": "Control whether to display the custom pick starting button",
        },
        "custom_list": {
            "name": "Custom picking list switching down",
            "description": "Control whether to display a custom picking list switching down",
        },
        "custom_range_start": {
            "name": "Custom pick dropdown box",
            "description": "Control whether to display custom extraction range selection box",
        },
        "custom_range_end": {
            "name": "Custom pick gender range dropdown box",
            "description": "Control whether to display custom pick gender range selection box",
        },
        "draw_custom_method": {
            "name": "Custom pick control panel position",
            "description": "Control whether to display custom pick control panel position",
        },
        "custom_quantity_label": {
            "name": "Quantity label",
            "description": "Control whether to display custom pick numbers/groups label",
        },
        "custom_remaining_button": {
            "name": "View remaining list button",
            "description": "Control whether to display a button to view the remaining list",
        },
        "roll_call_reset_button": {
            "name": "Reset picking button",
            "description": "Show reset name buttons when enabled",
        },
        "lottery_reset_button": {
            "name": "Reset lottery button",
            "description": "Control whether to display the lottery reset button",
        },
        "lottery_roll_call_list": {
            "name": "List of students in the prize switches drop-down",
            "description": "Control whether to display the student list switching box in lottery",
        },
        "lottery_roll_call_range": {
            "name": "Pick up frame for student range in lottery",
            "description": "Controls whether to display student name selection box in lottery",
        },
        "lottery_roll_call_gender": {
            "name": "Dropdown box of Gender range in Lottery",
            "description": "Controls whether to show a gender naming box for students in lottery",
        },
    },
    "JA_JP": {
        "title": {"name": "ページ管理", "description": "ページ管理設定オプション"},
        "roll_call": {"name": "点呼設定", "description": "点呼機能設定"},
        "lottery": {"name": "抽選設定", "description": "抽選機能設定"},
        "custom": {
            "name": "カスタム抽選設定",
            "description": "カスタム抽選機能設定",
        },
        "roll_call_method": {
            "name": "点呼コントロールパネル位置",
            "description": "点呼コントロールパネルの表示位置を設定",
            "combo_items": {"0": "左", "1": "右"},
        },
        "show_name": {
            "name": "名前設定ボタン",
            "description": "有効にすると、名前設定ボタンが表示されます",
            "switchbutton_name": {"enable": "表示", "disable": "非表示"},
        },
        "reset_roll_call": {
            "name": "点呼リセットボタン",
            "description": "有効にすると、点呼リセットボタンが表示されます",
            "switchbutton_name": {"enable": "表示", "disable": "非表示"},
        },
        "roll_call_quantity_control": {
            "name": "点呼数量コントロールバー",
            "description": "点呼数量調整コントロールバーの表示を制御",
        },
        "roll_call_start_button": {
            "name": "開始ボタン",
            "description": "点呼開始ボタンの表示を制御",
        },
        "roll_call_list": {
            "name": "点呼リスト切り替えドロップダウン",
            "description": "点呼リスト切り替えドロップダウンの表示を制御",
        },
        "roll_call_range": {
            "name": "点呼範囲ドロップダウン",
            "description": "点呼範囲選択ドロップダウンの表示を制御",
        },
        "roll_call_gender": {
            "name": "点呼性別範囲ドロップダウン",
            "description": "点呼性別範囲選択ドロップダウンの表示を制御",
        },
        "roll_call_quantity_label": {
            "name": "数量ラベル",
            "description": "点呼人数/グループ数ラベルの表示モードを設定",
            "combo_items": {"0": "総数+残数", "1": "総数", "2": "残数", "3": "非表示"},
        },
        "roll_call_remaining_button": {
            "name": "残りリスト表示ボタン",
            "description": "残りリスト表示ボタンの表示を制御",
        },
        "lottery_method": {
            "name": "抽選コントロールパネル位置",
            "description": "抽選コントロールパネルの表示位置を設定",
            "combo_items": {"0": "左", "1": "右"},
        },
        "show_lottery_name": {
            "name": "名前設定ボタン",
            "description": "賞品名設定ボタンの表示を制御",
            "switchbutton_name": {"enable": "表示", "disable": "非表示"},
        },
        "reset_lottery": {
            "name": "抽選リセットボタン",
            "description": "抽選リセットボタンの表示を制御",
            "switchbutton_name": {"enable": "表示", "disable": "非表示"},
        },
        "lottery_quantity_control": {
            "name": "抽選数量コントロールバー",
            "description": "抽選数量調整コントロールバーの表示を制御",
        },
        "lottery_start_button": {
            "name": "開始ボタン",
            "description": "抽選開始ボタンの表示を制御",
        },
        "lottery_list": {
            "name": "抽選リスト切り替えドロップダウン",
            "description": "抽選リスト切り替えドロップダウンの表示を制御",
        },
        "lottery_quantity_label": {
            "name": "数量ラベル",
            "description": "賞品数ラベルの表示モードを設定",
            "combo_items": {"0": "総数+残数", "1": "総数", "2": "残数", "3": "非表示"},
        },
        "lottery_remaining_button": {
            "name": "残りリスト表示ボタン",
            "description": "残りリスト表示ボタンの表示を制御",
        },
        "custom_method": {
            "name": "カスタム抽選コントロールパネル位置",
            "description": "カスタム抽選コントロールパネルの表示位置を設定",
            "combo_items": {"0": "左", "1": "右"},
        },
        "reset_custom": {
            "name": "カスタム抽選リセットボタン",
            "description": "カスタム抽選リセットボタンの表示を制御",
            "switchbutton_name": {"enable": "表示", "disable": "非表示"},
        },
        "custom_quantity_control": {
            "name": "カスタム抽選数量コントロールバー",
            "description": "カスタム抽選数量調整コントロールバーの表示を制御",
        },
        "custom_start_button": {
            "name": "開始ボタン",
            "description": "カスタム抽選開始ボタンの表示を制御",
        },
        "custom_list": {
            "name": "カスタム抽選リスト切り替えドロップダウン",
            "description": "カスタム抽選リスト切り替えドロップダウンの表示を制御",
        },
        "custom_range_start": {
            "name": "カスタム抽選ドロップダウン",
            "description": "カスタム抽選範囲選択ボックスの表示を制御",
        },
        "custom_range_end": {
            "name": "カスタム抽選性別範囲ドロップダウン",
            "description": "カスタム抽選性別範囲選択ボックスの表示を制御",
        },
        "draw_custom_method": {
            "name": "カスタム抽選コントロールパネル位置",
            "description": "カスタム抽選コントロールパネル位置の表示を制御",
        },
        "custom_quantity_label": {
            "name": "数量ラベル",
            "description": "カスタム抽選人数/グループ数ラベルの表示を制御",
        },
        "custom_remaining_button": {
            "name": "残りリスト表示ボタン",
            "description": "残りリスト表示ボタンの表示を制御",
        },
        "roll_call_reset_button": {
            "name": "点呼リセットボタン",
            "description": "有効にすると点呼リセットボタンが表示されます",
        },
        "lottery_reset_button": {
            "name": "抽選リセットボタン",
            "description": "抽選リセットボタンの表示を制御",
        },
        "lottery_roll_call_list": {
            "name": "抽選内の学生リスト切り替えドロップダウン",
            "description": "抽選内の学生リスト切り替えボックスの表示を制御",
        },
        "lottery_roll_call_range": {
            "name": "抽選内の学生点呼範囲ドロップダウン",
            "description": "抽選内の学生名選択ボックスの表示を制御",
        },
        "lottery_roll_call_gender": {
            "name": "抽選内の学生性別範囲ドロップダウン",
            "description": "抽選内の学生性別選択ボックスの表示を制御",
        },
    },
}
