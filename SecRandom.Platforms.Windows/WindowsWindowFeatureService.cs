using System.Collections.Concurrent;
using System.Runtime.InteropServices;
using SecRandom.Platforms.Abstractions;

namespace SecRandom.Platforms.Windows;

public sealed class WindowsWindowFeatureService : IWindowFeatureService
{
    private const int GwlExStyle = -20;
    private const long WsExTransparent = 0x00000020L;
    private const long WsExToolWindow = 0x00000080L;
    private const long WsExAppWindow = 0x00040000L;
    private const long WsExLayered = 0x00080000L;
    private const long WsExNoActivate = 0x08000000L;
    private const uint WdaNone = 0x00000000;
    private const uint WdaExcludeFromCapture = 0x00000011;
    private const uint SwpNoMove = 0x0002;
    private const uint SwpNoSize = 0x0001;
    private const uint SwpNoActivate = 0x0010;
    private const uint SwpFrameChanged = 0x0020;
    private const WindowFeatures StyleFeatures = WindowFeatures.ToolWindow |
                                                WindowFeatures.SkipTaskSwitcher |
                                                WindowFeatures.NoActivate |
                                                WindowFeatures.ClickThrough;
    private static readonly nint HwndTopmost = -1;
    private static readonly nint HwndNotopmost = -2;
    private const uint LwaAlpha = 0x00000002;
    private readonly ConcurrentDictionary<nint, WindowFeatures> _enabledFeatures = [];

    public WindowFeatureApplyResult ApplyOpacity(PlatformWindowHandle window, double opacity)
    {
        if (!window.IsValid)
            return WindowFeatureApplyResult.Failed(WindowFeatures.None, "The native window handle is not available.");

        if (!string.IsNullOrWhiteSpace(window.Descriptor)
            && !string.Equals(window.Descriptor, "HWND", StringComparison.OrdinalIgnoreCase))
        {
            return WindowFeatureApplyResult.Unsupported(WindowFeatures.None,
                $"The '{window.Descriptor}' native handle is not a Windows HWND.");
        }

        if (TrySetLayeredAlpha(window.Value, opacity, out var failure))
            return WindowFeatureApplyResult.Applied(WindowFeatures.None);

        return WindowFeatureApplyResult.Failed(WindowFeatures.None, failure);
    }

    private static bool TrySetLayeredAlpha(nint window, double opacity, out string? failure)
    {
        try
        {
            Marshal.SetLastPInvokeError(0);
            var style = (long)GetWindowLongPtr(window, GwlExStyle);
            if (style == 0 && Marshal.GetLastWin32Error() != 0)
            {
                failure = $"GetWindowLongPtr failed with Win32 error {Marshal.GetLastWin32Error()}.";
                return false;
            }

            if ((style & WsExLayered) == 0)
            {
                Marshal.SetLastPInvokeError(0);
                var previous = SetWindowLongPtr(window, GwlExStyle, new IntPtr(style | WsExLayered));
                if (previous == 0 && Marshal.GetLastWin32Error() != 0)
                {
                    failure = $"SetWindowLongPtr failed with Win32 error {Marshal.GetLastWin32Error()}.";
                    return false;
                }

                SetWindowPos(window, 0, 0, 0, 0, 0,
                    SwpNoMove | SwpNoSize | SwpNoActivate | SwpFrameChanged);
            }

            var alpha = (byte)Math.Clamp((int)Math.Round(opacity * 255), 0, 255);
            if (SetLayeredWindowAttributes(window, 0, alpha, LwaAlpha))
            {
                failure = null;
                return true;
            }

            failure = $"SetLayeredWindowAttributes failed with Win32 error {Marshal.GetLastWin32Error()}.";
            return false;
        }
        catch (Exception exception)
        {
            failure = exception.Message;
            return false;
        }
    }

    public WindowFeatures SupportedFeatures => WindowFeatures.Topmost |
                                                WindowFeatures.ToolWindow |
                                                 WindowFeatures.SkipTaskSwitcher |
                                                 WindowFeatures.NoActivate |
                                                 WindowFeatures.ClickThrough |
                                                 WindowFeatures.RoundedCorners |
                                                 (OperatingSystem.IsWindowsVersionAtLeast(10, 0, 19041)
                                                    ? WindowFeatures.ExcludeFromCapture
                                                    : WindowFeatures.None);

