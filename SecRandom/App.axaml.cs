using System.Diagnostics;
using System.Globalization;
using System.Linq;
using System.Reflection;
using System.Runtime.InteropServices;
using System.Text.Json;
using Avalonia;
using Avalonia.Controls;
using Avalonia.Controls.ApplicationLifetimes;
using Avalonia.Markup.Xaml;
using Avalonia.Media;
using Avalonia.Platform;
using Avalonia.Styling;
using Avalonia.Threading;
using Avalonia.VisualTree;
using FluentAvalonia.Styling;
using FluentAvalonia.UI.Controls;
using HotAvalonia;
using Microsoft.Extensions.DependencyInjection;
using Microsoft.Extensions.Hosting;
using Microsoft.Extensions.Logging;
using Microsoft.Extensions.Logging.Console;
using Sentry;
using SecRandom.Controls.AttachedSettings;
using SecRandom.Core;
using SecRandom.Core.Abstraction;
using SecRandom.Core.Abstraction.Services;
using SecRandom.Core.Controls;
using SecRandom.Core.Enums;
using SecRandom.Core.Enums.Configs;
using SecRandom.Core.Extensions.Registry;
using SecRandom.Core.Icons;
using SecRandom.Core.Models;
using SecRandom.Core.Models.SubConfigs;
using SecRandom.Core.Services.Config;
using SecRandom.Core.Services.Draw;
using SecRandom.Core.Services;
using SecRandom.Core.Services.Archive;
using SecRandom.Core.Services.Verification;
using SecRandom.Core.Services.Logging;
using SecRandom.Core.Services.SingleInstance;
using SecRandom.Core.Views;
using SecRandom.Shared.Models.Ipc;
using SecRandom.Shared;
using SecRandom.Dialogs;
using AppearanceSettingsConfig = SecRandom.Core.Models.SubConfigs.Personalized.AppearanceSettingsConfig;
using SecRandom.Services;
using SecRandom.Services.Config;
using SecRandom.Services.CrashRecovery;
using SecRandom.Services.Desktop;
using SecRandom.Services.Draw;
using SecRandom.Services.Notification;
using SecRandom.Services.Profiles;
using SecRandom.Services.RosterTransfer;
using SecRandom.Services.Ipc;
using SecRandom.Services.ImportExport;
using SecRandom.Services.FirstRun;
using SecRandom.Services.Feedback;
using SecRandom.Services.Linkage;
using SecRandom.Services.Music;
using SecRandom.Services.Settings;
using SecRandom.Services.Platform;
using SecRandom.Services.Security;
using SecRandom.Services.SecAgent;
using SecRandom.Services.Telemetry;
using SecRandom.Services.Verification;
using SecRandom.Services.Voice;
using SecRandom.Services.Updates;
using SecRandom.Services.ViewEngine;
using SecRandom.Mobile;
using SecRandom.Services.Mobile;
using SecRandom.Views.Mobile;
using SecRandom.Views.Mobile.Settings;
using SecRandom.Platforms;
using SecRandom.Platforms.Abstractions;
using MobileResources = SecRandom.Langs.Mobile.Resources;
using SecRandom.ViewModels;
using SecRandom.ViewModels.MainPages;
using SecRandom.ViewModels.SettingsPages;
using SecRandom.ViewModels.SettingsPages.History;
using SecRandom.Views;
using SecRandom.Views.MainPages;
using SecRandom.Views.SettingsPages;
using SecRandom.Views.SettingsPages.About;
using SecRandom.Views.SettingsPages.General;
using SecRandom.Views.SettingsPages.History;
using SecRandom.Views.SettingsPages.Linkage;
using SecRandom.Views.SettingsPages.ListManagement;
using SecRandom.Views.SettingsPages.LogViewer;
using SecRandom.Views.SettingsPages.More;
using SecRandom.Views.SettingsPages.Personalized;
using SecRandom.Views.SettingsPages.Picking;
using SecRandom.Views.SettingsPages.Update;
// using SecRandom.Views.SettingsPages.Plugins.Overview;
using DefaultNotificationSettingsPage = SecRandom.Views.SettingsPages.Notification.DefaultNotificationSettingsPage;
using FloatingWindowSettingsPage = SecRandom.Views.SettingsPages.Personalized.FloatingWindowSettingsPage;
using LotteryNotificationSettingsPage = SecRandom.Views.SettingsPages.Notification.LotteryNotificationSettingsPage;
using QuickDrawNotificationSettingsPage = SecRandom.Views.SettingsPages.Notification.QuickDrawNotificationSettingsPage;
using RollCallNotificationSettingsPage = SecRandom.Views.SettingsPages.Notification.RollCallNotificationSettingsPage;
using SecuritySettingsPage = SecRandom.Views.SettingsPages.General.SecuritySettingsPage;
using VoiceSettingsPage = SecRandom.Views.SettingsPages.Notification.VoiceSettingsPage;
using CR = SecRandom.Langs.Common.Resources;

namespace SecRandom;

public partial class App : Application
{
    private static FloatingWindow? _floatingWindow;
    private static Window? _quickDrawWindow;
    private static NotificationChannelSettings? _quickDrawNotificationSettings;
    private static MainWindow? _mainWindow;
    private static MainWindow? _settingsWindow;
    private NativeMenuItem? _floatingWindowMenuItem;
    private static IClassicDesktopStyleApplicationLifetime? _desktopLifetime;
    private IHost? _mobileHost;
    private ISingleViewApplicationLifetime? _singleViewLifetime;
    private MobileViewHost? _mobileViewHost;
    private bool _mobileStopping;
    private bool _mobileStartupFailureShown;
    private Utils.DesktopDataRootPreparationResult? _desktopDataRootPreparation;
    private readonly object _shutdownGate = new();
    private bool _isStopping;
    private bool _isOobeActive;
    public new static App Current => (Application.Current as App)!;
    internal bool IsStopping => _isStopping;
    public static bool IsDesktop;

    public TopLevel GetRootWindow()
    {
        if (_desktopLifetime?.Windows
                .Where(window => window.GetType().Name != "TrayPopupRoot"
                                 && window is { IsActive: true, IsVisible: true, PlatformImpl: not null })
                .OrderBy(window => ReferenceEquals(window, _floatingWindow) ? 1 : 0)
                .FirstOrDefault() is TopLevel desktopRoot)
            return desktopRoot;

        if (_mobileViewHost is not null && TopLevel.GetTopLevel(_mobileViewHost) is { } mobileRoot)
            return mobileRoot;

        if (_floatingWindow is { PlatformImpl: not null } floatingRoot)
        {
            floatingRoot.Activate();
            return floatingRoot;
        }

        throw new InvalidOperationException("No active application TopLevel is available.");
    }

    public event EventHandler? AppStarted;
    public event EventHandler? AppStopping;

    public override void Initialize()
    {
        TouchInputModeAssist.Initialize();
        var isMobile = PlatformStartupContext.Current is MobilePlatformServiceRoot;
        if (isMobile)
            Utils.ConfigureMobileDataRoot();
        else
            _desktopDataRootPreparation = Utils.PrepareDesktopDataRoot();

        // ��ʼ������
        var mainConfig = new MainConfigModel();
        var settings = _desktopDataRootPreparation is { IsPortablePackage: true, IsWritable: false }
            ? mainConfig
            : LoadStartupSettings(mainConfig);
        var culture = settings.Basic.Language switch
        {
            LanguageMode.ChineseSimplified => @"zh-Hans",
            LanguageMode.English => @"en-US",
            LanguageMode.Japanese => @"ja-JP",
            _ => @"zh-Hans"
        };
        InitializeLanguages(new CultureInfo(culture));
        if (isMobile)
            ApplyMobileCulture(new CultureInfo(culture));

        // ��ʼ�� Avalonia App
        AvaloniaXamlLoader.Load(this);

        // �� XAML ��Դ������ɺ�����Ӧ��������ã����� BuildHost��ȷ���ظ�ʵ���Ի���Ҳ�ܸ������⣩
        ApplyStartupAppearance(settings.Appearance);

        if (!Design.IsDesignMode && !OperatingSystem.IsMacOS() && !OperatingSystem.IsAndroid() &&
            !OperatingSystem.IsIOS())
        {
            this.EnableHotReload();
        }

#if DEBUG
        // ���ӿ����߹���
        this.AttachDeveloperTools();
#endif
    }

    public override void OnFrameworkInitializationCompleted()
    {
        var startupProtocolUri = ProtocolActivation.ConsumeStartupUri();
        if (ApplicationLifetime is IClassicDesktopStyleApplicationLifetime desktop)
        {
            WriteDesktopStartupDiagnostic("Desktop framework initialization started.");
            _desktopLifetime = desktop;
            IsDesktop = true;

            if (_desktopDataRootPreparation is { IsPortablePackage: true, IsWritable: false } preparation)
            {
                desktop.MainWindow = CreatePortableDataRootFailureHost(desktop, preparation);
                base.OnFrameworkInitializationCompleted();
                return;
            }

            if (CrashRecoveryRuntime.StartupPromptOptions is { } promptOptions)
            {
                // ���ֱ�����ʾ�ڵ�ʵ����ȡǰ�������� Host ���ṩ��ϵ�����Ӧ���ڷ�����
                try
                {
                    BuildHost(PlatformStartupContext.Current);
                }
                catch (Exception exception)
                {
                    WriteDesktopStartupDiagnostic("Crash-recovery Host build failed.", exception);
                }

                desktop.MainWindow = ShowCrashRecoveryPromptOnly(promptOptions);
                base.OnFrameworkInitializationCompleted();
                return;
            }

            // ===== ��ʵ����⣨�� Desktop Lifetime��=====
            if (!SingleInstanceService.Instance.TryAcquire())
            {
                // ����ʵ�������У�������ʱ����������ʾ�Ի������� BuildHost
                desktop.MainWindow = CreateDuplicateInstanceDialogHost(desktop, startupProtocolUri);
                base.OnFrameworkInitializationCompleted();
                return;
            }

            // ����������ע�� IPC ��������ٹ�������
            SingleInstanceService.Instance.CommandReceived += OnIpcCommandReceived;
            SingleInstanceService.Instance.RequestReceived += OnIpcRequestReceived;

            // ������������
            try
            {
                WriteDesktopStartupDiagnostic("Building desktop Host.");
                BuildHost(PlatformStartupContext.Current);
                WriteDesktopStartupDiagnostic("Desktop Host built.");
            }
            catch (Exception exception)
            {
                WriteDesktopStartupDiagnostic("Desktop Host build failed.", exception);
                throw;
            }

            if (IAppHost.GetService<FirstRunOobeService>().IsRequired())
            {
                ShowFirstRunOobe(desktop, startupProtocolUri);
                base.OnFrameworkInitializationCompleted();
                return;
            }

            try
            {
                WriteDesktopStartupDiagnostic("Continuing desktop startup.");
                ContinueDesktopStartup(desktop, startupProtocolUri);
                WriteDesktopStartupDiagnostic("Desktop startup initialized.");
            }
            catch (Exception exception)
            {
                WriteDesktopStartupDiagnostic("Desktop startup initialization failed.", exception);
                throw;
            }
        }
        else if (ApplicationLifetime is ISingleViewApplicationLifetime singleView)
        {
            StartMobileApplication(singleView);
        }

        base.OnFrameworkInitializationCompleted();
    }

