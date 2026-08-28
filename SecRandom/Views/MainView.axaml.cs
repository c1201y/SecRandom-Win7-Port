using System;
using System.Linq;
using Avalonia.Controls;
using Avalonia.Controls.Primitives;
using Avalonia.Interactivity;
using Avalonia.Markup.Xaml;
using Avalonia.Media;
using Avalonia.Threading;
using Avalonia.Media.Imaging;
using DynamicData;
using FluentAvalonia.UI.Controls;
using Microsoft.Extensions.DependencyInjection;
using SecRandom.Core;
using SecRandom.Core.Abstraction;
using SecRandom.Core.Abstraction.Services;
using SecRandom.Core.Attributes;
using SecRandom.Core.Controls;
using SecRandom.Core.Enums;
using SecRandom.Core.Extensions;
using SecRandom.Core.Helpers.UI;
using SecRandom.Core.Icons;
using SecRandom.Core.Models.UI;
using SecRandom.Core.Services;
using SecRandom.Core.Views;
using SecRandom.Mobile;
using SecRandom.Platforms.Abstractions;
using SecRandom.Services;
using SecRandom.Services.Mobile;
using SecRandom.ViewModels;
using ViewFrame = SecRandom.Core.Views.Frame;

namespace SecRandom.Views;

public partial class MainView : ViewBase, IFANavigationPageFactory
{
    private const string DefaultMainPageId = "main.rollCall";

    private readonly ViewFrame? _navigationFrame;
    private readonly NavigationView? _navigationView;

    private AppToastAdorner? _appToastAdorner;
    private bool _isAdornerAdded;
    private bool _isFeatureAvailabilitySubscribed;
    private readonly IFeatureAvailabilityService _featureAvailability = IAppHost.GetService<IFeatureAvailabilityService>();

    public MainView()
    {
        Current = this;
        DataContext = this;
        InitializeComponent();

        _navigationFrame = this.FindControl<ViewFrame>("NavigationFrame");
        _navigationView = this.FindControl<NavigationView>("NavigationView");

        if (_navigationFrame != null) _navigationFrame.NavigationPageFactory = this;
        BuildNavigationMenuItems();
        SelectNavigationItemById(DefaultMainPageId);
        Closed += (_, _) =>
        {
            if (ReferenceEquals(Current, this))
                Current = null;
        };

        RenderOptions.SetBitmapInterpolationMode(this, BitmapInterpolationMode.HighQuality);
        RenderOptions.SetEdgeMode(this, EdgeMode.Antialias);
    }

    public static MainView? Current { get; private set; }
    public MainViewModel ViewModel { get; } = IAppHost.GetService<MainViewModel>();
    public bool IsMacOs => OperatingSystem.IsMacOS();
    public bool IsDesktop => App.IsDesktop;
    public bool UseDesktopUI =>
        (IAppHost.TryGetService<IPlatformServiceRoot>() as MobilePlatformServiceRoot)?.UsesDesktopMainView ?? IsDesktop;

    public static void ShowSuccessToast(string message) => ShowToast(message, InfoBarSeverity.Success);

    public static void ShowToast(string message, InfoBarSeverity severity)
    {
        var view = Current;
        if (view is null)
            return;

        void Show()
        {
            view.ShowToast(new ToastMessage(message)
            {
                Severity = severity
            });
        }

        if (Dispatcher.UIThread.CheckAccess())
            Show();
        else
            Dispatcher.UIThread.Post(Show);
    }

    public Control? GetPage(Type srcType)
    {
        return Activator.CreateInstance(srcType) as Control;
    }

    public Control? GetPageFromObject(object target)
    {
        if (target is not PageInfo info) return null;

        var page = IAppHost.Host!.Services.GetKeyedService<UserControl>(info.Id);
        if (page == null)
            // ���ҳ��δע�ᣬ����һ��ռλ���ؼ�
            return new TextBlock { Text = $"ҳ�� {info.Id} δ�ҵ�" };

        return page;
    }

    private void OnLoaded(object? sender, RoutedEventArgs e)
    {
        if (!_isFeatureAvailabilitySubscribed)
        {
            _featureAvailability.Changed += FeatureAvailabilityOnChanged;
            _isFeatureAvailabilitySubscribed = true;
        }

        if (ViewModel.SelectedPageInfo is null) SelectNavigationItemById(DefaultMainPageId);

        if (Content is not Control element || _isAdornerAdded) return;

        var layer = AdornerLayer.GetAdornerLayer(element);
        _appToastAdorner = new AppToastAdorner(this);
        layer?.Children.Add(_appToastAdorner);
        AdornerLayer.SetAdornedElement(_appToastAdorner, this);

        if (GlobalConstants.IsDevelopment)
        {
            var adorner = new DevelopmentBuildAdorner();
            layer?.Children.Add(adorner);
            AdornerLayer.SetAdornedElement(adorner, this);
        }

        _isAdornerAdded = true;
    }

