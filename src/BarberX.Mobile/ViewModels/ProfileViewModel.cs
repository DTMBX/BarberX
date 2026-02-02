using CommunityToolkit.Mvvm.ComponentModel;
using CommunityToolkit.Mvvm.Input;
using Evident.Shared.Services;

namespace Evident.Mobile.ViewModels;

public partial class ProfileViewModel : BaseViewModel
{
    private readonly IApiClient _apiClient;

    [ObservableProperty]
    private string fullName = string.Empty;

    [ObservableProperty]
    private string email = string.Empty;

    [ObservableProperty]
    private string tierLevel = "Free";

    [ObservableProperty]
    private string profileImageUrl = string.Empty;

    [ObservableProperty]
    private DateTime memberSince;

    [ObservableProperty]
    private DateTime lastLogin;

    [ObservableProperty]
    private string organization = "N/A";

    [ObservableProperty]
    private int videosAnalyzed;

    [ObservableProperty]
    private int documentsProcessed;

    [ObservableProperty]
    private string storageUsed = "0 MB";

    [ObservableProperty]
    private bool isFreeTier = true;

    public ProfileViewModel(IApiClient apiClient)
    {
        _apiClient = apiClient;
        Title = "Profile";
    }

    public async Task LoadProfileAsync()
    {
        if (IsBusy) return;

        try
        {
            IsBusy = true;

            var profile = await _apiClient.GetProfileAsync();
            FullName = profile.FullName ?? "User";
            Email = profile.Email ?? "";
            TierLevel = profile.Tier;
            Organization = profile.Organization ?? "N/A";
            MemberSince = profile.CreatedAt;
            IsFreeTier = profile.Tier == "FREE";

            var usage = await _apiClient.GetUsageStatsAsync();
            VideosAnalyzed = usage.BwcVideosProcessed;
            DocumentsProcessed = usage.PdfDocumentsProcessed;
            StorageUsed = $"{usage.StorageUsedMb:F2} MB";
        }
        catch (Exception ex)
        {
            await Shell.Current.DisplayAlert("Error", $"Failed to load profile: {ex.Message}", "OK");
        }
        finally
        {
            IsBusy = false;
        }
    }

    [RelayCommand]
    private async Task EditProfile()
    {
        string newName = await Shell.Current.DisplayPromptAsync(
            "Edit Profile",
            "Enter your full name:",
            initialValue: FullName);

        if (!string.IsNullOrWhiteSpace(newName))
        {
            FullName = newName;
            // TODO: Update via API
        }
    }

    [RelayCommand]
    private async Task ChangePassword()
    {
        await Shell.Current.DisplayAlert("Change Password", "This feature will be available soon.", "OK");
    }

    [RelayCommand]
    private async Task Upgrade()
    {
        await Shell.Current.GoToAsync("//settings");
    }
}