    private void StartMobileApplication(ISingleViewApplicationLifetime singleView)
    {
        _singleViewLifetime = singleView;
        Dispatcher.UIThread.UnhandledException += MobileDispatcherOnUnhandledException;
        try
        {
            BuildHost(PlatformStartupContext.Current);
            _mobileHost = IAppHost.Host;
            _mobileViewHost = ActivatorUtilities.CreateInstance<MobileViewHost>(_mobileHost!.Services);
            singleView.MainView = _mobileViewHost;
            ObserveTask(_mobileHost.Services.GetRequiredService<IViewEngine>().ShowAsync(GetMobileInitialViewId()),
                "Mobile root view activation failed.");

            if (singleView is IControlledApplicationLifetime controlled)
                controlled.Exit += (_, _) => _ = StopMobileHostAsync();

            ObserveTask(StartMobileHostAsync(_mobileHost), "Mobile runtime service startup failed.");
        }
        catch (Exception exception)
        {
            ReportMobileException(exception);
            if (ReferenceEquals(IAppHost.Host, _mobileHost))
                IAppHost.Host = null;
            _mobileHost?.Dispose();
            _mobileHost = null;
            ShowMobileStartupFailure(exception);
        }
    }

    private async Task StartMobileHostAsync(IHost host)
    {
        try
        {
            _ = host.Services.GetRequiredService<IProfileService>();
            _ = host.Services.GetRequiredService<IDrawTemporaryRecordService>();
            _ = host.Services.GetRequiredService<IFeatureAvailabilityService>();
            _ = host.Services.GetRequiredService<DrawEngine>();
            if (_mobileStopping || !ReferenceEquals(host, _mobileHost))
                return;

            await host.StartAsync().ConfigureAwait(false);
            if (_mobileStopping || !ReferenceEquals(host, _mobileHost))
                return;

            await host.Services.GetRequiredService<TelemetryRuntimeService>().InitializeAsync().ConfigureAwait(false);
        }
        catch (Exception exception)
        {
            ReportMobileException(exception);
            if (_mobileStopping || !ReferenceEquals(host, _mobileHost))
                return;

            await StopMobileHostAsync().ConfigureAwait(false);
            await Dispatcher.UIThread.InvokeAsync(() => ShowMobileStartupFailure(exception));
        }
    }

    private async Task ReloadMobileRootViewAsync()
    {
        IHost? host = _mobileHost;
        ISingleViewApplicationLifetime? singleView = _singleViewLifetime;
        if (_mobileStopping || host is null || singleView is null)
            return;

        MobileViewHost? oldHost = _mobileViewHost;
        if (oldHost is not null)
        {
            var engine = host.Services.GetRequiredService<IViewEngine>();
            await engine.CloseHostAsync(oldHost, ViewCloseReason.Programmatic).ConfigureAwait(false);
            await oldHost.DestroyAsync().ConfigureAwait(false);
            await oldHost.DetachAsync().ConfigureAwait(false);
        }

        var newHost = ActivatorUtilities.CreateInstance<MobileViewHost>(host.Services);
        _mobileViewHost = newHost;
        await Dispatcher.UIThread.InvokeAsync(() => singleView.MainView = newHost);
        await host.Services.GetRequiredService<IViewEngine>().ShowAsync(GetMobileInitialViewId()).ConfigureAwait(false);
    }

    private static string GetMobileInitialViewId() =>
        (PlatformStartupContext.Current as MobilePlatformServiceRoot)?.UsesDesktopMainView == true
            ? DesktopViewIds.Main
            : MobilePageIds.Root;

    private async Task StopMobileHostAsync()
    {
        IHost? host = _mobileHost;
        if (_mobileStopping || host is null)
            return;

        _mobileStopping = true;
        try
        {
            if (_mobileViewHost is not null)
            {
                await host.Services.GetRequiredService<IViewEngine>()
                    .CloseHostAsync(_mobileViewHost, ViewCloseReason.ApplicationShutdown)
                    .ConfigureAwait(false);
                await _mobileViewHost.DestroyAsync().ConfigureAwait(false);
                await _mobileViewHost.DetachAsync().ConfigureAwait(false);
            }

            IMobileMediaPlayer mediaPlayer = host.Services.GetRequiredService<IMobileMediaPlayer>();
            await mediaPlayer.StopAsync().ConfigureAwait(false);
            if (mediaPlayer is IDisposable disposableMediaPlayer)
                disposableMediaPlayer.Dispose();
            await host.Services.GetRequiredService<TelemetryRuntimeService>().ShutdownAsync().ConfigureAwait(false);
            await host.StopAsync(TimeSpan.FromSeconds(5)).ConfigureAwait(false);
        }
        catch (Exception exception)
        {
            ReportMobileException(exception);
        }
        finally
        {
            if (ReferenceEquals(IAppHost.Host, host))
                IAppHost.Host = null;
            host.Dispose();
            if (ReferenceEquals(_mobileHost, host))
                _mobileHost = null;
            _mobileViewHost = null;
        }
    }

    private void MobileDispatcherOnUnhandledException(object? sender, DispatcherUnhandledExceptionEventArgs e)
    {
        TrySaveConfigForCrashRecovery();
        ReportMobileException(e.Exception);
        ObserveTask(CaptureUnhandledExceptionAsync(e.Exception),
            "Mobile unhandled exception telemetry capture failed.");
        e.Handled = true;

        CrashRecoveryPromptOptions? options = CrashRecoveryRuntime.TryCreateCurrentProcessPromptOptions(e.Exception);
        if (options is not null)
            ShowMobileCrashRecovery(options);
    }

    private void ShowMobileCrashRecovery(CrashRecoveryPromptOptions options)
    {
        CrashRecoveryViewState? state = IAppHost.TryGetService<CrashRecoveryViewState>();
        IViewEngine? engine = IAppHost.TryGetService<IViewEngine>();
        if (state is null || engine is null)
            return;

        state.Configure(options, static () => false, canIgnore: true);
        ObserveTask(engine.ShowAsync("system.crashRecovery"), "Mobile crash recovery display failed.");
    }

    private void ShowMobileStartupFailure(Exception exception)
    {
        if (_mobileStartupFailureShown || _singleViewLifetime is null)
            return;

        _mobileStartupFailureShown = true;
        _singleViewLifetime.MainView = CreateMobileStartupFailureView(exception);
    }

    internal static void ApplyMobileCulture(CultureInfo culture)
    {
        ArgumentNullException.ThrowIfNull(culture);
        MobileResources.Culture = culture;
    }

    private static Control CreateMobileStartupFailureView(Exception exception)
    {
        string startupFailedText;
        try
        {
            startupFailedText = MobileResources.M_StartupFailed;
        }
        catch (Exception resourceException)
        {
            startupFailedText = "SecRandom startup failed: " + resourceException.GetType().Name;
        }

        return new ScrollViewer
        {
            Content = new TextBlock
            {
                Text = startupFailedText + "\n" + exception,
                Margin = new Thickness(32),
                TextAlignment = TextAlignment.Center,
                TextWrapping = TextWrapping.Wrap,
                HorizontalAlignment = Avalonia.Layout.HorizontalAlignment.Center,
                VerticalAlignment = Avalonia.Layout.VerticalAlignment.Center
            }
        };
    }

    private static void ReportMobileException(Exception exception)
    {
        System.Diagnostics.Debug.WriteLine(exception);
        (PlatformStartupContext.Current as MobilePlatformServiceRoot)?.StartupErrorLogger?.Invoke(exception);
    }

    private void ContinueDesktopStartup(IClassicDesktopStyleApplicationLifetime desktop, string? startupProtocolUri)
    {
        _desktopLifetime = desktop;
        WriteDesktopStartupDiagnostic("Scheduling desktop runtime services.");
        ObserveTask(StartRuntimeServicesAsync(), "Runtime service startup failed.");
        WriteDesktopStartupDiagnostic("Creating floating window.");
        _floatingWindow = new FloatingWindow();
        _floatingWindow.Opened += (_, _) => RefreshTrayWindowMenuItems();
        _floatingWindow.Closed += (_, _) => _floatingWindow = null;
        if (!IAppHost.GetService<MainConfigHandler>().Data.FloatingWindowSettings.StartupDisplayFloatingWindow)
        {
            _floatingWindow.Hide();
            _floatingWindow.SetUserVisibilityIntent(false);
        }

        desktop.MainWindow = _floatingWindow;

        WriteDesktopStartupDiagnostic("Initializing desktop application chrome.");
        InitializeApp();
        WriteDesktopStartupDiagnostic("Desktop application chrome initialized.");
        if (startupProtocolUri is not null)
            Dispatcher.UIThread.Post(() => HandleProtocolUri(startupProtocolUri), DispatcherPriority.Render);

        AppDomain.CurrentDomain.ProcessExit += CurrentDomainOnProcessExit;
        Dispatcher.UIThread.UnhandledException += App_OnDispatcherUnhandledException;
    }

    private void ShowFirstRunOobe(IClassicDesktopStyleApplicationLifetime desktop, string? startupProtocolUri)
    {
        _isOobeActive = true;
        var oobe = CreateFirstRunOobe(desktop, startupProtocolUri);
        desktop.MainWindow = oobe;
        oobe.Show();
    }

    private FirstRunOobeWindow CreateFirstRunOobe(
        IClassicDesktopStyleApplicationLifetime desktop,
        string? startupProtocolUri)
    {
        var oobe = new FirstRunOobeWindow();
        oobe.Completed += (_, _) =>
        {
            _isOobeActive = false;
            ContinueDesktopStartup(desktop, startupProtocolUri);
            ShowMainWindow();
        };
        oobe.LanguageChanged += (_, _) =>
        {
            var replacement = CreateFirstRunOobe(desktop, startupProtocolUri);
            desktop.MainWindow = replacement;
            replacement.Show();
            oobe.CloseForLanguageChange();
        };
        oobe.Closed += (_, _) =>
        {
            if (!oobe.IsCompleted && !oobe.IsReplacingForLanguageChange)
                RequestDesktopShutdown();
        };
        return oobe;
    }

