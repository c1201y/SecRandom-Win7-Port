<div align="center">

<img src="secrandom-icon-paper.png" width="128" height="128" alt="SecRandom" />

# SecRandom Win7 Port

**A Windows 7 port of SecRandom, a fork for personal use**

[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg?style=for-the-badge)](../LICENSE)

**Language** [ [简体中文](../README.md) | **English** | [日本語](README_JA.md) ]

</div>

> [!NOTE]
> This repository is a fork of [SECTL/SecRandom](https://github.com/SECTL/SecRandom) with the goal of running on Windows 7 SP1.
>
> Maintained for personal use only; **most of the code is AI-generated**. Use with caution in production.

## About

SecRandom is a fair random-selection application for classrooms, teams, events, decision-making, and other scenarios. This repository adds a Windows 7 compatibility port and personal adjustments on top of the original project.

- The original project targets .NET 10; this repository is ported to **.NET 6** to support Windows 7 SP1
- Only Windows desktop targets (`win-x64`, `win-x86`, `win-arm64`) are kept; mobile and Linux/macOS builds are removed
- Several compatibility tweaks were added for Win7 software rendering (native rounded corners, native layered transparency, disabled MiniAudio audio, etc.)

## Features

### Draw workflows

- **Roll call**: Supports standard random, history-balanced, and repeat-control draws.
- **Quick draw**: Quickly draws students through a standalone floating window.
- **Lottery**: Supports prize-wheel and inventory draws, with students and prizes managed independently.
- **Rich presentation**: Provides unified settings for animation, results, speech, music, and notifications, with fallback when a notification fails.

### Fairness and list management

- Dynamically adjusts weights based on draw history, intervals, groups, and gender to reduce repetition and uneven distribution.
- Uses a stable internal identifier for history; student number, ID, and name are display-only.
- Supports multiple student lists and prize pools with `.xlsx`, `.xls`, and `.csv` import, mapping, and preview.
- Saves history for every draw round for easy review.

### Verifiable draw results

- Automatically saves a proof record file for every draw.
- Optionally lets a server participate in and witness the draw.
- Re-checks draw results through the official channel.

### ClassIsland 1.x linkage

- Links with ClassIsland 1.x by receiving commands over a named pipe from the **[ConvenientText](https://github.com/c1201y/ConvenientText) plugin**.
- Triggers roll-call reset, lottery reset, and similar actions from ClassIsland (e.g. `secrandom://roll_call/reset`, `secrandom://lottery/reset`).
- Commands pass through the same security verification and course-linkage checks as the built-in IPC channel.

### Data, privacy, and security

- Settings, lists, and history can all be imported, exported, backed up, and restored.
- Backups can include lists, history, draw proofs, images, and audio, but never passwords or other security information.
- Protects important operations with a password, TOTP, or USB drive, and configures which operations require verification.

## Tech Stack

| Version | Tech Stack |
| --- | --- |
| This repo | C# + Avalonia + FluentAvalonia (.NET 6, Windows 7 SP1 port) |
| Upstream v3 | C# + Avalonia + FluentAvalonia (.NET 10) |

## Build

```bash
dotnet restore SecRandom.sln
dotnet build SecRandom.sln -c Release --no-restore
dotnet publish SecRandom.Desktop/SecRandom.Desktop.csproj -c Release -r win-x64 --self-contained true -o artifacts/SecRandom-win-x64
```

## Debug page

The debug page is hidden by default. To open it: **Settings → About → Acknowledgment** section, tap the **"Debug"** row, and the debug entry appears at the bottom of the settings sidebar.

## License and Third-Party Notices

- This repository is released under the original project's [GNU GPLv3](../LICENSE); derivative redistributions must also use GNU GPLv3
- Third-party components, copyright, and distribution review details are in [THIRD-PARTY-NOTICES.md](../THIRD-PARTY-NOTICES.md)

## Disclaimer

- This is a personal secondary-development port; **most of the code is AI-generated** and may contain unknown defects
- No official support is provided; back up your data and verify the behavior before use
- Feature details and online witnessing services follow the [upstream repository](https://github.com/SECTL/SecRandom)

**Copyright © 2025-2026 c1201y**