using System;
using System.Collections.Generic;
using System.IO;
using System.Reflection;
using System.Runtime.CompilerServices;
using System.Runtime.InteropServices;
using Avalonia;
using Avalonia.Controls;
using Avalonia.Media;
using Avalonia.Platform;
using SecRandom;
using SecRandom.Extensions;
using SecRandom.Services.CrashRecovery;
using SecRandom.Services.Desktop;
using SecRandom.Platforms;
using SecRandom.Shared;
#if SEC_RANDOM_PLATFORM_WINDOWS
using SecRandom.Platforms.Windows;
#elif SEC_RANDOM_PLATFORM_LINUX
using SecRandom.Platforms.Linux;
#elif SEC_RANDOM_PLATFORM_MACOS
using SecRandom.Platforms.MacOs;
#endif

namespace SecRandom.Desktop;

internal sealed class Program
{
    // Initialization code. Don't use any Avalonia, third-party APIs or any
    // SynchronizationContext-reliant code before AppMain is called: things aren't initialized
    // yet and stuff might break.
    [STAThread]
    public static void Main(string[] args)
    {
        // Win7 兼容实现：SetProcessDPIAware 必须在任何窗口创建或子进程派生之前调用，
        // 否则子进程会继承非 DPI 感知状态。UiAccessStartup 可能通过 CreateProcessAsUser
        // 派生替代进程，因此将 DPI 感知设置提前到所有操作之前。
        ConfigureWindows7DpiAwareness();

        // UiAccess startup reads the persisted topmost setting, so data-root selection must precede it.
        Utils.PrepareDesktopDataRoot();
        if (!UiAccessStartup.ShouldContinue(args))
        {
            Environment.ExitCode = UiAccessStartup.BootstrapExitCode;
            return;
        }

        args = UiAccessStartup.GetApplicationArguments(args);
        ConfigurePlatformServices();
        ProtocolActivation.SetStartupArguments(args);
        CrashRecoveryRuntime.SetStartupArguments(args);
        AppDomain.CurrentDomain.UnhandledException += CurrentDomainOnUnhandledException;

        try
        {
            BuildAvaloniaApp()
                .StartWithClassicDesktopLifetime(CrashRecoveryPromptOptions.RemoveCrashRecoveryArguments(args));
        }
        catch (Exception exception)
        {
            if (!CrashRecoveryRuntime.TryHandleFatalException(exception))
                throw;
        }
        finally
        {
            AppDomain.CurrentDomain.UnhandledException -= CurrentDomainOnUnhandledException;
        }
    }

    private static void ConfigurePlatformServices()
    {
#if SEC_RANDOM_PLATFORM_WINDOWS
        if (OperatingSystem.IsWindows())
            WindowsTouchKeyboardIntegration.Initialize();
        PlatformStartupContext.Set(new WindowsPlatformServiceRoot());
#elif SEC_RANDOM_PLATFORM_LINUX
        PlatformStartupContext.Set(new LinuxPlatformServiceRoot());
#elif SEC_RANDOM_PLATFORM_MACOS
        PlatformStartupContext.Set(new MacOsPlatformServiceRoot());
#else
        throw new PlatformNotSupportedException("No SecRandom desktop platform implementation was selected.");
#endif
    }

    private static void ConfigureWindows7DpiAwareness()
    {
        if (OperatingSystem.IsWindows() && Environment.OSVersion.Version < new Version(6, 2))
            SetProcessDPIAware();
    }

    private static void CurrentDomainOnUnhandledException(object sender, UnhandledExceptionEventArgs e)
    {
        if (e.ExceptionObject is Exception exception)
            CrashRecoveryRuntime.TryHandleFatalException(exception);
    }