    /// <summary>
    ///     ������ʵ���Ի����������ڡ�
    ///     �������ڱ������ɼ����Ի����� <see cref="Window.Opened"/> �첽�¼��е�����
    ///     ������ͬ���� <see cref="OnFrameworkInitializationCompleted"/> ������ UI �̡߳�
    /// </summary>
    private static Window CreateDuplicateInstanceDialogHost(
        IClassicDesktopStyleApplicationLifetime _,
        string? startupProtocolUri = null)
    {
        // The overlay dialog is shown through the normal ShowAsync path, but the
        // borderless window is resized to hug the dialog card so only the card is visible.
        var host = new Window
        {
            Width = 420,
            Height = 220,
            WindowStartupLocation = WindowStartupLocation.CenterScreen,
            ShowInTaskbar = false,
            Topmost = true,
            CanResize = false,
            SystemDecorations = SystemDecorations.None,
            // Some Windows compositions still draw a 1px non-client edge plus a
            // DWM shadow for WS_POPUP windows; NoChrome removes both.
            ExtendClientAreaToDecorationsHint = true,
            ExtendClientAreaChromeHints = ExtendClientAreaChromeHints.NoChrome,
            ExtendClientAreaTitleBarHeightHint = 0
        };

        // The hugged window must stay fully opaque: under the Win7 software-rendering
        // path every pixel not covered by the card composites as black. The FA window
        // template does not reliably paint Window.Background, so an explicit full-size
        // surface border carries the card color instead.
        var surface = new Border();
        if (host.TryFindResource("SolidBackgroundFillColorBaseBrush", out var background)
            && background is IBrush backgroundBrush)
            surface.Background = backgroundBrush;
        else
            surface.Background = Brushes.White;
        host.Content = surface;

        // Opened 事件在 Dispatcher 事件循环里异步执行，能安全回到 UI 线程
        host.Opened += async (_, _) =>
        {
            if (startupProtocolUri is not null)
            {
                var sent = await SingleInstanceService.SendCommandAsync(SingleInstanceCommand.UrlPrefix +
                                                                        startupProtocolUri);
                if (sent)
                {
                    host.Close();
                    RequestDesktopShutdown();
                    return;
                }
            }

            var action = await ShowDialogHuggingCardAsync(host, surface);

            switch (action)
            {
                case DuplicateInstanceAction.OpenExisting:
                    // Э�������׷�ʧ�ܺ�����������ԭʼ������ⶪʧ URL ���
                    await SingleInstanceService.SendCommandAsync(startupProtocolUri is null
                        ? SingleInstanceCommand.ShowMainWindow
                        : SingleInstanceCommand.UrlPrefix + startupProtocolUri);
                    break;

                case DuplicateInstanceAction.Restart:
                    // ֪ͨ��һ��ʵ�������������ȴ���ȷ���Է���ʱ����Ӧ
                    await SingleInstanceService.SendCommandAsync(SingleInstanceCommand.Restart);
                    await Task.Delay(300);
                    break;

                case DuplicateInstanceAction.Cancel:
                default:
                    break;
            }

            // ���з�֧���ն��˳���ǰ���ظ���ʵ��
            host.Close();
            RequestDesktopShutdown();
        };

        return host;
    }

    private static async Task<DuplicateInstanceAction> ShowDialogHuggingCardAsync(
        Window host, Border surface)
    {
        var dialogTask = DuplicateInstanceDialog.ShowAsync(host);

        // Wait for the overlay dialog to complete a layout pass, then shrink the
        // borderless window to the card bounds and adopt the card background so
        // no host surface, smoke layer, or gray frame stays visible. Any failure
        // here must degrade to the normal dialog, never take the process down.
        for (var attempt = 0; attempt < 3; attempt++)
        {
            try
            {
                await Dispatcher.UIThread.InvokeAsync(() => { }, DispatcherPriority.Background);
                if (HugDialogCard(host, surface))
                    break;
            }
            catch (Exception exception)
            {
                WriteDesktopStartupDiagnostic("Dialog hug pass failed.", exception);
                break;
            }
        }

        return await dialogTask;
    }

    private static bool HugDialogCard(Window host, Border surface)
    {
        var dialog = host.GetVisualDescendants().OfType<ContentDialog>().FirstOrDefault();
        if (dialog is null || dialog.Bounds.Width < 80 || dialog.Bounds.Height < 80)
            return false;

        // Drop shadows come from Visual.Effect and Border.BoxShadow; once the
        // window hugs the card, their clipped remains show as corner ticks.
        foreach (var visual in host.GetVisualDescendants())
            visual.Effect = null;

        // The template's Panel#LayoutRoot carries the semi-transparent smoke fill
        // behind the card; clear it so only the card color remains.
        foreach (var panel in dialog.GetVisualDescendants().OfType<Panel>())
        {
            if (panel.Name == "LayoutRoot")
                panel.Background = null;
        }

        // Pass 1: the wrapper layers around the card (FADialogHost and friends) are
        // opaque theme surfaces; strip their background and every margin, padding,
        // stroke, and shadow so only the card remains when the window hugs it.
        foreach (var border in host.GetVisualDescendants().OfType<Border>())
        {
            if (!IsVisualDescendant(border, dialog))
            {
                border.BoxShadow = default;
                border.Margin = default;
                border.Padding = default;
                border.BorderThickness = default;
                border.BorderBrush = null;
                border.Background = null;
                // A rounded wrapper leaves its own corners unpainted; the hugged
                // window needs square full-bleed wrappers behind the card.
                border.CornerRadius = default;
            }
        }

        host.UpdateLayout();

        // Pass 2: the ContentDialog control stretches over the whole overlay; the
        // visible card is its largest fully-opaque child surface. Hug that one.
        Border? card = null;
        double largest = 0;
        foreach (var border in dialog.GetVisualDescendants().OfType<Border>())
        {
            if (border.Background is not ISolidColorBrush solid || solid.Color.A != byte.MaxValue)
                continue;

            var area = border.Bounds.Width * border.Bounds.Height;
            if (area > largest)
            {
                largest = area;
                card = border;
            }
        }

        if (card is null || card.Bounds.Width < 80 || card.Bounds.Height < 80)
            return false;

        // The card's rounded corners leave the window corners uncovered, and the
        // software-rendering path does not paint Window.Background there (it shows
        // as black). Paint the full-size wrapper layers with the card color so the
        // exposed slivers blend into the card instead.
        foreach (var border in host.GetVisualDescendants().OfType<Border>())
        {
            if (!IsVisualDescendant(border, dialog)
                && border.Bounds.Width >= dialog.Bounds.Width * 0.9)
            {
                border.Background = card.Background;
                border.CornerRadius = default;
            }
        }

        // The explicit surface border is the reliable full-bleed painter under the
        // software-rendering path; adopt the card color so corner slivers blend.
        if (!ReferenceEquals(surface, card))
            surface.Background = card.Background;

        // The theme strokes the outer card surface; combined with the hugged window
        // edge it reads as a hard frame, so strip wide inner strokes too.
        foreach (var border in dialog.GetVisualDescendants().OfType<Border>())
        {
            if (IsVisualDescendant(border, dialog)
                && border.Bounds.Width >= card.Bounds.Width * 0.95
                && border.Bounds.Height >= card.Bounds.Height * 0.9)
            {
                border.BorderThickness = default;
                border.BorderBrush = null;
            }
        }

        host.UpdateLayout();

        host.Width = Math.Ceiling(card.Bounds.Width);
        host.Height = Math.Ceiling(card.Bounds.Height);
        host.Background = card.Background;
        host.UpdateLayout();

        // The card may reflow after the resize; adjust once more if it drifted.
        if (Math.Abs(card.Bounds.Width - host.Width) > 0.5 ||
            Math.Abs(card.Bounds.Height - host.Height) > 0.5)
        {
            host.Width = Math.Ceiling(card.Bounds.Width);
            host.Height = Math.Ceiling(card.Bounds.Height);
            host.UpdateLayout();
        }

        CenterOnScreen(host);
        ClipWindowToRoundedRegion(host, card.CornerRadius.TopLeft);
        return true;
    }

    private static void ClipWindowToRoundedRegion(Window host, double cornerRadiusDip)
    {
        // Win7 has no reliable per-pixel transparency under the software-rendering
        // path, so clip the window itself to a rounded region instead. The region
        // radius must match the card corner exactly, otherwise the exposed sliver
        // between the two arcs reads as a dark speck. Region coordinates are device
        // pixels; SetWindowRgn owns the region afterwards.
        if (!OperatingSystem.IsWindows())
            return;

        try
        {
            var hwnd = host.TryGetPlatformHandle()?.Handle ?? IntPtr.Zero;
            if (hwnd == IntPtr.Zero)
                return;

            var scale = host.RenderScaling;
            var width = (int)Math.Ceiling(host.Width * scale) + 1;
            var height = (int)Math.Ceiling(host.Height * scale) + 1;
            var radius = (int)Math.Round(cornerRadiusDip * scale);
            if (width <= 0 || height <= 0 || radius <= 0)
                return;

            var region = CreateRoundRectRgn(0, 0, width, height, radius, radius);
            if (region != IntPtr.Zero)
                _ = SetWindowRgn(hwnd, region, true);
        }
        catch
        {
            // Cosmetic-only; a square window is acceptable when clipping fails.
        }
    }

    [DllImport("gdi32.dll")]
    private static extern IntPtr CreateRoundRectRgn(
        int left, int top, int right, int bottom, int ellipseWidth, int ellipseHeight);

    [DllImport("user32.dll")]
    private static extern int SetWindowRgn(IntPtr hWnd, IntPtr hRgn, bool redraw);

    private static bool IsVisualDescendant(Visual candidate, Visual ancestor)
    {
        var current = candidate;
        while (current is not null)
        {
            if (current == ancestor)
                return true;
            current = current.GetVisualParent();
        }

        return false;
    }

    private static void CenterOnScreen(Window host)
    {
        if (!SupportsProgrammaticWindowPositioning)
            return;

        try
        {
            var screen = host.Screens.ScreenFromVisual(host)
                ?? host.Screens.ScreenFromWindow(host)
                ?? (host.Screens.ScreenCount > 0 ? host.Screens.All[0] : null);
            if (screen is null)
                return;

            // Screens work in device pixels while Width/Height are DIPs.
            var scale = host.RenderScaling;
            var area = screen.WorkingArea;
            var width = (host.FrameSize?.Width ?? host.Width) * scale;
            var height = (host.FrameSize?.Height ?? host.Height) * scale;
            host.Position = new PixelPoint(
                area.X + Math.Max(0, (int)Math.Round((area.Width - width) / 2)),
                area.Y + Math.Max(0, (int)Math.Round((area.Height - height) / 2)));
        }
        catch
        {
            // Best-effort centering only; keep the startup position otherwise.
        }
    }

    private static Window CreatePortableDataRootFailureHost(
        IClassicDesktopStyleApplicationLifetime desktop,
        Utils.DesktopDataRootPreparationResult preparation)
    {
        var host = new SecRandomTmpRootWindow();
        host.Opened += async (_, _) =>
        {
            var dialog = new TaskDialog
            {
                XamlRoot = host,
                Title = CR.M_PortableDataDirectoryUnavailableTitle,
                Header = CR.M_PortableDataDirectoryUnavailableTitle,
                Content = string.Format(
                    CR.M_PortableDataDirectoryUnavailableContent,
                    preparation.DataRoot,
                    preparation.ErrorMessage ?? CR.M_UnknownError)
            };
            dialog.Buttons.Add(new TaskDialogButton(CR.C_Close, "close") { IsDefault = true });

            await dialog.ShowAsync();
            host.Close();
            desktop.Shutdown();
        };

        return host;
    }

