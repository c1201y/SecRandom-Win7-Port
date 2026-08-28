# v3.1.5.0

## 🚀 主要更新

- **全面代码审查与 bug 修复**：对 Win7 兼容性、内存泄漏、并发安全、UI 线程阻塞等维度进行系统性审计，共修复 24 个问题
- **抽奖/点名防重复提交**：快速连续点击「开始」按钮不再产生重复的历史记录
- **UI 响应性提升**：名单/奖池文件枚举从 UI 线程同步 I/O 改为后台异步执行，切换名单时界面不再卡顿

## 🐛 修复问题

- 修复 3 个 ViewModel（RollCall/Lottery/QuickDraw）`Dispose` 时未释放 `ResultItems` 中的 `Bitmap` 导致内存持续增长的问题
- 修复 `ShortcutService.Dispose` 遗漏 `featureAvailability.Changed` 事件退订的问题
- 修复 QuickDraw `StartCooldown` 无 try-finally 导致异常时 `_isCoolingDown` 永远卡住的问题
- 修复 `UpdateCenterService` `CancellationTokenSource` 竞态条件——快速连续触发更新检查时可能访问已释放的 CTS
- 修复 `WindowsAudioPlayback.Stop` 与 `Dispose` 并发时的 `ObjectDisposedException` 崩溃
- 修复 `TimerViewModel._viewRefs` 计数可变为负数导致 AttachView 无法重新启动 Timer 的逻辑 bug
- 修复 `MainWindow.SaveWindowSize` 在 `_configHandler` 为 null 时的 `NullReferenceException` 崩溃
- 修复 Lottery/RollCall `StartDrawCoreAsync` 缺少 `_isDrawCommandRunning` 检查，取消后重新抽奖可能触发并发抽取并写入重复历史记录的问题
- 修复 8 处名单/奖池文件枚举（`Directory.GetFiles`）和插件 README 读取（`File.ReadAllText`）在 UI 线程同步执行导致界面冻结的问题——改为 `Task.Run` 后台执行
- 修复 `SettingsView` 和 `MainView` 窗口卸载时未移除 `AppToastAdorner` 导致的潜在内存泄漏
- 修复 `MainWindow.SettingsOnPropertyChanged` 中 `_settings!.AutoSaveWindowSize` 空引用风险

## 🔧 其它变更

- `RefreshLists` / `RefreshPrizeLists` / `RefreshStudentLists` 签名从 `void` 改为 `async Task`（`RefreshAfterProfileChange` 同步改为 `RefreshAfterProfileChangeAsync`）
