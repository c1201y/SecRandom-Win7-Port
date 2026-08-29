using Avalonia.Media;
using System.Reflection;

namespace SecRandom.Core;

public static class GlobalConstants
{
    public static string Tag => GitInfo.Tag;
    public static string Branch => GitInfo.Branch;
    public static string CommitHash => GitInfo.CommitHash?.Length >= 7 ? GitInfo.CommitHash[..7] : GitInfo.CommitHash ?? string.Empty;
    public static string FullCommitHash => GitInfo.CommitHash ?? string.Empty;

    public static string CodeName => @"Nonomi";
    public static string Version => @"v3.1.5.1";
    public static string AssemblyVersion => @"3.1.5.1";
    public static string DisplayVersion => $@"{Version} 移植版";
    public static string VersionLong => $@"{Version}-{CodeName}-{CommitHash}({Branch})";

    public static string PlatformExecutableExtension => OperatingSystem.IsWindows() ? @".exe" : "";

    // 桌面与移动端遥测共用的 Sentry DSN；两端各自适配器不得再硬编码副本
    public const string SentryDsn = "https://7614b2b2fd46a451e7cb3ed670279e75@o4510689230192640.ingest.us.sentry.io/4511675887910912";
    public const string BehindSceneAttachedSettings = "F45DFB95-7D20-4BAB-86A3-8864BBDFCE9E";
    public const string SpecificAnnouncementAttachedSettings = "10F2C686-07D7-47E7-9A4F-B7A4724A6A10";
    public const string DrawImageAttachedSettings = "4C88E037-4F69-42D0-A32F-16D2827B7B6D";
    public const string DrawMusicAttachedSettings = "A16F1E84-77E8-4E09-B9EC-8BAF5C148057";

    public const string DefaultThemeColor = "#0078D4"; // 系统自带主题色蓝  66CCFF 天依蓝
    public const string DefaultFontFamily = "avares://SecRandom/Assets/Fonts/MiSans/#MiSans";

#if DEBUG
    public static bool IsDevelopment => true;
#else
    public static bool IsDevelopment => false;
#endif

    public static FontFamily FluentIconsFontFamily { get; } =
        new(@"avares://SecRandom/Assets/Fonts/#FluentSystemIcons-Resizable");

    public static FontFamily DefaultAvaFontFamily { get; } =
        new(@"avares://SecRandom/Assets/Fonts/MiSans/#MiSans");
}
