using System;
using System.Threading;
using System.Threading.Tasks;
using Avalonia.Controls;
using Avalonia.Platform;
using Avalonia.Threading;
using Microsoft.Extensions.Hosting;

namespace SecRandom.Services.Desktop;

public class TaskBarIconService : IHostedService
{
    public TrayIcon MainTaskBarIcon { get; } =
        new()
        {
            Icon = new WindowIcon(AssetLoader.Open(new Uri("avares://SecRandom/Assets/AppLogo.png"))),
            ToolTipText = @"SecRandom"
        };

    public TaskBarIconService()
    {
        App.Current.AppStopping += CurrentOnAppStopping;
    }

    private void CurrentOnAppStopping(object? sender, EventArgs e)
    {
        Dispatcher.UIThread.Invoke(() =>
        {
            MainTaskBarIcon.IsVisible = false;
        });
    }

    public Task StartAsync(CancellationToken cancellationToken)
    {
        return Task.CompletedTask;
    }

    public Task StopAsync(CancellationToken cancellationToken)
    {
        return Task.CompletedTask;
    }
}
