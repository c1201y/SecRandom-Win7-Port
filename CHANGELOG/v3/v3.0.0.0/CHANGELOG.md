# v3.0.0.0 — Windows 7 兼容移植版

## 🚀 主要更新

- **目标框架从 .NET 10 降级至 .NET 6**，支持 Windows 7 SP1 及以上系统运行
- 移除 Edge TTS 依赖（保留桩类），精简第三方组件
- 替换 .NET 7/8 专有 API（`nint.Zero`、`GeneratedRegex`、`TimeProvider`、`AesGcm` 重载等），使用 .NET 6 兼容写法
- 添加 `UnsafeAccessorAttribute`、`RequiredMemberAttribute`、`CompilerFeatureRequiredAttribute` 等编译器多态填充
- 图标引用改用 Unicode 字面量，绕过 Source Generator 在 .NET 6 下不运行的限制
- Windows 7 启动强制启用 Avalonia 软件渲染，DrawAudioService 在非 x64 平台跳过 MiniAudio 后端

## 🐛 修复问题

- 修复 `SecRandom.Platforms.Linux` 和 `SecRandom.Platforms.MacOs` 目标框架未对齐至 net6.0 的问题
- 修复 CI 构建工作流：发布工作流改为仅手动触发并自动创建 tag
- 修复 `miniaudio.dll` 原生库在发布输出中缺失的问题

---

💝 **感谢所有贡献者为 SecRandom 项目付出的努力！**