    // Avalonia configuration, don't remove; also used by visual designer.
    public static AppBuilder BuildAvaloniaApp()
    {
        var builder = AppBuilder.Configure<App>()
            .UsePlatformDetect()
            .With(new FontManagerOptions
            {
                DefaultFamilyName = "avares://SecRandom/Assets/Fonts/MiSans/#MiSans"
            })
            .AfterPlatformServicesSetup(_ => BindAssetLoader())
            .LogToTrace()
            .LogToHostSink();

        // Win7's legacy DirectX/driver stack is not reliable with Avalonia's
        // hardware compositor. Software rendering keeps startup and transparent
        // floating windows out of the native GPU path on that OS.
        if (OperatingSystem.IsWindows() && Environment.OSVersion.Version < new Version(6, 2))
        {
            builder = builder.With(new Win32PlatformOptions
            {
                RenderingMode = [Win32RenderingMode.Software],
                CompositionMode = [Win32CompositionMode.RedirectionSurface],
                DpiAwareness = Win32DpiAwareness.SystemDpiAware
            });

            // Avalonia 11.3 cannot populate Win32 RenderScaling on Windows 7 because
            // GetDpiForMonitor is unavailable there. Patch the scaling into each top-level
            // when it becomes visible: Window.Show and PopupRoot.Show set IsVisible=true
            // before the initial layout pass and before the native window is shown, so
            // correcting the scaling at that point lets windows and popups be created,
            // sized and laid out at the correct scale from the start. This avoids both the
            // blurry 1.0 fallback and the visible resize a post-show correction would cause.
            Visual.IsVisibleProperty.Changed.AddClassHandler<TopLevel, bool>((topLevel, change) =>
            {
                if (change.GetNewValue<bool>() && topLevel.PlatformImpl is not null)
                {
                    ApplyWindows7Scaling(topLevel);
                    AttachWindows7BackgroundErase(topLevel);
                }
            });
        }

        return builder;
    }

    private static void ApplyWindows7Scaling(TopLevel topLevel)
    {
        var implementation = topLevel.PlatformImpl!;
        ApplyWindows7ScalingToImpl(implementation);

        // Win7 兼容实现：通过反射触发 Avalonia 内部的 ScalingChanged 委托，
        // 使 TopLevel 自身的 _scaling 字段和渲染缩放跟随 Win7 补丁后的 DPI 值。
        // 此操作是尽力而为的：字段名或委托类型在 Avalonia 版本更新时可能变化，
        // 因此失败时仅记录日志，不影响窗口显示。
        try
        {
            var scalingChanged = implementation.GetType()
                .GetProperty("ScalingChanged", BindingFlags.Instance | BindingFlags.Public | BindingFlags.NonPublic)
                ?.GetValue(implementation) as Action<double>;
            if (scalingChanged is not null)
            {
                var dpi = GetSystemDpi();
                if (dpi > 0)
                    scalingChanged(dpi / 96d);
            }
        }
        catch (Exception ex)
        {
            System.Diagnostics.Debug.WriteLine($"[Win7 DPI] Failed to invoke ScalingChanged: {ex.Message}");
        }
    }

    private static void ApplyWindows7ScalingToImpl(object implementation)
    {
        var dpi = GetSystemDpi();
        if (dpi <= 0)
            return;

        var scaling = dpi / 96d;
        var type = implementation.GetType();
        var scalingField = FindInstanceField(type, "_scaling");
        var dpiField = FindInstanceField(type, "_dpi");
        if (scalingField is null || dpiField is null)
            return;

        // Win7 兼容实现：通过反射将 GetDeviceCaps(LOGPIXELSX) 获取的真实 DPI 写入
        // Avalonia 平台实现的 _scaling 和 _dpi 字段，补偿 GetDpiForMonitor 不可用的缺陷。
        // 失败时静默跳过，不阻塞窗口创建——窗口会以 1.0 缩比渲染，外观模糊但功能可用。
        try
        {
            scalingField.SetValue(implementation, scaling);
            dpiField.SetValue(implementation, (uint)dpi);
        }
        catch (Exception ex)
        {
            System.Diagnostics.Debug.WriteLine($"[Win7 DPI] Failed to patch scaling fields: {ex.Message}");
        }
    }

    private static int GetSystemDpi()
    {
        var hdc = GetDC(IntPtr.Zero);
        if (hdc == IntPtr.Zero)
            return 0;

        try
        {
            return GetDeviceCaps(hdc, 88); // LOGPIXELSX
        }
        finally
        {
            ReleaseDC(IntPtr.Zero, hdc);
        }
    }

    private static FieldInfo? FindInstanceField(Type type, string name)
    {
        for (var current = type; current is not null; current = current.BaseType)
        {
            var field = current.GetField(name, BindingFlags.Instance | BindingFlags.NonPublic | BindingFlags.DeclaredOnly);
            if (field is not null)
                return field;
        }

        return null;
    }

    private static readonly ConditionalWeakTable<TopLevel, Win32Properties.CustomWndProcHookCallback> s_windows7BackgroundHooks = new();

