<div align="center">

<img src="secrandom-icon-paper.png" width="128" height="128" alt="SecRandom" />

# SecRandom Win7 Port

**Windows 7 向けの SecRandom 二次開発移植版**

[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg?style=for-the-badge)](../LICENSE)

**言語** [ [简体中文](../README.md) | [English](README_EN.md) | **日本語** ]

</div>

> [!NOTE]
> このリポジトリは [SECTL/SecRandom](https://github.com/SECTL/SecRandom) の二次開発版で、Windows 7 SP1 での動作を目的としています
>
> 個人用途で保守しており、**コードの大部分は AI によって生成されています**。本番環境での利用には注意してください

## 概要

SecRandom は、授業、チーム、イベント、意思決定などの場面で公平な抽選を行うためのアプリケーションです。このリポジトリでは、元プロジェクトに Windows 7 互換性の移植と個人向けの調整を加えています。

- 元プロジェクトは .NET 10 で構築されていますが、本リポジトリは **.NET 6** に移植し、Windows 7 SP1 をサポートします
- Windows デスクトップのみ（`win-x64`、`win-x86`、`win-arm64`）を対象とし、モバイルおよび Linux/macOS のビルドは除外しました
- Win7 のソフトウェアレンダリング向けにいくつかの互換処理を追加しました（ネイティブ角丸、ネイティブレイヤード透明度、MiniAudio オーディオ無効化など）

## 機能

### 抽選ワークフロー

- **点呼**: 通常のランダム抽選、履歴バランス抽選、重複制御に対応します。
- **クイック抽選**: 独立したフローティングウィンドウから、生徒をすばやく抽選します。
- **抽選会**: 賞品ルーレットと在庫抽選に対応し、生徒と賞品を個別に管理します。
- **豊かな演出**: アニメーション、結果、音声、音楽、通知を統一設定で管理し、通知失敗時のフォールバックに対応します。

### 公平性とリスト管理

- 履歴回数、抽選間隔、グループ、性別などに基づいて重みを動的に調整し、重複と分布の偏りを抑えます。
- 安定した内部識別子で履歴を管理します。学籍番号、ID、名前は表示情報のみです。
- 複数の生徒リストと賞品プール、および `.xlsx`、`.xls`、`.csv` のインポート、マッピング、プレビューに対応します。
- すべての抽選ラウンドの履歴を保存し、確認しやすくします。

### 抽選結果の再確認

- 抽選ごとに証明記録ファイルを自動保存します。
- サーバーを抽選に参加させ、立ち会わせるかどうかを選択できます。
- 公式チャンネルを通じて抽選結果を再確認できます。

### ClassIsland 1.x 連携

- ClassIsland 1.x と連携し、名前付きパイプを介して **[ConvenientText](https://github.com/c1201y/ConvenientText) プラグイン** からの連携コマンドを受け取ります。
- ClassIsland から点呼リセット、抽選会リセットなどの操作を実行できます（例: `secrandom://roll_call/reset`、`secrandom://lottery/reset`）。
- コマンドは内蔵 IPC チャンネルと同様のセキュリティ検証と授業リンクチェックを通過します。

### データ、プライバシー、セキュリティ

- 設定、リスト、履歴はすべてインポート、エクスポート、バックアップ、復元に対応します。
- バックアップにはリスト、履歴、抽選証明、画像、音声を含められますが、パスワードなどのセキュリティ情報は含まれません。
- パスワード、TOTP、USB メモリによる保護で重要な操作を守り、検証が必要な操作を設定できます。

## 技術スタック

| バージョン | 技術スタック |
| --- | --- |
| 本リポジトリ | C# + Avalonia + FluentAvalonia（.NET 6、Windows 7 SP1 移植） |
| 元 v3 | C# + Avalonia + FluentAvalonia（.NET 10） |

## ビルド

```bash
dotnet restore SecRandom.sln
dotnet build SecRandom.sln -c Release --no-restore
dotnet publish SecRandom.Desktop/SecRandom.Desktop.csproj -c Release -r win-x64 --self-contained true -o artifacts/SecRandom-win-x64
```

## ライセンスと第三者通知

- 本リポジトリは元プロジェクトの [GNU GPLv3](../LICENSE) に従って公開されており、派生物も GNU GPLv3 で公開する必要があります
- 第三者コンポーネント、著作権情報、配布審査に関する注記は [THIRD-PARTY-NOTICES.md](../THIRD-PARTY-NOTICES.md) を参照してください

## 免責事項

- 個人による二次開発移植であり、**コードの大部分は AI によって生成されています**。未知の欠陥が含まれる可能性があります
- 公式サポートは提供していません。利用前にデータをバックアップし、機能が期待どおりであることを確認してください
- 機能の詳細やオンライン立会いサービスについては、[元リポジトリ](https://github.com/SECTL/SecRandom) の説明を参照してください

**Copyright © 2025-2026 c1201y**