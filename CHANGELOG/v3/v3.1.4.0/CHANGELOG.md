# v3.1.4.0

## 🚀 主要更新

- 窗口缩放体验正式稳定化：此前 v3.1.3.0 引入的「无边框窗口边缘拖拽缩放」在 Windows 7 上经实机验证并修复，现可平滑使用

## 🐛 修复问题

- 修复 拖拽窗口边缘调整大小时出现的明显闪烁（根因：Avalonia 窗口类注册的 `CS_HREDRAW | CS_VREDRAW` 在每次 resize 时强制整窗擦除重绘；现逐窗口移除该样式，resize 时保留旧帧）
- 修复 快速拖拽窗口边缘时未加载区域短暂出现黑色条块的问题（`WM_ERASEBKGND` 改为仅填充新暴露的条带，避免整窗擦除露黑）
- 修复 将窗口拖动到屏幕顶部无法触发最大化的问题（恢复系统原生 `WS_THICKFRAME` sizing 边框与 Aero Snap 拖顶最大化，覆盖引导窗、主窗、设置窗三个窗口）
- 修复 重复启动弹窗先显示浅灰窗口的闪烁
- 修复 上一轮修复引入的 `ConditionalWeakTable.Add` 重复键崩溃导致 Win7 启动后窗口无法创建（`GetValue` 将「守卫检查 + 添加」原子化，同一窗口重复触发 `IsVisible` 也不再生效重复键）

## 🔧 其它变更

- 引导窗 / 主窗 / 设置窗改为 `SystemDecorations.BorderOnly`（保留隐形 sizing 边框、去标题栏），由系统原生 resize 循环接管，移除原先的手动 `SetWindowPos` 模拟缩放 hack

