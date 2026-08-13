using System;
using System.Collections.Generic;
using System.Linq;
using System.Threading.Tasks;
using Avalonia;
using Avalonia.Controls;

namespace SecRandom.Core.Views;

public sealed class NavigationEventArgs : EventArgs
{
    public NavigationEventArgs(Page page)
    {
        Page = page;
    }

    public Page Page { get; }
}

public sealed class ModalPoppedEventArgs : EventArgs
{
    public ModalPoppedEventArgs(Page modal)
    {
        Modal = modal;
    }

    public Page Modal { get; }
}

/// <summary>
/// In-process page navigator for MVE hosts. It keeps the Avalonia 12 NavigationPage
/// call surface (Push/Pop/Modal/Replace, CurrentPage, Popped/ModalPopped, attached
/// chrome properties) on top of a plain content presenter so hosts do not change.
/// </summary>
public class NavigationPage : ContentControl
{
    public static readonly AttachedProperty<bool> HasNavigationBarProperty =
        AvaloniaProperty.RegisterAttached<NavigationPage, Control, bool>("HasNavigationBar", false);

    public static readonly AttachedProperty<bool> HasBackButtonProperty =
        AvaloniaProperty.RegisterAttached<NavigationPage, Control, bool>("HasBackButton", true);

    private readonly List<Page> _stack = [];
    private readonly List<Page> _modalStack = [];

    public static void SetHasNavigationBar(AvaloniaObject obj, bool value) => obj.SetValue(HasNavigationBarProperty, value);

    public static bool GetHasNavigationBar(AvaloniaObject obj) => obj.GetValue<bool>(HasNavigationBarProperty);

    public static void SetHasBackButton(AvaloniaObject obj, bool value) => obj.SetValue(HasBackButtonProperty, value);

    public static bool GetHasBackButton(AvaloniaObject obj) => obj.GetValue<bool>(HasBackButtonProperty);

    public Page? CurrentPage { get; private set; }

    public event EventHandler<NavigationEventArgs>? Popped;

    public event EventHandler<ModalPoppedEventArgs>? ModalPopped;

    public Task PushAsync(Page page)
    {
        ArgumentNullException.ThrowIfNull(page);
        _stack.Add(page);
        ShowTop();
        return Task.CompletedTask;
    }

    public Task PopAsync()
    {
        if (_stack.Count == 0)
            return Task.CompletedTask;

        var removed = _stack[^1];
        _stack.RemoveAt(_stack.Count - 1);
        if (_modalStack.Count == 0)
        {
            ShowTop();
            Popped?.Invoke(this, new NavigationEventArgs(removed));
        }

        return Task.CompletedTask;
    }

    public Task PushModalAsync(Page page)
    {
        ArgumentNullException.ThrowIfNull(page);
        _modalStack.Add(page);
        ShowTop();
        return Task.CompletedTask;
    }

    public Task PopModalAsync()
    {
        if (_modalStack.Count == 0)
            return Task.CompletedTask;

        var removed = _modalStack[^1];
        _modalStack.RemoveAt(_modalStack.Count - 1);
        ShowTop();
        ModalPopped?.Invoke(this, new ModalPoppedEventArgs(removed));
        return Task.CompletedTask;
    }

    public Task PopAllModalsAsync()
    {
        while (_modalStack.Count > 0)
        {
            var removed = _modalStack[^1];
            _modalStack.RemoveAt(_modalStack.Count - 1);
            ModalPopped?.Invoke(this, new ModalPoppedEventArgs(removed));
        }

        ShowTop();
        return Task.CompletedTask;
    }

    public Task PopToRootAsync()
    {
        while (_stack.Count > 1)
        {
            var removed = _stack[^1];
            _stack.RemoveAt(_stack.Count - 1);
            Popped?.Invoke(this, new NavigationEventArgs(removed));
        }

        ShowTop();
        return Task.CompletedTask;
    }

    public Task ReplaceAsync(Page page)
    {
        ArgumentNullException.ThrowIfNull(page);
        if (_stack.Count == 0)
            _stack.Add(page);
        else
            _stack[^1] = page;
        ShowTop();
        return Task.CompletedTask;
    }

    private void ShowTop()
    {
        var current = _modalStack.LastOrDefault() ?? _stack.LastOrDefault();
        CurrentPage = current;
        Content = current;
    }
}
