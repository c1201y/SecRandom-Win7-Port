# v3.1.4.0

## 🚀 主要更新

- 窗口缩放体验正式稳定化：此前 v3.1.3.0 引入的「无边框窗口边缘拖拽缩放」在 Windows 7 上经实机验证并修复，现可平滑使用
- **Windows 7 兼容性全面修复**：SetWindowDisplayAffinity 降级、CreateRoundRectRgn 参数修正、32 位 P/Invoke 路由、DPI 感知时序修正、OpenCV 原生库降级，Win7 上摄像头/窗口圆角/高 DPI 缩放均可正常使用

## 🐛 修复问题

- 修复 拖拽窗口边缘调整大小时出现的明显闪烁（根因：Avalonia 窗口类注册的 `CS_HREDRAW | CS_VREDRAW` 在每次 resize 时强制整窗擦除重绘；现逐窗口移除该样式，resize 时保留旧帧）
- 修复 快速拖拽窗口边缘时未加载区域短暂出现黑色条块的问题（`WM_ERASEBKGND` 改为仅填充新暴露的条带，避免整窗擦除露黑）
- 修复 将窗口拖动到屏幕顶部无法触发最大化的问题（恢复系统原生 `WS_THICKFRAME` sizing 边框与 Aero Snap 拖顶最大化，覆盖引导窗、主窗、设置窗三个窗口）
- 修复 重复启动弹窗先显示浅灰窗口的闪烁
- 修复 上一轮修复引入的 `ConditionalWeakTable.Add` 重复键崩溃导致 Win7 启动后窗口无法创建（`GetValue` 将「守卫检查 + 添加」原子化，同一窗口重复触发 `IsVisible` 也不再生效重复键）
- 修复 Win7 上 `SetWindowDisplayAffinity`（Win8+ API）未做运行时版本检测可能导致 `EntryPointNotFoundException` 崩溃的问题（增加 `IsWindowsVersionAtLeast(6,2)` 防御检查）
- 修复 `CreateRoundRectRgn` 参数错误导致圆角区域比客户区大 1 像素的渲染溢出（right/bottom 应为坐标值而非宽高）
- 修复 32 位 Windows 上 `GetWindowLongPtrW`/`SetWindowLongPtrW` 不存在为 DLL 导出（仅为头文件宏）导致 `EntryPointNotFoundException` 的问题（按 `IntPtr.Size` 路由到 `GetWindowLongW`/`SetWindowLongW`）
- 修复 `SetProcessDPIAware` 调用时序过晚，子进程可能继承非 DPI 感知状态的问题（提前到 `Main()` 最早位置）
- 修复 DPI 缩放反射补丁无异常保护，Avalonia 内部字段变更时可能导致启动崩溃的问题（增加 try-catch，失败时以 1.0 缩放渲染）
- 修复 Win7 上 OpenCvSharp4 原生 DLL 加载失败导致摄像头 QR 扫描崩溃的问题（降级 `OpenCvSharp4.runtime.win` 到 4.7.0 并增加 try-catch 安全网）

## 🔧 其它变更

- 引导窗 / 主窗 / 设置窗改为 `SystemDecorations.BorderOnly`（保留隐形 sizing 边框、去标题栏），由系统原生 resize 循环接管，移除原先的手动 `SetWindowPos` 模拟缩放 hack
- `OpenCvSharp4.runtime.win` 从 4.13.0 降级到 4.7.0（最后确认支持 Win7 的原生构建版本），managed wrapper 保持 4.13.0