    /// <summary>
    ///     �������Ժ���ʵ���� IPC �����һ��ʵ��ר�ã���
    ///     �ص����Ժ�̨�̣߳���ͨ�� <see cref="Dispatcher"/> �л��� UI �̡߳�
    /// </summary>
    private void OnIpcCommandReceived(string command)
    {
        Dispatcher.UIThread.Post(() =>
        {
            if (_isOobeActive)
                return;

            switch (command)
            {
                case SingleInstanceCommand.ShowMainWindow:
                    ObserveTask(IAppHost.GetService<ISecurityService>().AuthorizeAsync(
                        SecurityOperation.ToggleMainWindow,
                        () =>
                        {
                            ShowMainWindow();
                            return Task.CompletedTask;
                        }), "Legacy main-window authorization failed.");
                    break;
                case SingleInstanceCommand.Restart:
                    ObserveTask(IAppHost.GetService<ISecurityService>().AuthorizeAsync(
                        SecurityOperation.RestartApplication,
                        () =>
                        {
                            Restart();
                            return Task.CompletedTask;
                        }), "Legacy restart authorization failed.");
                    break;
                default:
                    if (command.StartsWith(SingleInstanceCommand.UrlPrefix, StringComparison.Ordinal))
                        HandleProtocolUri(command[SingleInstanceCommand.UrlPrefix.Length..]);
                    break;
            }
        });
    }

    private Task<IpcResponseEnvelope> OnIpcRequestReceived(IpcRequestEnvelope request,
        CancellationToken cancellationToken)
    {
        if (_isOobeActive)
            return Task.FromResult(new IpcResponseEnvelope(true, "url",
                new IpcBusinessResult("error", "��ʼ������δ��ɡ�", "oobe_required")));

        return IAppHost.GetService<ProtocolCommandRouter>().HandleIpcAsync(request, cancellationToken);
    }

    private void HandleProtocolUri(string value)
    {
        ObserveTask(IAppHost.GetService<ProtocolCommandRouter>().HandleUrlAsync(value),
            "Protocol URL handling failed.");
    }

    private static Window ShowCrashRecoveryPromptOnly(CrashRecoveryPromptOptions promptOptions)
    {
        CrashRecoveryWindow window = new(promptOptions, RestartFromCrashRecoveryPrompt, canIgnore: false);
        window.Closed += (_, _) =>
        {
            if (!window.WasIgnored)
                RequestDesktopShutdown();
        };
        return window;
    }

    private static bool RestartFromCrashRecoveryPrompt()
    {
        return CrashRecoveryRuntime.TryRestartCurrentApp(
            CrashRecoveryRuntime.CreateRestartStartInfos([]),
            RequestDesktopShutdown);
    }

    private void BuildHost(IPlatformServiceRoot platform)
    {
        if (IAppHost.Host is not null) return;
        var mobilePlatform = platform as MobilePlatformServiceRoot;
        var isMobile = mobilePlatform is not null;
        var useMobileUI = isMobile && !mobilePlatform!.UsesDesktopMainView;

        IAppHost.Host = Host
            .CreateDefaultBuilder()
            .UseContentRoot(AppContext.BaseDirectory)
            .ConfigureServices(services =>
            {
                if (isMobile)
                {
                    services.AddPlatformServices(platform);
                    services.AddSingleton<SingleViewHostProvider>();
                    services.AddSingleton<IViewHostProvider>(provider =>
                        provider.GetRequiredService<SingleViewHostProvider>());
                    services.AddViewEngine()
                        .AddView<MobileRootView>(MobilePageIds.Root)
                        .AddView<MainView>(DesktopViewIds.Main)
                        .AddView<SettingsView>(MobilePageIds.Settings)
                        .AddView<RemainingListView>(RemainingListViewService.ViewId);
                    services.AddTransient<MobileViewHost>();
                }
                else
                {
                    services.AddPlatformServices(platform);
                    services.AddSingleton<DesktopViewHostProvider>();
                    services.AddSingleton<IViewHostProvider>(serviceProvider =>
                        serviceProvider.GetRequiredService<DesktopViewHostProvider>());
                    services.AddViewEngine()
                        .AddView<MainView>(DesktopViewIds.Main)
                        .AddView<SettingsView>(DesktopViewIds.Settings)
                        .AddView<RemainingListView>(RemainingListViewService.ViewId, ViewPresentation.Modal);
                }

                // ��־
                services.AddLogging(builder =>
                {
                    if (!isMobile)
                    {
                        builder.AddConsoleFormatter<LoggingConsoleFormatter, ConsoleFormatterOptions>();
                        builder.AddConsole(console => { console.FormatterName = @"secrandom"; });
                    }

                    builder.AddSentry(options =>
                    {
                        // SDK ���������� TelemetryRuntimeService ����˽����ͳһ���ƣ���־ Provider ֻ�����ѳ�ʼ���� SDK��
                        options.InitializeSdk = false;
                        options.MinimumEventLevel = LogLevel.Error;
                        // Sentry Structured Logs Ĭ�Ϲرգ���־ Provider �� SDK ��ʼ��ѡ���Ҫ���á�
                        options.EnableLogs = true;
                    });
#if DEBUG
                    builder.SetMinimumLevel(LogLevel.Trace);
#endif
                });
                services.AddSingleton<ILoggerProvider, FileLoggerProvider>();

                // ����
                services.AddCoreRuntimeServices();
                services.AddSingleton<DeviceUuidStore>();

                services.AddSingleton<ITelemetrySdkAdapter, SentryTelemetrySdkAdapter>();
                services.AddSingleton<TelemetryRuntimeService>();
                services.AddHostedService<OnlineStatusService>();

                // ����
                services.AddTransient<RollCallDrawService>();
                services.AddTransient<LotteryDrawService>();
                services.AddSingleton<RosterTransferService>();
                services.AddSingleton<IRosterQrCameraCaptureFactory, RosterQrCameraCaptureFactory>();
                services.AddHttpClient<RosterSyncTransferService>(client =>
                {
                    client.BaseAddress = new Uri("https://secrandom-sync.sectl.cn/");
                    client.Timeout = TimeSpan.FromSeconds(30);
                });
                if (isMobile)
                {
                    MobilePlatformServiceRoot currentMobilePlatform = mobilePlatform!;
                    services.AddSingleton<MobileMediaLibraryService>();
                    services.AddSingleton<IMobileMediaPlayer>(currentMobilePlatform.MediaPlayer);
                    if (currentMobilePlatform.KeyboardOcclusionSource is { } keyboardOcclusionSource)
                        services.AddSingleton<IMobileKeyboardOcclusionSource>(keyboardOcclusionSource);
                    services.AddSingleton<MobileDrawMediaService>();
                    services.AddSingleton<IMobileUpdateInstaller>(currentMobilePlatform.UpdateInstaller);
                    services.AddHttpClient<MobileUpdateService>();
                }

                services.AddSingleton<IProfileQueryService, ProfileQueryService>();
                services.AddSingleton<RemainingListViewState>();
                services.AddSingleton<RemainingListViewService>();
                services.AddSingleton<DrawProofExportService>();
                services.AddSingleton<IVerificationKernel, ManagedVerificationKernel>();
                services.AddHttpClient<IWitnessClient, WitnessClient>(client =>
                    client.Timeout = TimeSpan.FromSeconds(3));
                services.AddSingleton<DrawProofAttestationService>();
                services.AddHostedService(serviceProvider =>
                    serviceProvider.GetRequiredService<DrawProofAttestationService>());
                services.AddTransient<VerificationDrawCoordinator>();
                services.AddSingleton<SettingsSearchService>();
                services.AddSingleton<FirstRunOobeService>();
                services.AddSingleton<OobeDataSetupService>();
                services.AddSingleton<IArchivePostImportHooks, DesktopArchivePostImportHooks>();
                services.AddSingleton<IImportExportService, ImportExportService>();
                services.AddSingleton<ISentryFeedbackClient, SentryFeedbackClient>();
                services.AddSingleton<IUserFeedbackService, UserFeedbackService>();
                services.AddHostedService<AutomaticBackupService>();
                services.AddHostedService<TaskBarIconService>();
                services.AddSingleton<GlobalShortcutService>();
                services.AddHostedService(serviceProvider =>
                    serviceProvider.GetRequiredService<GlobalShortcutService>());
                services.AddSingleton<DesktopIntegrationService>();
                services.AddSingleton<IExternalLauncher, ExternalLauncher>();
                services.AddHttpClient("updates", client => client.Timeout = TimeSpan.FromSeconds(30));
                services.AddSingleton<UpdateCenterService>(serviceProvider => new UpdateCenterService(
                    serviceProvider.GetRequiredService<MainConfigHandler>(),
                    serviceProvider.GetRequiredService<ILogger<UpdateCenterService>>(),
                    serviceProvider.GetRequiredService<IHttpClientFactory>().CreateClient("updates")));
                services.AddSingleton<IUpdateNotificationService, UpdateNotificationService>();
                services.AddHostedService<UpdateScheduler>();
                services.AddSingleton<ProtocolCommandRouter>();
                services.AddSingleton<ISpeechProvider, SystemSpeechProvider>();
                services.AddSingleton<ISpeechProvider, EdgeTtsSpeechProvider>();
                services.AddSingleton<ISpeechAudioPlayer, SpeechAudioPlayer>();
                services.AddSingleton<IVoiceAnnouncementService, VoiceAnnouncementService>();
                services.AddSingleton<NotificationService>();
                // Local-only REST endpoint for the SecAgent connector. It intentionally has no UI/settings registration.
                services.AddHostedService<SecAgentHttpHostedService>();
                services.AddHostedService<SecAgentPluginBootstrapHostedService>();
                services.AddSingleton(serviceProvider => new MusicLibraryService(
                    serviceProvider.GetRequiredService<MainConfigHandler>(),
                    serviceProvider.GetRequiredService<ILogger<MusicLibraryService>>(),
                    attachedSettingsProfileService: serviceProvider.GetRequiredService<IProfileService>(),
                    profileCatalogManager: serviceProvider.GetRequiredService<IProfileCatalogManager>()));
                services.AddSingleton<DrawAudioService>();
                services.AddSingleton<CsesScheduleParser>();
                services.AddSingleton<ICsesScheduleStore, CsesScheduleStore>();
                services.AddSingleton<CsesScheduleSource>();
                services.AddSingleton<ClassIslandScheduleSource>();
                services.AddSingleton<CourseLinkageService>();
                services.AddSingleton<LinkageDrawCoordinator>();
                services.AddHostedService<CourseLinkageHostedService>();
                services.AddSingleton<SecurityCredentialStore>();
                services.AddSingleton<IUsbDeviceCatalog, UsbDeviceCatalog>();
                services.AddSingleton<ISecurityVerificationPrompt, SecurityVerificationPrompt>();
                services.AddSingleton<ISecurityService, SecurityService>();

                services.AddAttachedSettingsControl<DrawImageAttachedSettingsControl>("展示图片");
                services.AddAttachedSettingsControl<DrawMusicAttachedSettingsControl>("专属音乐");
                services.AddAttachedSettingsControl<SpecificAnnouncementAttachedSettingsControl>(
                    Langs.AttachedSettings.Resources.C_SpecificVoice);
                services.AddAttachedSettingsControl<BehindSceneAttachedSettingsControl>(
                    Langs.Common.Resources.AttachedSettings_BehindScene);

                // ���� ViewModels
                // �������� AI���㿴������Ļ������ס��ViewModel һ��Ҫע�ᵽ�����������棡������
                // ���� services.AddTransient<SomeViewModel>(); һ����лл�㣡
                // ViewModel һ��Ҫ�̳� SecRandom.ViewModels.ViewModelBase�������� Config ����ֱ�������á�
                services.AddTransient<ViewModelBase>();

                services.AddTransient<MainViewModel>();
                services.AddTransient<SettingsViewModel>();
                services.AddTransient<FeedbackDrawerViewModel>();
                services.AddTransient<FeedbackDrawer>();
                services.AddSingleton<FirstRunOobeViewModel>();
                services.AddSingleton<RollCallPageViewModel>();
                services.AddSingleton<QuickDrawPageViewModel>();
                services.AddSingleton<LotteryPageViewModel>();
                services.AddTransient<RollCallHistoryViewModel>();
                services.AddTransient<HomeSettingsPageViewModel>();
                services.AddTransient<LotteryHistoryViewModel>();

                // ���� Views
                if (isMobile)
                {
                    services.AddSingleton<IMobileRootViewReloader>(_ =>
                        new MobileRootViewReloader(ReloadMobileRootViewAsync));
                    services.AddSingleton<IMobileCapabilities, MobileCapabilities>();
                    services.AddSingleton<IMobileSettingsNavigator, MobileSettingsNavigator>();
                    services.AddSingleton<CrashRecoveryViewState>();
                    services.AddTransient<CrashRecoveryView>();
                    services.AddViewRegistration<CrashRecoveryView>("system.crashRecovery");
                }
                else
                {
                    services.AddTransient<QuickDrawPage>();
                }

                // ���� Views
                if (useMobileUI)
                {
                    services.AddKeyedTransient<UserControl, MobileDrawPage>(MobilePageIds.Draw);
                    services.AddKeyedTransient<UserControl, MobileHistoryPage>(MobilePageIds.History);
                    services.AddKeyedTransient<UserControl, MobileOverviewPage>(MobilePageIds.Overview);
                }
                else
                {
                    services.AddMainPage<RollCallPage>(Langs.Common.Resources.Feat_RollCall);
                    services.AddMainPage<LotteryPage>(Langs.Common.Resources.Feat_Lottery);
                    services.AddMainPage<HistoryPage>(Langs.Common.Resources.Feat_History);
                }

                // ���ý��� Views
                services.AddSettingsPage<LogViewerSettingsPage>(Langs.SettingsPages.LogViewer.Resources.Page_Title);

                // �ƶ��˱���Ŀ¼�ǣ�����ҳ��������ʵ�֣�ֻ��ϵͳ��װ�߽粻ͬ�ĸ���ҳ�����ƶ�ʵ�֡�
                if (isMobile && useMobileUI)
                {
                    services.AddSettingsPage<MobileSettingsCatalogPage>(MobileResources.P_Settings);
                }
                else
                {
                    services.AddSettingsPage<HomeSettingsPage>(Langs.Common.Resources.Settings_Home);
                    services.AddSettingsPageSeparator();
                }

                services.AddGroup(new PageGroupInfo(
                    Langs.Common.Resources.Settings_General, "settings.general", FluentIcons.SettingsFilled));
                services.AddSettingsPage<BasicSettingsPage>(Langs.Common.Resources.Settings_Basic);
                if (!isMobile)
                {
                    // �ֻ�û�а�ȫ����֧��
                    services.AddSettingsPage<SecuritySettingsPage>(Langs.Common.Resources.Settings_Security);
                }
                services.AddSettingsPage<PrivacySettingsPage>(Langs.SettingsPages.General.Privacy.Resources
                    .Page_Title);
                services.AddSettingsPage<VerificationSettingsPage>(Langs.SettingsPages.General.Verification
                    .Resources.Page_Title);
                services.AddSettingsPage<BackupSettingsPage>(Langs.Common.Resources.Settings_Backup);

                services.AddGroup(new PageGroupInfo(
                    Langs.Common.Resources.Settings_Personalized, "settings.personalized",
                    FluentIcons.ColorFilled));
                services.AddSettingsPage<AppearanceSettingsPage>(Langs.Common.Resources.Settings_Appearance);
                if (!isMobile)
                {
                    // �ֻ�û�и���
                    services.AddSettingsPage<FloatingWindowSettingsPage>(Langs.Common.Resources
                        .Settings_FloatingWindow);
                }
                services.AddSettingsPage<MusicSettingsPage>(Langs.SettingsPages.Personalized.Music.Resources
                    .Page_Title);
                services.AddSettingsPage<LinkageSettingsPage>(Langs.Common.Resources.Settings_Linkage);
                services.AddSettingsPage<MoreSettingsPage>(Langs.SettingsPages.More.Resources.Page_Title);

                services.AddSettingsPageSeparator();

                services.AddGroup(new PageGroupInfo(
                    Langs.Common.Resources.Settings_RosterManagement, "settings.listManagement",
                    FluentIcons.PeopleListFilled));
                services.AddSettingsPage<RollCallListSettingsPage>(Langs.SettingsPages.ListManagement.RollCallList
                    .Resources.Page_Title);
                services.AddSettingsPage<LotteryListSettingsPage>(Langs.SettingsPages.ListManagement.LotteryList
                    .Resources.Page_Title);

                services.AddGroup(new PageGroupInfo(
                    Langs.Common.Resources.Settings_Draw, "settings.picking", FluentIcons.SettingsFilled));
                services.AddSettingsPage<DefaultDrawSettingsPage>(
                    Langs.SettingsPages.Picking.Resources.Page_Default);
                services.AddSettingsPage<RollCallDrawSettingsPage>(Langs.SettingsPages.Picking.Resources
                    .Page_RollCall);
                services.AddSettingsPage<QuickDrawSettingsPage>(
                    Langs.SettingsPages.Picking.Resources.Page_QuickDraw);
                services.AddSettingsPage<LotteryDrawSettingsPage>(
                    Langs.SettingsPages.Picking.Resources.Page_Lottery);

                services.AddGroup(new PageGroupInfo(
                    Langs.Common.Resources.Settings_Notification, "settings.notification",
                    FluentIcons.CommentNoteFilled));
                if (!OperatingSystem.IsIOS())
                {
                    // iOS ��֧�� miniaudio
                    services.AddSettingsPage<VoiceSettingsPage>(Langs.Common.Resources.Settings_Voice);
                }
                if (!isMobile)
                {
                    // �ֻ�û�и���
                    services.AddSettingsPage<DefaultNotificationSettingsPage>(Langs.SettingsPages.Notification.Resources
                        .Page_Title);
                    services.AddSettingsPage<RollCallNotificationSettingsPage>(Langs.Common.Resources
                        .Settings_RollCallNotification);
                    services.AddSettingsPage<QuickDrawNotificationSettingsPage>(Langs.Common.Resources
                        .Settings_QuickDrawNotification);
                    services.AddSettingsPage<LotteryNotificationSettingsPage>(Langs.Common.Resources
                        .Settings_LotteryNotification);
                }

                services.AddGroup(new PageGroupInfo(
                    Langs.Common.Resources.Feat_History, "settings.history", FluentIcons.HistoryFilled));
                services.AddSettingsPage<HistoryManagementSettingsPage>(Langs.Common.Resources
                    .Settings_HistoryManagement);
                services.AddSettingsPage<RollCallHistorySettingsPage>(Langs.Common.Resources.Feat_RollCallHistory);
                services.AddSettingsPage<LotteryHistorySettingsPage>(Langs.Common.Resources.Feat_LotteryHistory);

                services.AddSettingsPageSeparator(isHide: true);
                // services.AddSettingsPage<PluginsSettingsPage>(Langs.SettingsPages.Plugins.Overview.Resources
                //     .Page_Title);

                // �ײ�
                services.AddSettingsPage<UpdateSettingsPage>(Langs.Common.Resources.Settings_Update);
                services.AddSettingsPage<AboutSettingsPage>(Langs.Common.Resources.Settings_About);

                services.AddSettingsPageSeparator(PageLocation.Bottom, isHide: true);
                services.AddSettingsPage<DebugSettingsPage>(
                    Langs.SettingsPages.Debug.DebugStrings.Get("Page_Title"));
            })
            .Build();

        ApplyBehindSceneAttachedSettingsRegistration(
            IAppHost.GetService<MainConfigHandler>().Data.General.InternalSettingsEnabled);

        var logger = IAppHost.GetService<ILogger<App>>();

        logger.LogInformation(@"SecRandom {VERSION} (Codename: {CODENAME})", GlobalConstants.Version,
            GlobalConstants.CodeName);
        logger.LogInformation(@"Copyright by 椰汁(2025~{YEAR})  Licensed under GPL3.0", DateTime.Now.Year);
        logger.LogInformation("Host built.");

        // ˢ�¸��Ի�����
        RefreshPersonalizedSettings();

        IAppHost.GetService<IProfileService>();

        // RESOURCES TEST
        var isVisible = false;
        if (GlobalConstants.IsDevelopment && isVisible)
            IAppHost.GetService<SettingsSearchService>().LogTestInformation();
    }

