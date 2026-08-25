using System;
using System.ComponentModel;
using System.Runtime.InteropServices;
using Avalonia;
using Avalonia.Controls;
using Avalonia.Input;
using Avalonia.Interactivity;
using Avalonia.Markup.Xaml;
using Avalonia.Media;
using Avalonia.Threading;
using FluentAvalonia.UI.Windowing;
using SecRandom.Core.Abstraction;
using SecRandom.Core.Enums.Configs;
using SecRandom.Core.Models.SubConfigs.General;
using SecRandom.Core.Services.Config;
using SecRandom.Platforms.Abstractions;
using SecRandom.Services.Platform;

namespace SecRandom.Views;

public partial class MainWindow : AppWindow
{
    private readonly MainWindowSettingsScope _settingsScope;
    private readonly BasicSettingsConfig? _settings;
    private readonly MainConfigHandler? _configHandler;
    private bool _hasBeenShown;
    private bool _windowSizeSavePending;
    private double _lastNormalWindowWidth;
    private double _lastNormalWindowHeight;
    private WindowState _lastNonMinimizedWindowState = WindowState.Normal;

    public MainWindow() : this(MainWindowSettingsScope.None)
    {
    }

    internal MainWindow(MainWindowSettingsScope settingsScope)
    {
        _settingsScope = settingsScope;
        InitializeComponent();

        TitleBar.Height = 48;
        TitleBar.ExtendsContentIntoTitleBar = true;

        // 透明标题栏按钮颜色
        TitleBar.ButtonHoverBackgroundColor = Color.FromArgb(23, 0, 0, 0);
        TitleBar.ButtonPressedBackgroundColor = Color.FromArgb(52, 0, 0, 0);
        TitleBar.ButtonInactiveForegroundColor = Colors.Gray;

        // SystemDecorations=None 没有原生缩放边框,自行处理边缘拖拽缩放。
        PointerMoved += MainWindowOnPointerMoved;
        PointerPressed += MainWindowOnPointerPressed;

        if (!UsesStoredWindowSettings)
            return;

        _configHandler = IAppHost.GetService<MainConfigHandler>();
        _settings = _configHandler.Data.General.Basic;
        _settings.PropertyChanged += SettingsOnPropertyChanged;
        PropertyChanged += MainWindowOnPropertyChanged;
        Closing += MainWindowOnClosing;
        Closed += MainWindowOnClosed;
        RestoreWindowSettings();

        if (OperatingSystem.IsMacOS())
        {
            ExtendClientAreaToDecorationsHint = true;
            ExtendClientAreaTitleBarHeightHint = 48;
        }
    }

    private void InitializeComponent()
    {
        AvaloniaXamlLoader.Load(this);
    }

    // 无边框窗口的边缘拖拽缩放:窗口边缘 ResizeBorderThickness 像素内按下即进入系统缩放拖拽。
    private const double ResizeBorderThickness = 6;

    private WindowEdge? GetResizeEdge(Point position)
    {
        if (WindowState != WindowState.Normal)
            return null;

        var left = position.X <= ResizeBorderThickness;
        var right = position.X >= Bounds.Width - ResizeBorderThickness;
        var top = position.Y <= ResizeBorderThickness;
        var bottom = position.Y >= Bounds.Height - ResizeBorderThickness;
        if (top && left) return WindowEdge.NorthWest;
        if (top && right) return WindowEdge.NorthEast;
        if (bottom && left) return WindowEdge.SouthWest;
        if (bottom && right) return WindowEdge.SouthEast;
        if (top) return WindowEdge.North;
        if (bottom) return WindowEdge.South;
        if (left) return WindowEdge.West;
        if (right) return WindowEdge.East;
        return null;
    }

    private void MainWindowOnPointerMoved(object? sender, PointerEventArgs e)
    {
        var edge = GetResizeEdge(e.GetPosition(this));
        Cursor = edge switch
        {
            WindowEdge.North or WindowEdge.South => new Cursor(StandardCursorType.SizeNorthSouth),
            WindowEdge.West or WindowEdge.East => new Cursor(StandardCursorType.SizeWestEast),
            WindowEdge.NorthWest or WindowEdge.SouthEast => new Cursor(StandardCursorType.TopLeftCorner),
            WindowEdge.NorthEast or WindowEdge.SouthWest => new Cursor(StandardCursorType.TopRightCorner),
            _ => Cursor.Default
        };
    }

    private void MainWindowOnPointerPressed(object? sender, PointerPressedEventArgs e)
    {
        if (e.GetCurrentPoint(this).Properties.IsLeftButtonPressed
            && GetResizeEdge(e.GetPosition(this)) is { } edge)
        {
            BeginResizeDrag(edge, e);
            e.Handled = true;
        }
    }

