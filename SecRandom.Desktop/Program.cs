using System;
using System.Collections.Generic;
using System.IO;
using System.Reflection;
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
                    ApplyWindows7Scaling(topLevel);
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
