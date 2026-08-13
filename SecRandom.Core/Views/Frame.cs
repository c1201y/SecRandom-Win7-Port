using System;
using Avalonia;
using Avalonia.Controls;

namespace SecRandom.Core.Views;

/// <summary>
/// Resolves logical navigation targets for a host frame.
/// </summary>
public interface IFANavigationPageFactory
{
    Control? GetPage(Type srcType);

    Control? GetPageFromObject(object target);
}

/// <summary>
/// Single-content navigation frame for shell hosts. Keeps the Frame call surface
/// (NavigateFromObject/NavigationPageFactory) the shells already use.
/// </summary>
public class Frame : ContentControl
{
    public static readonly StyledProperty<IFANavigationPageFactory?> NavigationPageFactoryProperty =
        AvaloniaProperty.Register<Frame, IFANavigationPageFactory?>(nameof(NavigationPageFactory));

    public IFANavigationPageFactory? NavigationPageFactory
    {
        get => GetValue(NavigationPageFactoryProperty);
        set => SetValue(NavigationPageFactoryProperty, value);
    }

    public void NavigateFromObject(object? page)
    {
        if (page is null)
        {
            Content = null;
            return;
        }

        Content = NavigationPageFactory?.GetPageFromObject(page) ?? page as Control;
    }

    public void Navigate(Type pageType)
    {
        ArgumentNullException.ThrowIfNull(pageType);
        Content = NavigationPageFactory?.GetPage(pageType);
    }
}