    private void OnLoaded(object? sender, RoutedEventArgs e)
    {
        if (App.IsMicaSupported)
        {
            TransparencyLevelHint = [WindowTransparencyLevel.Mica];
            Background = Brushes.Transparent;
        }

        EnableBorderlessResize();

        if (WindowState != WindowState.Maximized)
        {
            _lastNormalWindowWidth = Math.Max(MinWidth, Bounds.Width);
            _lastNormalWindowHeight = Math.Max(MinHeight, Bounds.Height);
        }
        else
        {
            _lastNonMinimizedWindowState = WindowState.Maximized;
        }

        _hasBeenShown = true;
        ApplyPlatformWindowFeatures();
    }

    // SystemDecorations=None 移除了 WS_THICKFRAME,WM_SYSCOMMAND 的 SC_SIZE 缩放
    // 拖拽因此失效;补回该样式,FA AppWindow 的 WM_NCCALCSIZE 处理会保持视觉无边框。
    private void EnableBorderlessResize()
    {
        if (!OperatingSystem.IsWindows())
            return;

        var handle = TryGetPlatformHandle()?.Handle ?? IntPtr.Zero;
        if (handle == IntPtr.Zero)
            return;

        const int GWL_STYLE = -16;
        const int WS_THICKFRAME = 0x00040000;
        var style = GetWindowLong(handle, GWL_STYLE);
        if ((style & WS_THICKFRAME) == 0)
            SetWindowLong(handle, GWL_STYLE, style | WS_THICKFRAME);
    }

    [DllImport("user32.dll", EntryPoint = "GetWindowLong")]
    private static extern int GetWindowLong(IntPtr hWnd, int nIndex);

    [DllImport("user32.dll", EntryPoint = "SetWindowLong")]
    private static extern int SetWindowLong(IntPtr hWnd, int nIndex, int dwNewLong);

    private bool UsesStoredWindowSettings => _settingsScope != MainWindowSettingsScope.None;
    private bool UsesPrimaryWindowSettings => _settingsScope == MainWindowSettingsScope.Primary;

    private void RestoreWindowSettings()
    {
        if (_settings is null)
            return;

        if (UsesPrimaryWindowSettings)
            ApplyPlatformWindowFeatures();
        if (!_settings.AutoSaveWindowSize)
            return;

        _lastNormalWindowWidth = GetUsableDimension(
            GetStoredWindowWidth(),
            MinWidth,
            UsesPrimaryWindowSettings ? 1200 : 1000);
        _lastNormalWindowHeight = GetUsableDimension(
            GetStoredWindowHeight(),
            MinHeight,
            UsesPrimaryWindowSettings ? 800 : 720);
        Width = _lastNormalWindowWidth;
        Height = _lastNormalWindowHeight;
        if (GetStoredWindowMaximized())
        {
            _lastNonMinimizedWindowState = WindowState.Maximized;
            WindowState = WindowState.Maximized;
        }
    }

    private void SettingsOnPropertyChanged(object? sender, PropertyChangedEventArgs e)
    {
        if (UsesPrimaryWindowSettings
            && e.PropertyName == nameof(BasicSettingsConfig.MainWindowTopmostMode))
            ApplyPlatformWindowFeatures();
        else if (e.PropertyName == nameof(BasicSettingsConfig.AutoSaveWindowSize)
                 && _settings!.AutoSaveWindowSize)
            SaveWindowSize();
    }

    private void ApplyPlatformWindowFeatures()
    {
        var enabled = UsesPrimaryWindowSettings &&
                      _settings?.MainWindowTopmostMode is TopmostMode.Topmost or TopmostMode.UiAccess;
        Topmost = enabled;
        if (IsLoaded)
            this.ApplyPlatformFeatures(WindowFeatures.Topmost, enabled);
    }

    private void MainWindowOnPropertyChanged(object? sender, AvaloniaPropertyChangedEventArgs e)
    {
        if (e.Property == IsVisibleProperty && IsVisible && _hasBeenShown)
        {
            Dispatcher.UIThread.Post(RefreshRestoredLayout, DispatcherPriority.Render);
            return;
        }

        if (!UsesStoredWindowSettings || !_hasBeenShown)
            return;

        if (e.Property == BoundsProperty && WindowState == WindowState.Normal)
        {
            _lastNormalWindowWidth = Math.Max(MinWidth, Bounds.Width);
            _lastNormalWindowHeight = Math.Max(MinHeight, Bounds.Height);
            if (_settings?.AutoSaveWindowSize == true)
                QueueWindowSizeSave();
        }
        else if (e.Property == WindowStateProperty)
        {
            if (WindowState != WindowState.Minimized)
                _lastNonMinimizedWindowState = WindowState;

            if (WindowState != WindowState.Minimized && _settings?.AutoSaveWindowSize == true)
                QueueWindowSizeSave();
        }
    }

