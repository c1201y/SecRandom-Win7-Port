using System;
using System.Collections.Generic;
using System.ComponentModel;
using System.Globalization;
using System.Runtime.CompilerServices;
using Avalonia.Controls;
using Avalonia.Interactivity;
using Avalonia.Media;
using Avalonia.Media.Imaging;
using Avalonia.Platform;
using FluentAvalonia.UI.Controls;
using Microsoft.Extensions.DependencyInjection;
using Microsoft.Extensions.Hosting;
using SecRandom.Core.Abstraction;
using SecRandom.Core.Attributes;
using SecRandom.Core.Enums;
using SecRandom.Core.Helpers.UI;
using SecRandom.Core.Icons;
using SecRandom.Core;
using SecRandom.Services;
using SecRandom.Services.Desktop;
using LR = SecRandom.Langs.SettingsPages.About.Resources;

namespace SecRandom.Views.SettingsPages.About;

[PageInfo("settings.about", FluentIcons.InfoFilled, location: PageLocation.Bottom, hidePageTitle: true)]
public partial class AboutSettingsPage : UserControl, INotifyPropertyChanged
{
    private OnlineStatusService OnlineStatusService { get; } = IAppHost.Host!.Services
        .GetServices<IHostedService>().OfType<OnlineStatusService>().First();
    private IExternalLauncher ExternalLauncher { get; } = IAppHost.GetService<IExternalLauncher>();
    public int OnlineUsersCount => OnlineStatusService.CachedOnlineCount;

    private static readonly Dictionary<string, Bitmap> BannerCache = new();
    public IImage BannerSource => LoadBanner(CultureInfo.CurrentUICulture.TwoLetterISOLanguageName switch
    {
        "zh" => "avares://SecRandom/Assets/Banners/secrandom-banner-cn.png",
        "ja" => "avares://SecRandom/Assets/Banners/secrandom-banner-ja.png",
        _ => "avares://SecRandom/Assets/Banners/secrandom-banner-en.png"
    });

    private static Bitmap LoadBanner(string uri)
    {
        if (BannerCache.TryGetValue(uri, out var cached)) return cached;
        using var stream = AssetLoader.Open(new Uri(uri));
        var bitmap = new Bitmap(stream);
        BannerCache[uri] = bitmap;
        return bitmap;
    }

    private event PropertyChangedEventHandler? NotifyPropertyChanged;

    event PropertyChangedEventHandler? INotifyPropertyChanged.PropertyChanged
    {
        add => NotifyPropertyChanged += value;
        remove => NotifyPropertyChanged -= value;
    }
    
    public AboutSettingsPage()
    {
        DataContext = this;
        InitializeComponent();
    }

    private void OpenLink(string url)
    {
        ExternalLauncher.TryOpenUri(url);
    }

    private void UriNavigationCommands_OnClick(object sender, RoutedEventArgs e)
    {
        var url = e.Source switch
        {
            SettingsExpanderItem s => s.CommandParameter?.ToString(),
            Button s => s.CommandParameter?.ToString(),
            _ => null
        };

        if (url != null) OpenLink(url);
    }

    private void OnPropertyChanged([CallerMemberName] string? propertyName = null)
    {
        NotifyPropertyChanged?.Invoke(this, new PropertyChangedEventArgs(propertyName));
    }
}
