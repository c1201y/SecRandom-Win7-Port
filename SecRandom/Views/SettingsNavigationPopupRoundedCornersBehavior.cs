using System;
using Avalonia;
using Avalonia.Controls;
using Avalonia.Controls.Primitives;
using Avalonia.VisualTree;
using FluentAvalonia.UI.Controls;
using SecRandom.Platforms.Abstractions;
using SecRandom.Services.Platform;

namespace SecRandom.Views;

public class SettingsNavigationPopupRoundedCornersBehavior
{
    public static readonly AttachedProperty<bool> IsEnabledProperty =
        AvaloniaProperty.RegisterAttached<SettingsNavigationPopupRoundedCornersBehavior, Control, bool>("IsEnabled");

    static SettingsNavigationPopupRoundedCornersBehavior()
    {
        IsEnabledProperty.Changed.AddClassHandler<Control>(OnIsEnabledChanged);
    }

    public static void SetIsEnabled(Control control, bool value) => control.SetValue(IsEnabledProperty, value);

    public static bool GetIsEnabled(Control control) => control.GetValue(IsEnabledProperty);

    private static void OnIsEnabledChanged(Control control, AvaloniaPropertyChangedEventArgs args)
    {
        if (GetIsEnabled(control) && control is PopupRoot popupRoot)
            popupRoot.Opened += PopupRoot_OnOpened;
    }

    private static void PopupRoot_OnOpened(object? sender, EventArgs e)
    {
        if (sender is not PopupRoot popupRoot
            || popupRoot.Parent is not Popup { PlacementTarget: Visual target }
            || !target.GetVisualAncestors().Append(target).OfType<NavigationView>().Any(navigationView =>
                navigationView.GetVisualAncestors().Append(navigationView).OfType<SettingsView>().Any()))
            return;

        popupRoot.ApplyPlatformFeatures(WindowFeatures.RoundedCorners, enabled: true);
    }
}
