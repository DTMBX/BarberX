using System.Collections.ObjectModel;
using System.Windows.Input;
using CommunityToolkit.Mvvm.ComponentModel;
using CommunityToolkit.Mvvm.Input;
using Evident.Shared.Services;

namespace Evident.Mobile.ViewModels;

public partial class DashboardViewModel : BaseViewModel
{
    private readonly IApiClient _apiClient;

    [ObservableProperty]
    private string userName = "User";

    [ObservableProperty]
    private int totalCases;

    [ObservableProperty]
    private int totalAnalyses;

    [ObservableProperty]
    private int totalDocuments;

    [ObservableProperty]
    private int totalVideos;

    [ObservableProperty]
    private bool isFreeTier = true;

    [ObservableProperty]
    private double usagePercentage;

    [ObservableProperty]
    private string usageText = "0 of 5 analyses used";

    [ObservableProperty]
    private ObservableCollection<ActivityItem> recentActivities = new();

    [ObservableProperty]
    private ActivityItem? selectedActivity;

    public DashboardViewModel(IApiClient apiClient)
    {
        _apiClient = apiClient;
        Title = "Dashboard";
    }

    public async Task InitializeAsync()
    {
        if (IsBusy) return;

        try
        {
            IsBusy = true;

            // Load user profile
            var profile = await _apiClient.GetProfileAsync();
            UserName = profile.FullName ?? "User";
            IsFreeTier = profile.Tier == "FREE";

            // Load usage stats
            var usage = await _apiClient.GetUsageStatsAsync();
            TotalAnalyses = usage.BwcVideosProcessed;
            TotalDocuments = usage.PdfDocumentsProcessed;
            
            // Calculate usage for free tier
            if (IsFreeTier && usage.MonthlyLimits != null)
            {
                if (usage.MonthlyLimits.TryGetValue("analyses", out int limit))
                {
                    UsagePercentage = (double)TotalAnalyses / limit;
                    UsageText = $"{TotalAnalyses} of {limit} analyses used";
                }
            }

            // Load recent activity
            await LoadRecentActivityAsync();
        }
        catch (Exception ex)
        {
            await Shell.Current.DisplayAlert("Error", $"Failed to load dashboard: {ex.Message}", "OK");
        }
        finally
        {
            IsBusy = false;
        }
    }

    private async Task LoadRecentActivityAsync()
    {
        // Load recent analyses
        var analyses = await _apiClient.GetUserAnalysesAsync();
        
        RecentActivities.Clear();
        foreach (var analysis in analyses.Take(5))
        {
            RecentActivities.Add(new ActivityItem
            {
                Icon = "video.png",
                Title = "Video Analysis Complete",
                Description = $"Analysis #{analysis.Id}",
                Timestamp = DateTime.Now.AddHours(-2) // Replace with actual timestamp
            });
        }
    }

    [RelayCommand]
    private async Task NavigateToUpload()
    {
        await Shell.Current.GoToAsync("//upload");
    }

    [RelayCommand]
    private async Task CreateNewCase()
    {
        await Shell.Current.GoToAsync("//cases");
    }

    [RelayCommand]
    private async Task Upgrade()
    {
        await Shell.Current.GoToAsync("//settings");
    }

    [RelayCommand]
    private async Task ActivitySelected()
    {
        if (SelectedActivity == null) return;

        await Shell.Current.GoToAsync($"analysisdetail?id={SelectedActivity.Id}");
        SelectedActivity = null;
    }
}

public class ActivityItem
{
    public string Id { get; set; } = Guid.NewGuid().ToString();
    public string Icon { get; set; } = string.Empty;
    public string Title { get; set; } = string.Empty;
    public string Description { get; set; } = string.Empty;
    public DateTime Timestamp { get; set; }
}
