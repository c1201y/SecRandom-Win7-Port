using System;
using System.Reflection;
using System.Runtime.CompilerServices;
using Avalonia;
using Avalonia.Rendering;

namespace SecRandom.Helpers;

internal static class AvaloniaUnsafeAccessorHelpers
{
    public enum Win32CompositionMode
    {
        WinUIComposition = 1,
        DirectComposition = 2,
        LowLatencyDxgiSwapChain = 3,
        RedirectionSurface = 4
    }

    private static IAvaloniaDependencyResolver? AvaloniaLocator { get; } = GetCurrentAvaloniaLocator(null);

    private static IAvaloniaDependencyResolver? GetCurrentAvaloniaLocator(AvaloniaLocator? nullLocator)
    {
        try
        {
            var type = Type.GetType("Avalonia.Threading.Dispatcher, Avalonia");
            if (type != null)
            {
                var method = type.GetMethod("Current", System.Reflection.BindingFlags.Static | System.Reflection.BindingFlags.NonPublic);
                if (method != null)
                {
                    var dispatcher = method.Invoke(null, null);
                    if (dispatcher != null)
                    {
                        var locatorProperty = dispatcher.GetType().GetProperty("Locator", System.Reflection.BindingFlags.Instance | System.Reflection.BindingFlags.NonPublic);
                        if (locatorProperty != null)
                        {
                            return locatorProperty.GetValue(dispatcher) as IAvaloniaDependencyResolver;
                        }
                    }
                }
            }
        }
        catch
        {
        }
        return null;
    }

    private static object? GetAvaloniaDependencyService(IAvaloniaDependencyResolver? avaloniaLocator,
        Type serviceType)
    {
        try
        {
            if (avaloniaLocator != null)
            {
                var method = avaloniaLocator.GetType().GetMethod("GetService", new[] { typeof(Type) });
                if (method != null)
                {
                    return method.Invoke(avaloniaLocator, new object[] { serviceType });
                }
            }
        }
        catch
        {
        }
        return null;
    }

    internal static T? GetAvaloniaLocatorService<T>()
        where T : class
    {
        if (AvaloniaLocator is null)
            return null;
        var result = GetAvaloniaDependencyService(AvaloniaLocator, typeof(T));
        return result as T;
    }

    public static Win32CompositionMode? GetActiveWin32CompositionMode()
    {
        // On Avalonia 11 the platform timer is registered as IRenderTimer in the
        // AvaloniaLocator, so its concrete class name identifies the composition mode.
        var renderTimer = GetAvaloniaLocatorService<IRenderTimer>();
        if (renderTimer is null)
            return Win32CompositionMode.RedirectionSurface;

        var timerClassName = renderTimer.GetType().Name;

        return timerClassName switch
        {
            "WinUiCompositorConnection" => Win32CompositionMode.WinUIComposition,
            "DirectCompositionConnection" => Win32CompositionMode.DirectComposition,
            "DxgiConnection" => Win32CompositionMode.LowLatencyDxgiSwapChain,
            _ => Win32CompositionMode.RedirectionSurface
        };
    }
}