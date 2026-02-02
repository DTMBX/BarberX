using CommunityToolkit.Mvvm.ComponentModel;
using CommunityToolkit.Mvvm.Input;
using Evident.Shared.Services;

namespace Evident.Mobile.ViewModels;

public partial class SettingsViewModel : BaseViewModel
{
    private readonly IApiClient _apiClient;

    [ObservableProperty]
    private bool isDarkMode;

    [ObservableProperty]
    private bool notificationsEnabled = true;

    [ObservableProperty]
    private bool autoSyncEnabled = true;

    [ObservableProperty]
    private string currentTier = "Free";

    [ObservableProperty]
    private string subscriptionStatus = "Active";

    [ObservableProperty]
    private string appVersion = "1.0.0";

    public SettingsViewModel(IApiClient apiClient)
    {
        _apiClient = apiClient;
        Title = "Settings";
        LoadSettings();
    }

    private void LoadSettings()
    {
        IsDarkMode = Preferences.Get("dark_mode", false);
        NotificationsEnabled = Preferences.Get("notifications", true);
        AutoSyncEnabled = Preferences.Get("auto_sync", true);
    }

    partial void OnIsDarkModeChanged(bool value)
    {
        Preferences.Set("dark_mode", value);
        // TODO: Apply theme change
    }

    partial void OnNotificationsEnabledChanged(bool value)
    {
        Preferences.Set("notifications", value);
    }

    partial void OnAutoSyncEnabledChanged(bool value)
    {
        Preferences.Set("auto_sync", value);
    }

    [RelayCommand]
    private async Task ClearCache()
    {
        bool confirm = await Shell.Current.DisplayAlert(
            "Clear Cache",
            "Are you sure you want to clear the cache?",
            "Yes",
            "No");

        if (confirm)
        {
            // TODO: Clear cache
            await Shell.Current.DisplayAlert("Success", "Cache cleared successfully", "OK");
        }
    }

    [RelayCommand]
    private async Task DownloadData()
    {
        await Shell.Current.DisplayAlert("Download Data", "Your data export will be emailed to you within 24 hours.", "OK");
    }

    [RelayCommand]
    private async Task ViewPrivacyPolicy()
    {
        await Browser.OpenAsync("https://Evident.info/privacy", BrowserLaunchMode.SystemPreferred);
    }

    [RelayCommand]
    private async Task ManageSubscription()
    {
        await Shell.Current.DisplayAlert("Subscription", "Manage your subscription in the web portal.", "OK");
    }

    [RelayCommand]
    private async Task ViewTerms()
    {
        await Browser.OpenAsync("https://Evident.info/terms", BrowserLaunchMode.SystemPreferred);
    }

    [RelayCommand]
    private async Task ViewHelp()
    {
        await Browser.OpenAsync("https://Evident.info/help", BrowserLaunchMode.SystemPreferred);
    }

    [RelayCommand]
    private async Task Logout()
    {
        bool confirm = await Shell.Current.DisplayAlert(
            "Logout",
            "Are you sure you want to logout?",
            "Yes",
            "No");

        if (confirm)
        {
            Preferences.Clear();
            SecureStorage.RemoveAll();
            Application.Current.MainPage = new NavigationPage(new LoginPage());
        }
    }

    [RelayCommand]
    private async Task DeleteAccount()
    {
        bool confirm = await Shell.Current.DisplayAlert(
            "Delete Account",
            "This action cannot be undone. Are you sure?",
            "Delete",
            "Cancel");

        if (confirm)
        {
            // TODO: Call API to delete account
            await Shell.Current.DisplayAlert("Account Deleted", "Your account has been deleted.", "OK");
            Preferences.Clear();
            SecureStorage.RemoveAll();
            Application.Current.MainPage = new NavigationPage(new LoginPage());
        }
    }
}
