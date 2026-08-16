using System;
using SecRandom.Core.Icons;

namespace SecRandom.Core.MarkupExtensions;

/// <summary>
///     XAML 标记扩展，用法：<c>{ci:FI AccessTimeFilled}</c>
/// </summary>
public class FiExtension
{
    /// <inheritdoc cref="FiExtension" />
    public FiExtension()
    {
    }

    /// <inheritdoc cref="FiExtension" />
    public FiExtension(int icon)
    {
        Icon = icon;
    }

    public FiExtension(string iconName)
    {
        var field = typeof(FluentIcons).GetField(iconName);
        if (field?.GetValue(null) is not string glyph || glyph.Length == 0)
            throw new ArgumentException($"Unknown Fluent icon: {iconName}", nameof(iconName));

        Icon = char.ConvertToUtf32(glyph, 0);
    }

    /// <summary>
    ///     Fluent Icon 种类
    /// </summary>
    public int Icon { get; set; }

    /// <summary>
    ///     提供值
    /// </summary>
    /// <param name="serviceProvider">Avalonia 服务提供器</param>
    /// <returns>Fluent Icon 字符串值</returns>
    public string ProvideValue(IServiceProvider serviceProvider)
    {
        return char.ConvertFromUtf32(Icon);
    }
}
