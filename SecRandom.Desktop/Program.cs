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
        // UiAccess startup reads the persisted topmost setting, so data-root selection must precede it.
        Utils.PrepareDesktopDataRoot();
        if (!UiAccessStartup.ShouldContinue(args))
        {
            Environment.ExitCode = UiAccessStartup.BootstrapExitCode;
            return;
        }

        args = UiAccessStartup.GetApplicationArguments(args);
        ConfigureWindows7DpiAwareness();
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

        // Notify the TopLevel so its own _scaling field and layout scaling follow the impl.
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

        scalingField.SetValue(implementation, scaling);
        dpiField.SetValue(implementation, (uint)dpi);
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

    private static void AttachWindows7BackgroundErase(TopLevel topLevel)
    {
        // Avalonia's Win32 window class registers hbrBackground = NULL and leaves
        // WM_ERASEBKGND unhandled, so the client area stays black until the first frame is
        // presented. In light mode that reads as a black -> white flash when a window opens.
        // Paint the theme background during WM_ERASEBKGND so the pre-frame window already
        // matches the rendered content. Transparent windows (FloatingWindow) are skipped:
        // an opaque erase would break their transparency.
        if (s_windows7BackgroundHooks.TryGetValue(topLevel, out _))
            return;

        Win32Properties.CustomWndProcHookCallback callback = (IntPtr hWnd, uint msg, IntPtr wParam, IntPtr lParam, ref bool handled) =>
        {
            if (topLevel is Window { CanResize: true, SystemDecorations: SystemDecorations.None } resizableWindow
                && resizableWindow.WindowState != WindowState.Maximized)
            {
                // Win7 never enters the system sizing loop for undecorated windows, so the
                // left/bottom/right edges run a manual capture-based resize instead of
                // relying on WM_NCHITTEST/WS_THICKFRAME non-client behavior.
                var resizeState = s_windows7ResizeStates.GetValue(topLevel, static _ => new Windows7ManualResizeState());

                if (msg == 0x0014 && resizeState.IsActive) // WM_ERASEBKGND
                {
                    // SetWindowPos sends an erase request for each resize step. Letting the
                    // Win7 background brush run here produces a visible erase -> render flash.
                    handled = true;
                    return new IntPtr(1);
                }

                switch (msg)
                {
                    case 0x0020: // WM_SETCURSOR
                        if ((unchecked((int)(long)lParam) & 0xFFFF) == 1 /* HTCLIENT */
                            && TryGetWindows7ResizeZone(hWnd, out var cursorZone))
                        {
                            SetCursor(LoadWindows7ResizeCursor(cursorZone));
                            handled = true;
                            return new IntPtr(1);
                        }

                        break;

                    case 0x0201: // WM_LBUTTONDOWN
                        if (TryGetWindows7ResizeZone(hWnd, out var dragZone))
                        {
                            StartWindows7ManualResize(resizeState, hWnd, resizableWindow, dragZone);
                            handled = true;
                            return IntPtr.Zero;
                        }

                        break;

                    case 0x0200: // WM_MOUSEMOVE
                        if (resizeState.IsActive)
                        {
                            UpdateWindows7ManualResize(resizeState, hWnd);
                            handled = true;
                            return IntPtr.Zero;
                        }

                        break;

                    case 0x0202: // WM_LBUTTONUP
                        if (resizeState.IsActive)
                        {
                            EndWindows7ManualResize(resizeState);
                            handled = true;
                            return IntPtr.Zero;
                        }

                        break;

                    case 0x0021: // WM_CAPTURECHANGED
                        resizeState.IsActive = false;
                        break;
                }
            }

            if (msg != 0x0014) // WM_ERASEBKGND
                return IntPtr.Zero;

            if (ResolveWindows7BackgroundColor(topLevel) is { } color)
            {
                var rect = new RECT();
                if (GetClientRect(hWnd, out rect))
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
        s_windows7BackgroundHooks.Add(topLevel, callback);
    }

    private sealed class Windows7ManualResizeState
    {
        public bool IsActive;
        public bool EdgeLeft;
        public bool EdgeRight;
        public bool EdgeBottom;
        public POINT AnchorPoint;
        public RECT AnchorRect;
        public double MinWidth;
        public double MinHeight;
    }

    private const int W7ResizeZoneLeft = 0x1;
    private const int W7ResizeZoneRight = 0x2;
    private const int W7ResizeZoneBottom = 0x4;

    private static readonly ConditionalWeakTable<TopLevel, Windows7ManualResizeState> s_windows7ResizeStates = new();

    private static bool TryGetWindows7ResizeZone(IntPtr hWnd, out int zone)
    {
        zone = 0;
        if (!GetCursorPos(out var cursor) || !GetWindowRect(hWnd, out var rect))
            return false;

        var border = Math.Max(8, GetSystemMetrics(32) + GetSystemMetrics(92));
        if (cursor.X < rect.Left + border)
            zone |= W7ResizeZoneLeft;
        if (cursor.X >= rect.Right - border)
            zone |= W7ResizeZoneRight;
        if (cursor.Y >= rect.Bottom - border)
            zone |= W7ResizeZoneBottom;

        return zone != 0;
    }

    private static void StartWindows7ManualResize(
        Windows7ManualResizeState state,
        IntPtr hWnd,
        Window window,
        int zone)
    {
        if (!GetCursorPos(out var anchor) || !GetWindowRect(hWnd, out state.AnchorRect))
            return;

        state.AnchorPoint = anchor;
        state.EdgeLeft = (zone & W7ResizeZoneLeft) != 0;
        state.EdgeRight = (zone & W7ResizeZoneRight) != 0;
        state.EdgeBottom = (zone & W7ResizeZoneBottom) != 0;
        state.MinWidth = window.MinWidth * window.RenderScaling;
        state.MinHeight = window.MinHeight * window.RenderScaling;
        state.IsActive = true;
        SetCapture(hWnd);
    }

    private static void UpdateWindows7ManualResize(Windows7ManualResizeState state, IntPtr hWnd)
    {
        if (!GetCursorPos(out var cursor))
            return;

        var deltaX = cursor.X - state.AnchorPoint.X;
        var deltaY = cursor.Y - state.AnchorPoint.Y;
        var left = state.AnchorRect.Left;
        var top = state.AnchorRect.Top;
        var width = state.AnchorRect.Right - state.AnchorRect.Left;
        var height = state.AnchorRect.Bottom - state.AnchorRect.Top;

        if (state.EdgeRight)
        {
            width = Math.Max((int)state.MinWidth, width + deltaX);
        }
        else if (state.EdgeLeft)
        {
            width = Math.Max((int)state.MinWidth, width - deltaX);
            left = state.AnchorRect.Right - width;
        }

        if (state.EdgeBottom)
            height = Math.Max((int)state.MinHeight, height + deltaY);

        // SWP_NOZORDER | SWP_NOACTIVATE keeps focus and z-order stable while dragging.
        SetWindowPos(hWnd, IntPtr.Zero, left, top, width, height, 0x0004 | 0x0010);
    }

    private static void EndWindows7ManualResize(Windows7ManualResizeState state)
    {
        state.IsActive = false;
        ReleaseCapture();
    }

    private static IntPtr LoadWindows7ResizeCursor(int zone)
    {
        // OCR constants: IDC_SIZENWSE=32642, IDC_SIZENESW=32643, IDC_SIZEWE=32644, IDC_SIZENS=32645.
        var id = (zone & W7ResizeZoneBottom) != 0
            ? (zone & W7ResizeZoneLeft) != 0 ? 32643
                : (zone & W7ResizeZoneRight) != 0 ? 32642
                : 32645
            : 32644;
        return LoadCursor(IntPtr.Zero, new IntPtr(id));
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
    private static extern bool GetClientRect(IntPtr hWnd, out RECT lpRect);

    [DllImport("user32.dll")]
    private static extern bool GetWindowRect(IntPtr hWnd, out RECT lpRect);

    [DllImport("user32.dll", SetLastError = true)]
    private static extern bool SetWindowPos(
        IntPtr hWnd,
        IntPtr hWndInsertAfter,
        int x,
        int y,
        int cx,
        int cy,
        uint flags);

    [DllImport("user32.dll")]
    private static extern IntPtr SetCapture(IntPtr hWnd);

    [DllImport("user32.dll")]
    private static extern bool ReleaseCapture();

    [DllImport("user32.dll")]
    private static extern bool GetCursorPos(out POINT point);

    [DllImport("user32.dll")]
    private static extern IntPtr LoadCursor(IntPtr hInstance, IntPtr lpCursorName);

    [DllImport("user32.dll")]
    private static extern IntPtr SetCursor(IntPtr hCursor);

    [StructLayout(LayoutKind.Sequential)]
    private struct POINT
    {
        public int X;
        public int Y;
    }

    [DllImport("user32.dll")]
    private static extern int GetSystemMetrics(int index);

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
