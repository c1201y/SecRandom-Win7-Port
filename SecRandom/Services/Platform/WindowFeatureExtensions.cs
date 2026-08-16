using Avalonia.Controls;
using Avalonia.Platform;
using FluentAvalonia.UI.Windowing;
using SecRandom.Core.Abstraction;
using SecRandom.Platforms.Abstractions;

namespace SecRandom.Services.Platform;

internal static class WindowFeatureExtensions
{
    public static WindowFeatureApplyResult ApplyPlatformFeatures(
        this TopLevel topLevel,
        WindowFeatures features,
        bool enabled)
    {
        return Apply(topLevel.TryGetPlatformHandle(), features, enabled);
    }

    public static WindowFeatureApplyResult ApplyPlatformFeatures(
        this AppWindow window,
        WindowFeatures features,
        bool enabled)
    {
        return Apply(window.TryGetPlatformHandle(), features, enabled);
    }

    public static WindowFeatureApplyResult ApplyPlatformOpacity(
        this TopLevel topLevel,
        double opacity)
    {
        return ApplyOpacity(topLevel.TryGetPlatformHandle(), opacity);
    }

    public static WindowFeatureApplyResult ApplyPlatformOpacity(
        this AppWindow window,
        double opacity)
    {
        return ApplyOpacity(window.TryGetPlatformHandle(), opacity);
    }

    private static WindowFeatureApplyResult ApplyOpacity(IPlatformHandle? handle, double opacity)
    {
        var service = IAppHost.TryGetService<IWindowFeatureService>();
        if (service is null)
        {
            return WindowFeatureApplyResult.Unsupported(WindowFeatures.None,
                "The application host has not registered platform window services.");
        }

        if (handle is null)
        {
            return WindowFeatureApplyResult.Failed(WindowFeatures.None,
                "The native window handle is not available.");
        }

        return service.ApplyOpacity(
            new PlatformWindowHandle(handle.Handle, handle.HandleDescriptor), opacity);
    }

    private static WindowFeatureApplyResult Apply(
        IPlatformHandle? handle,
        WindowFeatures features,
        bool enabled)
    {
        var service = IAppHost.TryGetService<IWindowFeatureService>();
        if (service is null)
        {
            return WindowFeatureApplyResult.Unsupported(features,
                "The application host has not registered platform window services.");
        }

        return service.Apply(
            new PlatformWindowHandle(handle?.Handle ?? (nint)0, handle?.HandleDescriptor),
            new WindowFeatureRequest(features, enabled));
    }
}