    private void RefreshRestoredLayout()
    {
        if (!IsVisible || WindowState == WindowState.Minimized || Content is not Control content)
            return;

        content.InvalidateMeasure();
        content.InvalidateArrange();
        content.InvalidateVisual();
    }

    private void QueueWindowSizeSave()
    {
        if (_windowSizeSavePending)
            return;

        _windowSizeSavePending = true;
        DispatcherTimer.RunOnce(() =>
        {
            _windowSizeSavePending = false;
            SaveWindowSize();
        }, TimeSpan.FromMilliseconds(300));
    }

    private void SaveWindowSize()
    {
        if (_settings?.AutoSaveWindowSize != true || !IsVisible)
            return;

        if (_lastNormalWindowWidth <= 0 || _lastNormalWindowHeight <= 0)
        {
            _lastNormalWindowWidth = GetUsableDimension(
                GetStoredWindowWidth(),
                MinWidth,
                UsesPrimaryWindowSettings ? 1200 : 1000);
            _lastNormalWindowHeight = GetUsableDimension(
                GetStoredWindowHeight(),
                MinHeight,
                UsesPrimaryWindowSettings ? 800 : 720);
        }

        var stateToSave = WindowState == WindowState.Minimized
            ? _lastNonMinimizedWindowState
            : WindowState;
        SetStoredWindowMaximized(stateToSave == WindowState.Maximized);
        if (stateToSave == WindowState.Maximized)
        {
            SetStoredWindowWidth(_lastNormalWindowWidth);
            SetStoredWindowHeight(_lastNormalWindowHeight);
        }
        else if (WindowState == WindowState.Normal)
        {
            _lastNormalWindowWidth = Math.Max(MinWidth, Bounds.Width);
            _lastNormalWindowHeight = Math.Max(MinHeight, Bounds.Height);
            SetStoredWindowWidth(_lastNormalWindowWidth);
            SetStoredWindowHeight(_lastNormalWindowHeight);
        }

        _configHandler!.Save();
    }

    internal void RestoreFromMinimized()
    {
        if (WindowState == WindowState.Minimized)
            WindowState = _lastNonMinimizedWindowState;
    }

    private void MainWindowOnClosing(object? sender, WindowClosingEventArgs e)
    {
        if (!UsesStoredWindowSettings)
            return;

        SaveWindowSize();
        if (!UsesPrimaryWindowSettings)
            return;

        if (_settings?.BackgroundResident == true && !App.Current.IsStopping)
        {
            e.Cancel = true;
            Hide();
        }
        else if (!App.Current.IsStopping)
        {
            e.Cancel = true;
            App.RequestExitFromMainWindow();
        }
    }

    private void MainWindowOnClosed(object? sender, EventArgs e)
    {
        if (_settings is not null)
            _settings.PropertyChanged -= SettingsOnPropertyChanged;

        if (UsesStoredWindowSettings)
        {
            PropertyChanged -= MainWindowOnPropertyChanged;
            Closing -= MainWindowOnClosing;
            Closed -= MainWindowOnClosed;
        }
    }

    private double GetStoredWindowWidth()
    {
        return UsesPrimaryWindowSettings ? _settings!.MainWindowWidth : _settings!.SettingsWindowWidth;
    }

    private double GetStoredWindowHeight()
    {
        return UsesPrimaryWindowSettings ? _settings!.MainWindowHeight : _settings!.SettingsWindowHeight;
    }

    private bool GetStoredWindowMaximized()
    {
        return UsesPrimaryWindowSettings ? _settings!.MainWindowMaximized : _settings!.SettingsWindowMaximized;
    }

    private void SetStoredWindowWidth(double value)
    {
        if (UsesPrimaryWindowSettings)
            _settings!.MainWindowWidth = value;
        else
            _settings!.SettingsWindowWidth = value;
    }

    private void SetStoredWindowHeight(double value)
    {
        if (UsesPrimaryWindowSettings)
            _settings!.MainWindowHeight = value;
        else
            _settings!.SettingsWindowHeight = value;
    }

    private void SetStoredWindowMaximized(bool value)
    {
        if (UsesPrimaryWindowSettings)
            _settings!.MainWindowMaximized = value;
        else
            _settings!.SettingsWindowMaximized = value;
    }

    private static double GetUsableDimension(double value, double minimum, double fallback)
    {
        return double.IsFinite(value) && value >= minimum ? value : Math.Max(minimum, fallback);
    }
}

internal enum MainWindowSettingsScope
{
    None,
    Primary,
    Settings
}
