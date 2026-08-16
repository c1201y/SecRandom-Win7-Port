using FluentAvalonia.UI.Controls;

namespace SecRandom.Core.Controls;

/// <summary>
///     Fluent Icon 图标源
/// </summary>
public class FluentIconSource : FontIconSource
{
    public FluentIconSource()
    {
        FontFamily = GlobalConstants.FluentIconsFontFamily;
    }

    public FluentIconSource(string glyph) : this()
    {
        Glyph = glyph;
        FontFamily = GlobalConstants.FluentIconsFontFamily;
        FontSize = 16;
    }

    public FluentIconSource ProvideValue()
    {
        return this;
    }
}
