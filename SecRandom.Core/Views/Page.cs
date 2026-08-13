using Avalonia;
using Avalonia.Controls;

namespace SecRandom.Core.Views;

/// <summary>
/// Logical page base for the cross-platform view engine. Mirrors the Avalonia 12
/// Page contract used by MVE hosts so the engine keeps one API surface on Avalonia 11.
/// </summary>
public class Page : ContentControl
{
    public static readonly StyledProperty<object?> HeaderProperty =
        AvaloniaProperty.Register<Page, object?>(nameof(Header));

    public object? Header
    {
        get => GetValue(HeaderProperty);
        set => SetValue(HeaderProperty, value);
    }
}