    private static void ApplyBehindSceneAttachedSettingsRegistration(bool enabled)
    {
        if (enabled)
        {
            AttachedSettingsRegistryExtensions.RegisterAttachedSettingsControl<BehindSceneAttachedSettingsControl>(
                Langs.Common.Resources.AttachedSettings_BehindScene);
        }
        else
        {
            AttachedSettingsRegistryExtensions.UnregisterAttachedSettingsControl<BehindSceneAttachedSettingsControl>();
        }
    }

    private static MainConfigModel LoadStartupSettings(MainConfigModel fallback)
    {
        if (!File.Exists(fallback.ConfigFilePath))
            return fallback;

        try
        {
            return JsonSerializer.Deserialize<MainConfigModel>(
                File.ReadAllText(fallback.ConfigFilePath),
                ConfigServiceBase.JsonOptions) ?? fallback;
        }
        catch
        {
            return fallback;
        }
    }

    public void InitializeApp()
    {
        var taskBarIconService = IAppHost.Host!.Services
            .GetServices<IHostedService>().OfType<TaskBarIconService>().First();
        var menu = this.FindResource(@"AppMenu") as NativeMenu;
        taskBarIconService.MainTaskBarIcon.Menu = menu;
        _floatingWindowMenuItem = menu?.Items.ElementAtOrDefault(3) as NativeMenuItem;
        RefreshTrayWindowMenuItems();
        taskBarIconService.MainTaskBarIcon.IsVisible = true;
        taskBarIconService.MainTaskBarIcon.Clicked += MainTaskBarIconOnClicked;
        IAppHost.GetService<DesktopIntegrationService>().EnsureConfiguredIntegrations();

        if (IAppHost.GetService<MainConfigHandler>().Data.General.Basic.ShowStartupWindow)
            Dispatcher.UIThread.Post(ShowMainWindow, DispatcherPriority.Render);

        AppStarted?.Invoke(this, EventArgs.Empty);
    }

    public void Stop()
    {
        ObserveTask(StopAsync(), "Application shutdown failed.");
    }

    public async Task StopAsync()
    {
        await StopAsync(requestLifetimeShutdown: true).ConfigureAwait(false);
    }