    // GCL_STYLE index for GetClassLongPtr/SetClassLongPtr (window class styles).
    private const int GCL_STYLE = -26;
    // Avalonia registers every window class with CS_OWNDC | CS_HREDRAW | CS_VREDRAW. The
    // two redraw styles make Windows invalidate and erase the entire client area on every
    // interactive resize — the root cause of the flicker. We strip them per-window below.
    private const uint CS_VREDRAW = 0x0001;
    private const uint CS_HREDRAW = 0x0002;

    private static void AttachWindows7BackgroundErase(TopLevel topLevel)
    {
        // Avalonia's Win32 window class registers hbrBackground = NULL and leaves
        // WM_ERASEBKGND unhandled, so the client area stays black until the first frame is
        // presented. In light mode that reads as a black -> white flash when a window opens.
        // Paint the theme background during WM_ERASEBKGND so the pre-frame window already
        // matches the rendered content. Transparent windows (FloatingWindow) are skipped:
        // an opaque erase would break their transparency.
        //
        // Note: interactive resize is handled by the native system sizing loop now that the
        // resizable app windows keep WS_THICKFRAME via SystemDecorations.BorderOnly (see
        // MainWindow / FirstRunOobeWindow). DWM stretches the previous frame over regions
        // exposed during the resize, so no manual capture-based resize is needed here.
        // GetValue makes the guard + add atomic: the window-creation path can run the
        // IsVisible class handler for the same top-level more than once (or from re-entrant
        // message pump calls), which previously allowed a duplicate ConditionalWeakTable key
        // and crashed Win7 startup with "An item with the same key has already been added".
        s_windows7BackgroundHooks.GetValue(topLevel, _ =>
        {
            Win32Properties.CustomWndProcHookCallback callback = (IntPtr hWnd, uint msg, IntPtr wParam, IntPtr lParam, ref bool handled) =>
            {
                // Strip CS_HREDRAW | CS_VREDRAW from the window class of the opaque, resizable
                // app windows (OOBE / Main / Settings = SystemDecorations.BorderOnly). Avalonia
                // registers each window under a unique class name with CS_OWNDC | CS_HREDRAW |
                // CS_VREDRAW. The two redraw styles make Windows invalidate and erase the whole
                // client area on every interactive resize, which — combined with the async
                // render loop — produces the flicker seen on Windows 7 (Basic theme, no DWM
                // stretch). Removing them keeps the previous frame on screen during a resize;
                // only the newly exposed strip is invalidated and painted (see WM_ERASEBKGND
                // below), so resizing stays smooth and the exposed area never flashes black.
                // Each window has a unique class name, so this affects only the target window.
                // Idempotent by reading the live style first (also re-entrancy safe).
                if (topLevel is Window { SystemDecorations: SystemDecorations.BorderOnly })
                {
                    var style = GetClassLongPtrSafe(hWnd, GCL_STYLE);
                    var newStyle = style & ~(CS_HREDRAW | CS_VREDRAW);
                    if (newStyle != style)
                        SetClassLongPtrSafe(hWnd, GCL_STYLE, newStyle);

                }

                if (msg != 0x0014) // WM_ERASEBKGND
                    return IntPtr.Zero;

                if (ResolveWindows7BackgroundColor(topLevel) is { } color)
                {
                    // Paint only the invalidated (newly exposed) region, not the whole client
                    // area, so the previous frame stays intact during resize and only the strip
                    // actually being exposed receives the theme background (no black edge).
                    if (GetUpdateRect(hWnd, out var rect, false) && rect.Right > rect.Left && rect.Bottom > rect.Top)
                    {
                        var brush = CreateSolidBrush(color);
                        try
                        {
                            FillRect(wParam, ref rect, brush);
                            handled = true;
                            return new IntPtr(1);
                        }
                        finally
                        {
                            DeleteObject(brush);
                        }
                    }
                }

                return IntPtr.Zero;
            };

            Win32Properties.AddWndProcHookCallback(topLevel, callback);
            return callback;
        });
    }

    private static uint? ResolveWindows7BackgroundColor(TopLevel topLevel)
    {
        // A window that opts into transparency (FloatingWindow) must not get an
        // opaque erase background.
        if (topLevel.Background is ISolidColorBrush explicitBrush)
        {
            if (explicitBrush.Color.A == 255)
                return ToColorRef(explicitBrush.Color);
            return null;
        }

        if (topLevel.TryFindResource("SolidBackgroundFillColorBaseBrush", out var resource) &&
            resource is ISolidColorBrush baseBrush &&
            baseBrush.Color.A == 255)
            return ToColorRef(baseBrush.Color);

        return null;
    }

    private static uint ToColorRef(Color color)
    {
        return (uint)(color.R | (color.G << 8) | (color.B << 16));
    }