    public WindowFeatureApplyResult Apply(PlatformWindowHandle window, WindowFeatureRequest request)
    {
        if (!window.IsValid)
            return WindowFeatureApplyResult.Failed(request.Features, "The native window handle is not available.");

        if (!string.IsNullOrWhiteSpace(window.Descriptor)
            && !string.Equals(window.Descriptor, "HWND", StringComparison.OrdinalIgnoreCase))
        {
            return WindowFeatureApplyResult.Unsupported(request.Features,
                $"The '{window.Descriptor}' native handle is not a Windows HWND.");
        }

        var requested = request.Features & SupportedFeatures;
        var unsupported = request.Features & ~SupportedFeatures;
        if (requested == WindowFeatures.None)
            return WindowFeatureApplyResult.Partial(WindowFeatures.None, unsupported, WindowFeatures.None);

        _enabledFeatures.TryGetValue(window.Value, out var current);
        var desired = request.Enabled ? current | requested : current & ~requested;
        var applied = WindowFeatures.None;
        var failed = WindowFeatures.None;
        string? detail = null;

        if ((requested & WindowFeatures.Topmost) != 0)
        {
            if (TrySetTopmost(window.Value, (desired & WindowFeatures.Topmost) != 0, out var failure))
                applied |= WindowFeatures.Topmost;
            else
            {
                failed |= WindowFeatures.Topmost;
                detail ??= failure;
            }
        }

        if ((requested & WindowFeatures.ExcludeFromCapture) != 0)
        {
            if (TrySetCaptureExclusion(window.Value, (desired & WindowFeatures.ExcludeFromCapture) != 0, out var failure))
                applied |= WindowFeatures.ExcludeFromCapture;
            else
            {
                failed |= WindowFeatures.ExcludeFromCapture;
                detail ??= failure;
            }
        }

        if ((requested & WindowFeatures.RoundedCorners) != 0)
        {
            if (TrySetRoundedCorners(window.Value, request.Enabled, out var failure))
                applied |= WindowFeatures.RoundedCorners;
            else
            {
                failed |= WindowFeatures.RoundedCorners;
                detail ??= failure;
            }
        }

        var requestedStyles = requested & StyleFeatures;
        if (requestedStyles != WindowFeatures.None)
        {
            if (TrySetExtendedStyles(window.Value, desired, out var failure))
                applied |= requestedStyles;
            else
            {
                failed |= requestedStyles;
                detail ??= failure;
            }
        }

        UpdateTrackedFeatures(window.Value, current, applied, request.Enabled);
        return WindowFeatureApplyResult.Partial(applied, unsupported, failed, detail);
    }

    private void UpdateTrackedFeatures(nint window, WindowFeatures current, WindowFeatures applied, bool enabled)
    {
        var updated = enabled ? current | applied : current & ~applied;
        if (updated == WindowFeatures.None)
            _enabledFeatures.TryRemove(window, out _);
        else
            _enabledFeatures[window] = updated;
    }

    private static bool TrySetTopmost(nint window, bool enabled, out string? failure)
    {
        try
        {
            var insertAfter = enabled ? HwndTopmost : HwndNotopmost;
            if (SetWindowPos(window, insertAfter, 0, 0, 0, 0,
                    SwpNoMove | SwpNoSize | SwpNoActivate | SwpFrameChanged))
            {
                failure = null;
                return true;
            }

            failure = $"SetWindowPos failed with Win32 error {Marshal.GetLastWin32Error()}.";
            return false;
        }
        catch (Exception exception)
        {
            failure = exception.Message;
            return false;
        }
    }

    private static bool TrySetCaptureExclusion(nint window, bool enabled, out string? failure)
    {
        try
        {
            if (SetWindowDisplayAffinity(window, enabled ? WdaExcludeFromCapture : WdaNone))
            {
                failure = null;
                return true;
            }

            failure = $"SetWindowDisplayAffinity failed with Win32 error {Marshal.GetLastWin32Error()}.";
            return false;
        }
        catch (Exception exception)
        {
            failure = exception.Message;
            return false;
        }
    }