    private void OnUnloaded(object? sender, RoutedEventArgs e)
    {
        if (_isFeatureAvailabilitySubscribed)
        {
            _featureAvailability.Changed -= FeatureAvailabilityOnChanged;
            _isFeatureAvailabilitySubscribed = false;
        }

        if (_appToastAdorner is not null && Content is Control element)
        {
            var layer = AdornerLayer.GetAdornerLayer(element);
            layer?.Children.Remove(_appToastAdorner);
            _appToastAdorner = null;
        }
        _isAdornerAdded = false;
    }

    private void BuildNavigationMenuItems()
    {
        var applySampleNav = App.IsDesktop || OperatingSystem.IsBrowser() || UseDesktopUI;
        
        ViewModel.NavigationViewItems.Clear();
        ViewModel.NavigationViewFooterItems.Clear();

        ViewModel.NavigationViewItems
            .AddRange(PagesRegistryService.MainItems
                .Where(IsPageAvailable)
                .Where(info => info.Location == PageLocation.Top)
                .ToNavigationViewItems(ViewModel.FlattenNavigationItems)
                .Select(x =>
                {
                    if (applySampleNav)
                    {
                        x.Classes.Add(@"SampleAppNav");
                    }

                    return x;
                }));

        ViewModel.NavigationViewFooterItems
            .AddRange(PagesRegistryService.MainItems
                .Where(IsPageAvailable)
                .Where(info => info.Location == PageLocation.Bottom)
                .ToNavigationViewItems(ViewModel.FlattenNavigationItems)
                .Select(x =>
                {
                    if (applySampleNav)
                    {
                        x.Classes.Add(@"SampleAppNav");
                    }

                    return x;
                }));

        var settingsPageInfo = new PageInfo(@"settings", FluentIcons.SettingsFilled, null, PageLocation.Bottom)
        {
            Name = Langs.Common.Resources.Feat_Settings
        };
        var settingsItem = settingsPageInfo.ToNavigationViewItemBase();
        if (applySampleNav)
        {
            settingsItem.Classes.Add(@"SampleAppNav");
        }
        
        ViewModel.NavigationViewFooterItems.Add(settingsItem);
        
        if (applySampleNav)
        {
            _navigationView?.Classes.Add(@"SampleAppNav");
        }
        else
        {
            if (_navigationView != null) _navigationView.PaneDisplayMode = NavigationViewPaneDisplayMode.LeftMinimal;
            ViewModel.IsNavPaneToggleButtonVisible = true;
        }
    }

    public void SelectNavigationItemById(string id)
    {
        var info = PagesRegistryService.MainItems.FirstOrDefault(info => info.Id == id);

        if (info != null && IsPageAvailable(info)) CoreNavigate(info);
    }

    private bool IsPageAvailable(PageInfo info)
    {
        return info.Id != "main.lottery" || _featureAvailability.IsLotteryEnabled;
    }

    private void FeatureAvailabilityOnChanged(object? sender, EventArgs e)
    {
        Dispatcher.UIThread.Post(() =>
        {
            BuildNavigationMenuItems();
            if (ViewModel.SelectedPageInfo?.Id == "main.lottery" && !_featureAvailability.IsLotteryEnabled)
                SelectNavigationItemById(DefaultMainPageId);
        });
    }

    private void SelectNavigationItem(PageInfo info)
    {
        var item = ViewModel.FlattenNavigationItems.FirstOrDefault(item => Equals(item.Tag, info));
        ViewModel.SelectedNavigationViewItem = item;
    }

    public void OpenDrawer(object content)
    {
        ViewModel.DrawerContent = content;
        ViewModel.IsDrawerOpen = true;
    }

    public void CloseDrawer()
    {
        ViewModel.IsDrawerOpen = false;
    }

    private void CoreNavigate(PageInfo info)
    {
        if (info.Id == "settings")
        {
            if (!App.IsDesktop && IAppHost.TryGetService<IMobileSettingsNavigator>() is { } mobileSettings)
                _ = mobileSettings.OpenAsync();
            else
                App.ShowSettingsWindow();
            return;
        }

        ViewModel.FrameContent = null;
        SelectNavigationItem(info);
        ViewModel.SelectedPageInfo = info;
        _navigationFrame?.NavigateFromObject(info);
        CloseDrawer();
    }

    private void NavigationView_OnItemInvoked(object? sender, NavigationViewItemInvokedEventArgs e)
    {
        PageInfo? info = null;

        if (e.InvokedItemContainer is NavigationViewItem { Tag: PageInfo containerInfo })
            info = containerInfo;
        else if (e.InvokedItem is PageInfo invokedInfo) info = invokedInfo;

        if (info != null) CoreNavigate(info);
    }

    private void TogglePaneButton_OnClick(object? sender, RoutedEventArgs e)
    {
        if (_navigationView != null) _navigationView.IsPaneOpen = !_navigationView.IsPaneOpen;
    }

    private void InitializeComponent()
    {
        AvaloniaXamlLoader.Load(this);
    }
}