    private async Task StopAsync(bool requestLifetimeShutdown)
    {
        lock (_shutdownGate)
        {
            if (_isStopping)
            {
                IAppHost.TryGetService<ILogger<App>>()?
                    .LogDebug("Skipping duplicate application shutdown request.");
                return;
            }

            _isStopping = true;
        }

        IAppHost.TryGetService<ILogger<App>>()?
            .LogInformation("Stopping application.");

        AppStopping?.Invoke(this, EventArgs.Empty);

        if (_floatingWindow != null) _floatingWindow.CanClose = true;

        IAppHost.GetService<MainConfigHandler>().Save();
        IAppHost.GetService<IProfileService>().SaveProfile();
        await ShutdownTelemetryAsync().ConfigureAwait(false);

        IHost? host = IAppHost.Host;
        if (host is not null)
        {
            await host.StopAsync(TimeSpan.FromSeconds(5)).ConfigureAwait(false);
            host.Dispose();
        }

        IAppHost.Host = null;

        // �ͷŵ�ʵ�� Mutex �� IPC �ܵ�
        SingleInstanceService.Instance.Dispose();

        if (requestLifetimeShutdown)
            RequestDesktopShutdown();
    }

    public async void Restart()
    {
        var startInfos = CrashRecoveryRuntime.CreateRestartStartInfos([]);

        TrySaveConfigForCrashRecovery();
        SingleInstanceService.Instance.Dispose();

        if (!CrashRecoveryRuntime.TryRestartCurrentApp(startInfos, static () => { }))
        {
            IAppHost.TryGetService<ILogger<App>>()?
                .LogError("Application restart launch phase failed.");
            return;
        }

        try
        {
            await StopAsync(requestLifetimeShutdown: false).ConfigureAwait(false);
        }
        catch (Exception ex)
        {
            IAppHost.TryGetService<ILogger<App>>()?
                .LogError(ex, "Application restart shutdown phase failed.");
            return;
        }

        RequestDesktopShutdown();
    }

    public async Task RestartThroughLauncherAsync()
    {
        var launcherName = OperatingSystem.IsWindows() ? "SecRandomLauncher.exe" : "SecRandomLauncher";
        var launcherPath = Path.Combine(Utils.PackageRoot, launcherName);
        if (!File.Exists(launcherPath))
            throw new FileNotFoundException("��Я�� Launcher �����ڡ�", launcherPath);

        await StopAsync(requestLifetimeShutdown: false).ConfigureAwait(false);
        var startInfo = new ProcessStartInfo(launcherPath)
        {
            WorkingDirectory = Utils.PackageRoot,
            UseShellExecute = false
        };
        Process.Start(startInfo);
        RequestDesktopShutdown();
    }

    private void App_OnDispatcherUnhandledException(object sender, DispatcherUnhandledExceptionEventArgs e)
    {
        TrySaveConfigForCrashRecovery();
        TryLogCritical(e.Exception);
        ObserveTask(CaptureUnhandledExceptionAsync(e.Exception), "Unhandled exception telemetry capture failed.");

        e.Handled = DispatcherCrashRecovery.TryRecover(
            e.Exception,
            CrashRecoveryRuntime.TryCreateCurrentProcessPromptOptions,
            ShowCrashRecoveryPrompt,
            CrashRecoveryRuntime.TryHandlePromptDisplayFailure,
            CrashRecoveryRuntime.TryHandleFatalException,
            RequestDesktopShutdown);
    }

    private static bool ShowCrashRecoveryPrompt(CrashRecoveryPromptOptions promptOptions)
    {
        CrashRecoveryWindow window = new(promptOptions, RestartFromCrashRecoveryCurrentApp);
        window.Closed += (_, _) =>
        {
            if (!window.WasIgnored)
                RequestDesktopShutdown();
        };
        window.Show();
        return true;
    }

    private static bool RestartFromCrashRecoveryCurrentApp()
    {
        Current.Restart();
        return true;
    }

    private static void TrySaveConfigForCrashRecovery()
    {
        try
        {
            IAppHost.TryGetService<MainConfigHandler>()?.Save();
            IAppHost.TryGetService<IProfileService>()?.SaveProfile();
        }
        catch (Exception ex)
        {
            IAppHost.TryGetService<ILogger<App>>()?
                .LogError(ex, "Crash-recovery persistence failed.");
        }
    }

    private static void TryLogCritical(Exception exception)
    {
        try
        {
            IAppHost.TryGetService<ILogger<App>>()?
                .LogCritical(exception, "Unhandled application exception.");
        }
        catch
        {
        }
    }

    private void CurrentDomainOnProcessExit(object? sender, EventArgs e)
    {
        try
        {
            IAppHost.TryGetService<MainConfigHandler>()?.Save();
            IAppHost.TryGetService<IProfileService>()?.SaveProfile();
        }
        catch (Exception ex)
        {
            IAppHost.TryGetService<ILogger<App>>()?
                .LogError(ex, "Process-exit persistence failed.");
        }
    }

    /// <summary>
    /// ��ʼ��ң������ʱ������ <see cref="StartRuntimeServicesAsync"/> �� Host ����ǰ���á�
    /// </summary>
    private static async Task InitializeRuntimeServicesAsync()
    {
        try
        {
            var telemetry = IAppHost.GetService<TelemetryRuntimeService>();
            await telemetry.InitializeAsync().ConfigureAwait(false);
            // await SendSentryTestEventAsync(telemetry).ConfigureAwait(false);
            // Dispatcher.UIThread.Post(() => throw new InvalidOperationException("SENTRY_TEST_FAKE_ERROR_UNHANDLED"));
        }
        catch (Exception ex)
        {
            IAppHost.TryGetService<ILogger<App>>()?
                .LogError(ex, "Telemetry initialization failed.");
        }
    }

    /// <summary>
    /// ��˳������ң��� Host��ȷ�� SDK �� HostedService ����ǰ������
    /// </summary>
    private static async Task StartRuntimeServicesAsync()
    {
        await InitializeRuntimeServicesAsync().ConfigureAwait(false);
        await IAppHost.Host!.StartAsync().ConfigureAwait(false);
    }

    private static void ObserveTask(Task task, string failureMessage)
    {
        _ = ObserveTaskAsync(task, failureMessage);
    }

    private static async Task ObserveTaskAsync(Task task, string failureMessage)
    {
        try
        {
            await task.ConfigureAwait(false);
        }
        catch (Exception ex)
        {
            WriteDesktopStartupDiagnostic(failureMessage, ex);
            IAppHost.TryGetService<ILogger<App>>()?
                .LogError(ex, failureMessage);
        }
    }

    private static void WriteDesktopStartupDiagnostic(string message, Exception? exception = null)
    {
        try
        {
            string directory = Utils.GetFilePath("logs");
            Directory.CreateDirectory(directory);
            string entry = $"{DateTimeOffset.Now:O} [desktop-startup] {message}{Environment.NewLine}";
            if (exception is not null)
                entry += exception + Environment.NewLine;
            File.AppendAllText(Path.Combine(directory, "desktop-startup.log"), entry);
        }
        catch
        {
            System.Diagnostics.Debug.WriteLine($"[desktop-startup] {message}\n{exception}");
        }
    }

    private static async Task CaptureUnhandledExceptionAsync(Exception exception)
    {
        try
        {
            TelemetryRuntimeService? telemetry = IAppHost.TryGetService<TelemetryRuntimeService>();
            if (telemetry is not null)
                await telemetry.CaptureExceptionAsync(exception).ConfigureAwait(false);
        }
        catch (Exception ex)
        {
            IAppHost.TryGetService<ILogger<App>>()?
                .LogError(ex, "Unhandled exception telemetry capture failed.");
        }
    }

    private static async Task SendSentryTestEventAsync(TelemetryRuntimeService telemetry)
    {
        var exception = new InvalidOperationException("SENTRY_TEST_FAKE_ERROR");
        var logger = IAppHost.GetService<ILogger<App>>();

        logger.LogError(exception, "SENTRY_TEST_FAKE_ERROR log event.");
        await telemetry.CaptureExceptionAsync(exception).ConfigureAwait(false);
        await telemetry.FlushAsync(TimeSpan.FromSeconds(5)).ConfigureAwait(false);
    }

    private static async Task ShutdownTelemetryAsync()
    {
        try
        {
            TelemetryRuntimeService? telemetry = IAppHost.TryGetService<TelemetryRuntimeService>();
            if (telemetry is not null)
                await telemetry.ShutdownAsync(TimeSpan.FromSeconds(5)).ConfigureAwait(false);
        }
        catch (Exception ex)
        {
            IAppHost.TryGetService<ILogger<App>>()?
                .LogError(ex, "Telemetry shutdown failed.");
        }
    }

    private static void RequestDesktopShutdown()
    {
        if (_desktopLifetime is null)
            return;

        if (Dispatcher.UIThread.CheckAccess())
        {
            _desktopLifetime.Shutdown();
            return;
        }

        Dispatcher.UIThread.Post(() => _desktopLifetime?.Shutdown());
    }

    public static void InitializeLanguages(CultureInfo cultureInfo)
    {
        CultureInfo.CurrentCulture = cultureInfo;
        CultureInfo.CurrentUICulture = cultureInfo;
        CultureInfo.DefaultThreadCurrentCulture = cultureInfo;
        CultureInfo.DefaultThreadCurrentUICulture = cultureInfo;
        Langs.FirstRunOobe.Resources.Culture = cultureInfo;
        Langs.MainPages.QuickDraw.Resources.Culture = cultureInfo;
    }

    /// <summary>
    ///     �� XAML ��Դ������ɺ�����Ӧ��������ã�����ɫ������ģʽ����
    ///     ���� DI������ BuildHost ֮ǰ���ã�ȷ���ظ�ʵ���Ի���Ҳ�ܸ����û����⡣
    /// </summary>
    private void ApplyStartupAppearance(AppearanceSettingsConfig settings)
    {
        ApplyThemeSettings(settings);

        Resources[@"NavigationViewItemOnLeftIconBoxHeight"] = 20.0;
    }

    public void RefreshPersonalizedSettings()
    {
        var config = IAppHost.GetService<MainConfigHandler>().Data;
        var settings = config.Appearance;

        var fontFamily = settings.Font;
        if (fontFamily == @"MiSans")
            fontFamily = @"avares://SecRandom/Assets/Fonts/MiSans/#MiSans";

        // ����ģʽ
        ApplyThemeSettings(settings);

        // ����ɫ
        Resources[@"ContentControlThemeFontFamily"] = Resources[@"AppFontFamily"] = new FontFamily(fontFamily);
        Resources[@"AppFontWeight"] = Enum.Parse<FontWeight>(settings.FontWeight.ToString());
    }

