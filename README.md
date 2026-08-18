<div align="center">

<img src="resources/secrandom-icon-paper.png" width="128" height="128" alt="SecRandom" />

# SecRandom Win7 Port

**面向 Windows 7 的 SecRandom 二次开发移植版**

[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg?style=for-the-badge)](LICENSE)

**语言** [ **简体中文** | [English](resources/README_EN.md) | [日本語](resources/README_JA.md) ]

</div>

> [!NOTE]
> 本仓库是 [SECTL/SecRandom](https://github.com/SECTL/SecRandom) 的二次开发版本，目标是在 Windows 7 SP1 上运行
>
> 本项目仅为个人自用维护，**绝大部分代码由 AI 构建**，

## 说明

SecRandom 是面向课堂、团队、活动、决策等场景的公平抽取应用。本仓库在原项目基础上做了 Windows 7 兼容性移植与个人化调整：

- 原项目基于 .NET 10 构建，本仓库移植到 **.NET 6**，支持 Windows 7 SP1
- 仅保留 Windows 桌面目标（`win-x64`、`win-x86`、`win-arm64`），移除了移动端与 Linux/macOS 构建
- 针对 Win7 软件渲染做了若干兼容处理（如原生圆角、原生分层透明度、禁用 MiniAudio 音频等）

## 软件功能

### 抽取流程

- **点名**：支持普通随机、历史平衡及重复控制
- **闪抽**：通过独立悬浮窗快速抽取学生
- **抽奖**：支持奖品盘和库存抽取，学生与奖品独立管理
- **丰富呈现**：统一配置动画、结果、语音、音乐和通知，并支持通知失败回退

### 公平与名单管理

- 根据历史次数、抽取间隔、分组、性别等因素动态调整权重，降低重复与分布失衡
- 使用稳定内部标识维护历史，学号、编号和名称仅作为显示信息
- 支持多名单、多奖品池及 `.xlsx`、`.xls`、`.csv` 导入、映射和预览
- 每轮抽取均保存历史，方便查询和回顾

### 抽取结果可复查

- 每次抽取都会自动保存证明记录文件
- 可以选择让服务器参与并见证抽取过程
- 可以通过官方渠道重新检查抽取结果

### ClassIsland 1.x 联动

- 可与 ClassIsland 1.x 版本联动，通过命名管道接收来自 **[ConvenientText](https://github.com/c1201y/ConvenientText) 插件
- 指令同样经过安全验证与课程联动检查，与内置 IPC 通道行为一致

### 数据、隐私与安全

- 设置、名单和历史记录都可以导入、导出、备份和恢复
- 备份可以包含名单、历史、抽取证明、图片、音频等信息，但不会包含密码等安全信息
- 支持使用密码、TOTP或 U 盘保护重要操作，并可设置哪些操作需要验证

## 技术栈

| 版本 | 技术栈 |
| --- | --- |
| 本仓库 | C# + Avalonia + FluentAvalonia（.NET 6，Windows 7 SP1 移植） |
| 上游 v3 | C# + Avalonia + FluentAvalonia（.NET 10） |

## 构建

```bash
dotnet publish SecRandom.Desktop/SecRandom.Desktop.csproj -c Release -r win-x64 --self-contained true -o artifacts/SecRandom-win-x64
```

## 调试页

调试页默认隐藏，打开方式：点击设置窗口右上角的 **"⋯"（更多选项）** 菜单中的 **"调试"** 一项，调试项即会出现在设置侧边栏底部。

## 许可证与第三方声明

- 本仓库沿用原项目的 [GNU GPLv3](LICENSE) 协议发布，再发布衍生作品也必须遵循 GNU GPLv3
- 第三方组件、版权和分发审查信息见 [THIRD-PARTY-NOTICES.md](THIRD-PARTY-NOTICES.md)

## 免责声明

- 本项目为个人二次开发移植，**绝大多数代码由 AI 生成**，可能存在未知缺陷
- 不提供任何形式的官方支持；使用前请自行备份数据并确认功能符合预期
- 原项目的功能细节、在线见证服务等以 [上游仓库](https://github.com/SECTL/SecRandom) 说明为准

**Copyright © 2025-2026 椰汁**