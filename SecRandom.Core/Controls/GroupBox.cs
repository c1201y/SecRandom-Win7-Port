using Avalonia;
using Avalonia.Controls;

namespace SecRandom.Core.Controls;

/// <summary>
/// Grouped content box with a header label. Avalonia 11 has no GroupBox control,
/// so the MVE-era XAML keeps compiling against this template-backed replacement.
/// </summary>
public class GroupBox : ContentControl
{
    public static readonly StyledProperty<object?> HeaderProperty =
        AvaloniaProperty.Register<GroupBox, object?>(nameof(Header));

    public object? Header
    {
        get => GetValue(HeaderProperty);
        set => SetValue(HeaderProperty, value);
    }
}