    private void ApplyThemeSettings(AppearanceSettingsConfig settings)
    {
        var useSystemTheme = settings.Theme == ThemeMode.Auto;
        var requestedThemeVariant = settings.Theme switch
        {
            ThemeMode.Auto => ThemeVariant.Default,
            ThemeMode.Light => ThemeVariant.Light,
            ThemeMode.Dark => ThemeVariant.Dark,
            _ => ThemeVariant.Default
        };

        var fluentAvaloniaTheme = this.FindResource(@"FluentAvaloniaTheme") as FluentAvaloniaTheme;
        if (fluentAvaloniaTheme is not null)
        {
            // Configure system tracking before an explicit variant so FluentAvalonia does
            // not overwrite the requested variant while it is changing its resource set.
            if (fluentAvaloniaTheme.PreferSystemTheme != useSystemTheme)
                fluentAvaloniaTheme.PreferSystemTheme = useSystemTheme;

            if (settings.ThemeColorMode == ThemeColorMode.System)
            {
                if (fluentAvaloniaTheme.CustomAccentColor is not null)
                    fluentAvaloniaTheme.CustomAccentColor = null;
                if (!fluentAvaloniaTheme.PreferUserAccentColor)
                    fluentAvaloniaTheme.PreferUserAccentColor = true;
            }
            else
            {
                if (fluentAvaloniaTheme.PreferUserAccentColor)
                    fluentAvaloniaTheme.PreferUserAccentColor = false;
                if (fluentAvaloniaTheme.CustomAccentColor is not { } accentColor || accentColor != settings.ThemeColor)
                    fluentAvaloniaTheme.CustomAccentColor = settings.ThemeColor;
            }
        }

        if (!Equals(RequestedThemeVariant, requestedThemeVariant) && requestedThemeVariant != ThemeVariant.Default)
            RequestedThemeVariant = requestedThemeVariant;
    }

    #region Windows

    public static void ShowMainWindow() => ShowMainWindow(null);

    public static void ShowMainWindow(string? pageId)
    {
        ObserveTask(ShowMainWindowCoreAsync(pageId), "Failed to show main window.");
    }

    private static async Task ShowMainWindowCoreAsync(string? pageId = null)
    {
        TelemetryRuntimeService? telemetry = IAppHost.TryGetService<TelemetryRuntimeService>();
        using var transaction = telemetry?.StartTransaction("ui.main_window", "ui.navigation");

        try
        {
            WriteDesktopStartupDiagnostic("Showing main window.");
            if (_mainWindow is null)
            {
                WriteDesktopStartupDiagnostic("Creating main window and view host.");
                var mainWindow = _mainWindow = new MainWindow(MainWindowSettingsScope.Primary)
                {
                    Title = @"SecRandom"
                };
                var host = new DesktopWindowViewHost(mainWindow, DesktopViewIds.Main);
                IAppHost.GetService<DesktopViewHostProvider>().RegisterHost(host);
                mainWindow.Closed += (_, _) =>
                {
                    if (ReferenceEquals(_mainWindow, mainWindow))
                        _mainWindow = null;
                };
            }

            await IAppHost.GetService<IViewEngine>().ShowAsync(
                DesktopViewIds.Main,
                new ViewShowOptions { HostId = DesktopViewIds.Main }).ConfigureAwait(true);
            WriteDesktopStartupDiagnostic("Main window view displayed.");
            if (!string.IsNullOrWhiteSpace(pageId))
                MainView.Current?.SelectNavigationItemById(pageId);
            transaction?.Finish(SpanStatus.Ok);
        }
        catch (Exception ex)
        {
            WriteDesktopStartupDiagnostic("Main window display failed.", ex);
            transaction?.Finish(ex, SpanStatus.InternalError);
            IAppHost.TryGetService<ILogger<App>>()?.LogError(ex, "Failed to show main window.");
            throw;
        }
    }

    public static void ToggleMainWindow(string? pageId = null)
    {
        if (pageId == "main.lottery" && !IAppHost.GetService<IFeatureAvailabilityService>().IsLotteryEnabled)
            return;

        ObserveTask(IAppHost.GetService<ISecurityService>().AuthorizeAsync(
            SecurityOperation.ToggleMainWindow,
            () => ShowMainWindowCoreAsync(pageId)), "Main window authorization failed.");
    }

    public static void SetMainWindowVisibility(string action, string? pageId = null)
    {
        ObserveTask(SetMainWindowVisibilityCoreAsync(action, pageId), "Main window visibility update failed.");
    }

    private static async Task SetMainWindowVisibilityCoreAsync(string action, string? pageId)
    {
        if (pageId == "main.lottery" && !IAppHost.GetService<IFeatureAvailabilityService>().IsLotteryEnabled)
            return;

        var shouldShow = action switch
        {
            "show" => true,
            "hide" => false,
            _ => _mainWindow is not { IsVisible: true }
        };
        if (shouldShow)
        {
            await ShowMainWindowCoreAsync(pageId);
        }
        else
        {
            _mainWindow?.Hide();
        }
    }

    internal static void RequestExitFromMainWindow()
    {
        ObserveTask(IAppHost.GetService<ISecurityService>().AuthorizeAsync(
            SecurityOperation.ExitApplication,
            () =>
            {
                Current.Stop();
                return Task.CompletedTask;
            }), "Main window exit authorization failed.");
    }

    public static void ToggleFloatingWindow()
    {
        ObserveTask(IAppHost.GetService<ISecurityService>().AuthorizeAsync(
            SecurityOperation.ToggleFloatingWindow,
            () =>
            {
                if (_floatingWindow is { IsVisible: true })
                {
                    _floatingWindow.Hide();
                    _floatingWindow.SetUserVisibilityIntent(false);
                }
                else if (_floatingWindow is not null)
                {
                    _floatingWindow.SetUserVisibilityIntent(true);
                    if (!_floatingWindow.IsHiddenByCourseLinkage)
                        RestoreWithoutActivating(_floatingWindow);
                }

                Current.RefreshTrayWindowMenuItems();
                return Task.CompletedTask;
            }), "Floating window authorization failed.");
    }

    public static void SetFloatingWindowVisibility(string action)
    {
        var shouldShow = action switch
        {
            "show" => true,
            "hide" => false,
            _ => _floatingWindow is not { UserWantsVisible: true }
        };
        if (shouldShow && _floatingWindow is not null)
        {
            _floatingWindow.SetUserVisibilityIntent(true);
            if (!_floatingWindow.IsHiddenByCourseLinkage)
                RestoreWithoutActivating(_floatingWindow);
        }
        else if (!shouldShow)
        {
            _floatingWindow?.Hide();
            _floatingWindow?.SetUserVisibilityIntent(false);
        }

        Current.RefreshTrayWindowMenuItems();
    }

    public static void ShowSettingsWindow() => ShowSettingsWindow(null);

    public static void ShowSettingsWindow(string? pageId)
    {
        ObserveTask(IAppHost.GetService<ISecurityService>().AuthorizeSettingsAsync(
            async () =>
            {
                await ShowSettingsWindowCoreAsync();
                SettingsView.Current?.ExitPreview();
                if (!string.IsNullOrWhiteSpace(pageId))
                    SettingsView.Current?.NavigateToPage(pageId);
            },
            () =>
            {
                Dispatcher.UIThread.Post(() =>
                {
                    ObserveTask(ShowSettingsPreviewAsync(pageId),
                        "Settings preview display failed.");
                }, DispatcherPriority.Background);
                return Task.CompletedTask;
            }), "Settings window authorization failed.");
    }

    private static async Task ShowSettingsPreviewAsync(string? pageId)
    {
        await ShowSettingsWindowCoreAsync();
        if (!string.IsNullOrWhiteSpace(pageId))
            SettingsView.Current?.NavigateToPreviewPage(pageId);
        else
            SettingsView.Current?.EnterPreview();
    }

    public static void SetSettingsWindowVisibility(string action, string pageId, bool preview)
    {
        ObserveTask(SetSettingsWindowVisibilityCoreAsync(action, pageId, preview),
            "Settings window visibility update failed.");
    }

    private static async Task SetSettingsWindowVisibilityCoreAsync(string action, string pageId, bool preview)
    {
        var shouldShow = action switch
        {
            "show" => true,
            "hide" => false,
            _ => _settingsWindow is not { IsVisible: true }
        };
        if (shouldShow)
        {
            await ShowSettingsWindowCoreAsync();
            SettingsView.Current?.NavigateToPage(pageId);
        }
        else
        {
            _settingsWindow?.Hide();
        }
    }

    private static async Task ShowSettingsWindowCoreAsync()
    {
        TelemetryRuntimeService? telemetry = IAppHost.TryGetService<TelemetryRuntimeService>();
        using var transaction = telemetry?.StartTransaction("ui.settings_window", "ui.navigation");

        try
        {
            if (_settingsWindow is null)
            {
                var settingsWindow = _settingsWindow = new MainWindow(MainWindowSettingsScope.Settings)
                {
                    Title = @"SecRandom"
                };
                var host = new DesktopWindowViewHost(settingsWindow, DesktopViewIds.Settings);
                IAppHost.GetService<DesktopViewHostProvider>().RegisterHost(host);
                settingsWindow.Closed += (_, _) =>
                {
                    if (ReferenceEquals(_settingsWindow, settingsWindow))
                        _settingsWindow = null;
                };
            }

            await IAppHost.GetService<IViewEngine>().ShowAsync(
                DesktopViewIds.Settings,
                new ViewShowOptions { HostId = DesktopViewIds.Settings }).ConfigureAwait(true);
            transaction?.Finish(SpanStatus.Ok);
        }
        catch (Exception ex)
        {
            transaction?.Finish(ex, SpanStatus.InternalError);
            IAppHost.TryGetService<ILogger<App>>()?.LogError(ex, "Failed to show settings window.");
            throw;
        }
    }

    public static void ShowQuickDrawWindow()
    {
        ObserveTask(ShowQuickDrawWindowAsync(), "Quick draw window action failed.");
    }

    public static void ShowQuickDrawNotificationWindow(
        IReadOnlyCollection<string> items,
        int autoCloseTime,
        bool animate,
        bool preserveQuickDrawResult,
        NotificationChannelSettings windowSettings,
        bool showPreview)
    {
        Dispatcher.UIThread.Post(() => ObserveTask(
            ShowQuickDrawNotificationWindowAsync(items, autoCloseTime, animate, preserveQuickDrawResult, windowSettings,
                showPreview),
            "Quick draw notification window action failed."));
    }

    public static Task ShowQuickDrawNotificationPreviewWindowAsync(NotificationChannelSettings windowSettings)
    {
        return Dispatcher.UIThread.InvokeAsync(() =>
        {
            _quickDrawNotificationSettings = windowSettings;
            var quickDraw = IAppHost.GetService<QuickDrawPageViewModel>();
            quickDraw.NotificationOpacity = Math.Clamp(windowSettings.Transparency, 20, 100);
            var window = GetOrCreateQuickDrawWindow();
            window.Opacity = 1;
            if (!window.IsVisible)
                window.Show();
            window.Activate();
            Dispatcher.UIThread.Post(
                () => PositionQuickDrawNotificationWindow(window, windowSettings),
                DispatcherPriority.Render);
        }).GetTask();
    }

    public static void HideQuickDrawNotificationWindow()
    {
        Dispatcher.UIThread.Post(() =>
        {
            if (_quickDrawWindow is { IsVisible: true })
                _quickDrawWindow.Hide();
        });
    }