    [StructLayout(LayoutKind.Sequential)]
    private struct RECT
    {
        public int Left;
        public int Top;
        public int Right;
        public int Bottom;
    }

    [DllImport("user32.dll")]
    private static extern int FillRect(IntPtr hDC, ref RECT lprc, IntPtr hbr);

    [DllImport("gdi32.dll")]
    private static extern IntPtr CreateSolidBrush(uint crColor);

    [DllImport("gdi32.dll")]
    private static extern bool DeleteObject(IntPtr hObject);

    [DllImport("user32.dll")]
    private static extern IntPtr GetDC(IntPtr hWnd);

    [DllImport("user32.dll")]
    private static extern bool SetProcessDPIAware();

    [DllImport("gdi32.dll")]
    private static extern int GetDeviceCaps(IntPtr hdc, int index);

    [DllImport("user32.dll")]
    private static extern int ReleaseDC(IntPtr hWnd, IntPtr hdc);

    [DllImport("user32.dll", EntryPoint = "GetClassLongPtrW")]
    private static extern IntPtr GetClassLongPtr(IntPtr hWnd, int nIndex);

    [DllImport("user32.dll", EntryPoint = "SetClassLongPtrW")]
    private static extern IntPtr SetClassLongPtr(IntPtr hWnd, int nIndex, IntPtr dwNewLong);

    [DllImport("user32.dll", EntryPoint = "GetClassLongW")]
    private static extern uint GetClassLong(IntPtr hWnd, int nIndex);

    [DllImport("user32.dll", EntryPoint = "SetClassLongW")]
    private static extern uint SetClassLong(IntPtr hWnd, int nIndex, int dwNewLong);

    [DllImport("user32.dll")]
    private static extern bool GetUpdateRect(IntPtr hWnd, out RECT lpRect, bool bErase);

    // GetClassLongPtr/SetClassLongPtr only exist as real exports on 64-bit; on 32-bit they
    // are macros resolving to GetClassLong/SetClassLong. Route by pointer size so neither
    // platform hits a missing-entry-point exception. Class styles are 32-bit values, so the
    // helpers normalize to uint across both pointer widths.
    private static uint GetClassLongPtrSafe(IntPtr hWnd, int nIndex)
        => IntPtr.Size == 8 ? (uint)(long)GetClassLongPtr(hWnd, nIndex) : GetClassLong(hWnd, nIndex);

    private static void SetClassLongPtrSafe(IntPtr hWnd, int nIndex, uint value)
    {
        if (IntPtr.Size == 8)
            SetClassLongPtr(hWnd, nIndex, new IntPtr((long)value));
        else
            SetClassLong(hWnd, nIndex, unchecked((int)value));
    }

    private static void BindAssetLoader()
    {
        var appAssembly = typeof(App).Assembly;
        var assemblyDirectory = Path.GetDirectoryName(appAssembly.Location);
        var assetRoot = Path.Combine(
            string.IsNullOrEmpty(assemblyDirectory) ? AppContext.BaseDirectory : assemblyDirectory,
            "Assets");

        var assetLoader = new OverlayAssetLoader(
            new StandardAssetLoader(appAssembly),
            appAssembly,
            appAssembly.GetName().Name!,
            "/Assets/",
            assetRoot,
            new HashSet<string>(StringComparer.Ordinal)
            {
                "Updates/release-public-key.txt"
            });

        const BindingFlags flags = BindingFlags.Public | BindingFlags.NonPublic | BindingFlags.Static | BindingFlags.Instance;
        var locatorType = typeof(AvaloniaLocator);
        var locator = locatorType.GetProperty("CurrentMutable", flags)?.GetValue(null)
                      ?? throw new InvalidOperationException("Unable to get AvaloniaLocator.CurrentMutable.");
        var bindMethod = locatorType.GetMethod("Bind", flags)?.MakeGenericMethod(typeof(IAssetLoader))
                         ?? throw new InvalidOperationException("Unable to get AvaloniaLocator.Bind<T>().");
        var registration = bindMethod.Invoke(locator, null)
                           ?? throw new InvalidOperationException("Unable to bind Avalonia IAssetLoader.");
        var toConstantMethod = registration.GetType().GetMethod("ToConstant", flags)?.MakeGenericMethod(typeof(IAssetLoader))
                               ?? throw new InvalidOperationException("Unable to get AvaloniaLocator.ToConstant<T>().");

        toConstantMethod.Invoke(registration, [assetLoader]);
    }
}