    private static bool TrySetExtendedStyles(nint window, WindowFeatures desired, out string? failure)
    {
        try
        {
            Marshal.SetLastPInvokeError(0);
            var style = (long)GetWindowLongPtr(window, GwlExStyle);
            if (style == 0 && Marshal.GetLastWin32Error() != 0)
            {
                failure = $"GetWindowLongPtr failed with Win32 error {Marshal.GetLastWin32Error()}.";
                return false;
            }

            var updated = style;
            var isToolWindow = (desired & (WindowFeatures.ToolWindow | WindowFeatures.SkipTaskSwitcher)) != 0;
            updated = SetFlag(updated, WsExToolWindow, isToolWindow);
            if (isToolWindow)
                updated &= ~WsExAppWindow;
            updated = SetFlag(updated, WsExNoActivate, (desired & WindowFeatures.NoActivate) != 0);

            if ((desired & WindowFeatures.ClickThrough) != 0)
                updated |= WsExLayered | WsExTransparent;
            else
                updated &= ~WsExTransparent;

            if (updated != style)
            {
                Marshal.SetLastPInvokeError(0);
                var previous = SetWindowLongPtr(window, GwlExStyle, new IntPtr(updated));
                if (previous == 0 && Marshal.GetLastWin32Error() != 0)
                {
                    failure = $"SetWindowLongPtr failed with Win32 error {Marshal.GetLastWin32Error()}.";
                    return false;
                }
            }

            if (SetWindowPos(window, 0, 0, 0, 0, 0,
                    SwpNoMove | SwpNoSize | SwpNoActivate | SwpFrameChanged))
            {
                failure = null;
                return true;
            }

            failure = $"SetWindowPos failed with Win32 error {Marshal.GetLastWin32Error()}.";
            return false;
        }
        catch (Exception exception)
        {
            failure = exception.Message;
            return false;
        }
    }

    private static bool TrySetRoundedCorners(nint window, bool enabled, out string? failure)
    {
        try
        {
            if (!GetClientRect(window, out var rect))
            {
                failure = $"GetClientRect failed with Win32 error {Marshal.GetLastWin32Error()}.";
                return false;
            }

            if (!enabled)
            {
                if (SetWindowRgn(window, (nint)0, true) != 0)
                {
                    failure = null;
                    return true;
                }

                failure = $"SetWindowRgn failed with Win32 error {Marshal.GetLastWin32Error()}.";
                return false;
            }

            var width = Math.Max(1, rect.Right - rect.Left);
            var height = Math.Max(1, rect.Bottom - rect.Top);
            var region = CreateRoundRectRgn(0, 0, width + 1, height + 1, 16, 16);
            if (region == (nint)0)
            {
                failure = $"CreateRoundRectRgn failed with Win32 error {Marshal.GetLastWin32Error()}.";
                return false;
            }

            if (SetWindowRgn(window, region, true) != 0)
            {
                failure = null;
                return true;
            }

            DeleteObject(region);
            failure = $"SetWindowRgn failed with Win32 error {Marshal.GetLastWin32Error()}.";
            return false;
        }
        catch (Exception exception)
        {
            failure = exception.Message;
            return false;
        }
    }

    private static long SetFlag(long value, long flag, bool enabled) => enabled ? value | flag : value & ~flag;

    [DllImport("user32.dll", EntryPoint = "GetWindowLongPtrW", SetLastError = true)]
    private static extern nint GetWindowLongPtr(nint hWnd, int nIndex);

    [DllImport("user32.dll", EntryPoint = "SetWindowLongPtrW", SetLastError = true)]
    private static extern nint SetWindowLongPtr(nint hWnd, int nIndex, nint value);

    [DllImport("user32.dll", SetLastError = true)]
    [return: MarshalAs(UnmanagedType.Bool)]
    private static extern bool SetWindowPos(nint hWnd, nint hWndInsertAfter, int x, int y, int cx, int cy,
        uint flags);

    [DllImport("user32.dll", SetLastError = true)]
    [return: MarshalAs(UnmanagedType.Bool)]
    private static extern bool SetWindowDisplayAffinity(nint hWnd, uint affinity);

    [DllImport("user32.dll", SetLastError = true)]
    [return: MarshalAs(UnmanagedType.Bool)]
    private static extern bool GetClientRect(nint hWnd, out NativeRect rect);

    [DllImport("user32.dll", SetLastError = true)]
    private static extern int SetWindowRgn(nint hWnd, nint hRgn, [MarshalAs(UnmanagedType.Bool)] bool redraw);

    [DllImport("gdi32.dll", SetLastError = true)]
    private static extern nint CreateRoundRectRgn(int left, int top, int right, int bottom, int width, int height);

    [DllImport("gdi32.dll", SetLastError = true)]
    [return: MarshalAs(UnmanagedType.Bool)]
    private static extern bool DeleteObject(nint handle);

    [StructLayout(LayoutKind.Sequential)]
    private readonly struct NativeRect
    {
        public readonly int Left;
        public readonly int Top;
        public readonly int Right;
        public readonly int Bottom;
    }

    [DllImport("user32.dll", SetLastError = true)]
    [return: MarshalAs(UnmanagedType.Bool)]
    private static extern bool SetLayeredWindowAttributes(nint hWnd, uint crKey, byte bAlpha, uint dwFlags);
}