    private static async Task ShowQuickDrawNotificationWindowAsync(
        IReadOnlyCollection<string> items,
        int autoCloseTime,
        bool animate,
        bool preserveQuickDrawResult,
        NotificationChannelSettings windowSettings,
        bool showPreview)
    {
        _quickDrawNotificationSettings = windowSettings;
        var quickDraw = IAppHost.GetService<QuickDrawPageViewModel>();
        quickDraw.NotificationOpacity = Math.Clamp(windowSettings.Transparency, 20, 100);
        var window = GetOrCreateQuickDrawWindow();
        window.Opacity = 1;
        if (!window.IsVisible)
            window.Show();
        window.Activate();
        if (showPreview)
        {
            quickDraw.ShowNotificationPreview(items, preserveQuickDrawResult);
            await Task.Delay(quickDraw.PreviewAnimationDuration);
        }

        quickDraw.ShowNotificationResult(items, autoCloseTime, animate, preserveQuickDrawResult);
        Dispatcher.UIThread.Post(
            () => PositionQuickDrawNotificationWindow(window, windowSettings),
            DispatcherPriority.Render);
    }

    private static async Task ShowQuickDrawWindowAsync()
    {
        TelemetryRuntimeService? telemetry = IAppHost.TryGetService<TelemetryRuntimeService>();
        using var transaction = telemetry?.StartTransaction("ui.quick_draw_window", "ui.navigation");

        try
        {
            _quickDrawNotificationSettings = null;
            var quickDraw = IAppHost.GetService<QuickDrawPageViewModel>();
            quickDraw.ClearNotificationPresentation();
            if (!quickDraw.IsDrawing && !await quickDraw.AuthorizeTriggeredDrawAsync())
            {
                transaction?.Finish(SpanStatus.PermissionDenied);
                return;
            }

            // A user-triggered quick draw always has a visible result window. Notification
            // settings only control the optional notification animation and delivery path.
            // Only pre-show it when the draw will actually proceed, so a skipped trigger
            // (cooling down or already running) does not leave a stale window open with no
            // auto-close scheduled.
            if (quickDraw.CanStartTriggeredDraw())
            {
                var window = GetOrCreateQuickDrawWindow();
                if (!window.IsVisible)
                    window.Show();
                window.Activate();
            }

            var showBuiltInNotificationAnimation = IAppHost.GetService<NotificationService>()
                .UsesBuiltInNotificationService(NotificationSettingsType.QuickDraw);
            if (!showBuiltInNotificationAnimation)
            {
                if (!quickDraw.IsDrawing)
                    await quickDraw.StartAuthorizedTriggeredDrawAsync();
                transaction?.Finish(SpanStatus.Ok);
                return;
            }

            if (!quickDraw.IsDrawing)
                await quickDraw.StartAuthorizedTriggeredDrawAsync();
            else if (_quickDrawWindow is { IsVisible: true })
                _quickDrawWindow.Activate();
            transaction?.Finish(SpanStatus.Ok);
        }
        catch (Exception ex)
        {
            transaction?.Finish(ex, SpanStatus.InternalError);
            IAppHost.TryGetService<ILogger<App>>()?.LogError(ex, "Failed to show quick draw window.");
            throw;
        }
    }

    private static Window GetOrCreateQuickDrawWindow()
    {
        if (_quickDrawWindow is { IsLoaded: true })
            return _quickDrawWindow;

        _quickDrawWindow = new Window
        {
            Content = IAppHost.GetService<QuickDrawPage>(),
            Title = @"SecRandom",
            MinWidth = 280,
            MinHeight = 160,
            SizeToContent = SizeToContent.WidthAndHeight,
            Topmost = true,
            WindowStartupLocation = WindowStartupLocation.CenterScreen,
            SystemDecorations = SystemDecorations.None,
            CanMinimize = false,
            CanMaximize = false,
            CanResize = false,
            ShowInTaskbar = false,
            Background = Brushes.Transparent,
            TransparencyLevelHint = [WindowTransparencyLevel.Transparent]
        };
        _quickDrawWindow.Opened += (_, _) =>
        {
            ApplyQuickDrawWindowBounds(_quickDrawWindow);
            _quickDrawWindow.ApplyPlatformFeatures(WindowFeatures.RoundedCorners, enabled: true);
            if (_quickDrawWindow.Content is QuickDrawPage page)
                page.RefreshFloatingWindowPresentation();
            Dispatcher.UIThread.Post(
                () => PositionOrCenterQuickDrawWindow(_quickDrawWindow),
                DispatcherPriority.Render);
        };
        _quickDrawWindow.SizeChanged += (_, _) =>
        {
            if (_quickDrawWindow.IsVisible)
                _quickDrawWindow.ApplyPlatformFeatures(WindowFeatures.RoundedCorners, enabled: true);
            Dispatcher.UIThread.Post(
                () => PositionOrCenterQuickDrawWindow(_quickDrawWindow),
                DispatcherPriority.Render);
        };
        _quickDrawWindow.PositionChanged += (_, _) => ApplyQuickDrawWindowBounds(_quickDrawWindow);
        _quickDrawWindow.ScalingChanged += (_, _) => ApplyQuickDrawWindowBounds(_quickDrawWindow);
        _quickDrawWindow.Closed += (_, _) =>
        {
            _quickDrawWindow = null;
            _quickDrawNotificationSettings = null;
        };
        return _quickDrawWindow;
    }

    private static void PositionOrCenterQuickDrawWindow(Window? window)
    {
        if (_quickDrawNotificationSettings is { } settings)
            PositionQuickDrawNotificationWindow(window, settings);
        else
            CenterQuickDrawWindow(window);
    }

    private static void PositionQuickDrawNotificationWindow(
        Window? window,
        NotificationChannelSettings settings)
    {
        if (window is null)
            return;

        var nativeNames = WindowsMonitorNameProvider.GetNames();
        var screen = window.Screens.All.FirstOrDefault(candidate =>
                     {
                         nativeNames.TryGetValue(candidate.Bounds.Position, out var nativeName);
                         var displayName = string.IsNullOrWhiteSpace(candidate.DisplayName)
                             ? nativeName
                             : candidate.DisplayName;
                         return !string.IsNullOrWhiteSpace(settings.EnabledMonitor)
                                && NotificationMonitorIdentifier.Matches(
                                    displayName,
                                    candidate.Bounds,
                                    settings.EnabledMonitor);
                     })
                     ?? window.Screens.Primary
                     ?? window.Screens.All.FirstOrDefault();
        if (screen is null)
            return;

        var scale = window.RenderScaling;
        var width = (int)Math.Round(window.Bounds.Width * scale);
        var height = (int)Math.Round(window.Bounds.Height * scale);
        if (width <= 0 || height <= 0)
            return;

        var area = screen.WorkingArea;
        var x = settings.WindowPosition switch
        {
            1 or 2 => area.Center.X - width / 2,
            3 => area.X,
            4 => area.Right - width,
            _ => area.Center.X - width / 2
        };
        var y = settings.WindowPosition switch
        {
            1 => area.Y,
            2 => area.Bottom - height,
            3 or 4 => area.Center.Y - height / 2,
            _ => area.Center.Y - height / 2
        };
        window.Position = new PixelPoint(
            Math.Clamp(x + settings.HorizontalOffset, area.X, Math.Max(area.X, area.Right - width)),
            Math.Clamp(y + settings.VerticalOffset, area.Y, Math.Max(area.Y, area.Bottom - height)));
    }

    private static void ApplyQuickDrawWindowBounds(Window? window)
    {
        if (window is null)
            return;

        var screen = window.Screens.ScreenFromWindow(window);
        if (screen is null)
            return;

        const double edgePadding = 32;
        var scale = window.RenderScaling;
        window.MaxWidth = Math.Max(window.MinWidth, screen.WorkingArea.Width / scale - edgePadding);
        window.MaxHeight = Math.Max(window.MinHeight, screen.WorkingArea.Height / scale - edgePadding);
    }

    private static void CenterQuickDrawWindow(Window? window)
    {
        if (window is null)
            return;

        var screen = window.Screens.ScreenFromWindow(window);
        if (screen is null)
            return;

        var scale = window.RenderScaling;
        var width = (int)Math.Round(window.Bounds.Width * scale);
        var height = (int)Math.Round(window.Bounds.Height * scale);
        if (width <= 0 || height <= 0)
            return;

        var area = screen.WorkingArea;
        window.Position = new PixelPoint(
            area.X + (area.Width - width) / 2,
            area.Y + (area.Height - height) / 2);
    }

    #endregion

    #region TrayIcon

    private void MainTaskBarIconOnClicked(object? sender, EventArgs e)
    {
        if (!OperatingSystem.IsWindows())
        {
            return;
        }

        var taskBarIconService = IAppHost.Host!.Services
            .GetServices<IHostedService>().OfType<TaskBarIconService>().First();

        var impl = typeof(TrayIcon)
            .GetProperty("Impl", BindingFlags.NonPublic | BindingFlags.Instance)?
            .GetValue(taskBarIconService.MainTaskBarIcon) as ITrayIconImpl;

        var type = AppDomain.CurrentDomain.GetAssemblies()
            .Where(a => a.FullName?.StartsWith(@"Avalonia.Win32") ?? false)
            .SelectMany(a => a.GetTypes())
            .FirstOrDefault(t => t.Name == "TrayIconImpl");

        if (impl == null || type == null) return;

        var methodInfo = type.GetMethod("OnRightClicked",
            BindingFlags.NonPublic | BindingFlags.Instance);
        methodInfo?.Invoke(impl, null);
    }

    private void MenuItemAbout_OnClick(object? sender, EventArgs e)
    {
        ShowSettingsWindow(@"settings.about");
    }

    private void MenuItemOpenMainWindow_OnClick(object? sender, EventArgs e)
    {
        ToggleMainWindow();
    }

    private void MenuItemToggleFloatingWindow_OnClick(object? sender, EventArgs e)
    {
        ToggleFloatingWindow();
    }

    internal static void RestoreAndActivate(Window window)
    {
        if (window.WindowState == WindowState.Minimized)
        {
            if (window is MainWindow mainWindow)
                mainWindow.RestoreFromMinimized();
            else
                window.WindowState = WindowState.Normal;
        }

        window.Show();
        window.Activate();
    }

    internal static void RestoreWithoutActivating(Window window)
    {
        if (window.WindowState == WindowState.Minimized)
            window.WindowState = WindowState.Normal;
        window.Show();
    }

    private void RefreshTrayWindowMenuItems()
    {
        if (_floatingWindowMenuItem is not null)
            _floatingWindowMenuItem.Header = _floatingWindow is { IsVisible: true }
                ? SecRandom.Langs.Common.Resources.Menu_HideFloatingWindow
                : SecRandom.Langs.Common.Resources.Menu_ShowFloatingWindow;
    }

    private void MenuItemOpenSettings_OnClick(object? sender, EventArgs e)
    {
        ShowSettingsWindow();
    }

    private void MenuItemRestartProgram_OnClick(object? sender, EventArgs e)
    {
        ObserveTask(IAppHost.GetService<ISecurityService>().AuthorizeAsync(
            SecurityOperation.RestartApplication,
            () =>
            {
                Restart();
                return Task.CompletedTask;
            }), "Restart authorization failed.");
    }

    private void MenuItemExitProgram_OnClick(object? sender, EventArgs e)
    {
        ObserveTask(IAppHost.GetService<ISecurityService>().AuthorizeAsync(
            SecurityOperation.ExitApplication,
            () =>
            {
                Stop();
                return Task.CompletedTask;
            }), "Exit authorization failed.");
    }

    #endregion
}
