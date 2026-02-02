using System.Collections.ObjectModel;
using CommunityToolkit.Mvvm.ComponentModel;
using CommunityToolkit.Mvvm.Input;
using Evident.MatterDocket.MAUI.Services;
using Evident.MatterDocket.MAUI.Models;

namespace Evident.MatterDocket.MAUI.ViewModels;

public partial class DashboardViewModel : BaseViewModel
{
    private readonly IAuthService _authService;
    private readonly IUserService _userService;
    private readonly ICaseService _caseService;
    private readonly ITierService _tierService;

    [ObservableProperty]
    private UserProfile _currentUser;

    [ObservableProperty]
    private string _userTier = "FREE";

    [ObservableProperty]
    private int _totalCases;

    [ObservableProperty]
    private int _activeCases;

    [ObservableProperty]
    private long _storageUsedMB;

    [ObservableProperty]
    private long _storageAvailableMB = 1024;

    [ObservableProperty]
    private ObservableCollection<CaseListItem> _recentCases = new();

    [ObservableProperty]
    private ObservableCollection<AnalysisListItem> _recentAnalyses = new();

    public DashboardViewModel(
        IAuthService authService,
        IUserService userService,
        ICaseService caseService,
        ITierService tierService)
    {
        _authService = authService;
        _userService = userService;
        _caseService = caseService;
        _tierService = tierService;
        Title = "Dashboard";
    }

    /// <summary>
    /// Loads dashboard data
    /// </summary>
    [RelayCommand]
    private async Task LoadDashboardAsync()
    {
        await ExecuteAsync(async () =>
        {
            // Load user profile
            var profileResult = await _userService.GetProfileAsync();
            if (profileResult.Success)
            {
                CurrentUser = profileResult.Data;
                UserTier = profileResult.Data.Tier?.ToUpper() ?? "FREE";
            }

            // Load usage statistics
            var usageResult = await _userService.GetUsageStatsAsync();
            if (usageResult.Success)
            {
                TotalCases = usageResult.Data.TotalCases;
                StorageUsedMB = usageResult.Data.StorageUsedMB;
                
                // Calculate active cases (assuming status check)
                var casesResult = await _caseService.GetCasesAsync(1, 100);
                if (casesResult.Success)
                {
                    ActiveCases = casesResult.Data?.Count(c => c.Status == "Open") ?? 0;
                }
            }

            // Load recent cases
            var recentCasesResult = await _caseService.GetCasesAsync(1, 5);
            if (recentCasesResult.Success && recentCasesResult.Data != null)
            {
                RecentCases.Clear();
                foreach (var caseItem in recentCasesResult.Data)
                {
                    RecentCases.Add(caseItem);
                }
            }

        }, "Failed to load dashboard");
    }

    /// <summary>
    /// Navigate to upload page
    /// </summary>
    [RelayCommand]
    private async Task NavigateToUploadAsync()
    {
        await Shell.Current.GoToAsync("//Upload");
    }

    /// <summary>
    /// Navigate to cases page
    /// </summary>
    [RelayCommand]
    private async Task NavigateToCasesAsync()
    {
        await Shell.Current.GoToAsync("//Cases");
    }

    /// <summary>
    /// Navigate to settings page
    /// </summary>
    [RelayCommand]
    private async Task NavigateToSettingsAsync()
    {
        await Shell.Current.GoToAsync("//Settings");
    }

    /// <summary>
    /// Logout user
    /// </summary>
    [RelayCommand]
    private async Task LogoutAsync()
    {
        await ExecuteAsync(async () =>
        {
            await _authService.LogoutAsync();
            await Shell.Current.GoToAsync("//Login");
        }, "Failed to logout");
    }

    /// <summary>
    /// Navigate to case details
    /// </summary>
    [RelayCommand]
    private async Task ViewCaseAsync(CaseListItem caseItem)
    {
        if (caseItem == null) return;

        await Shell.Current.GoToAsync($"//CaseDetail?caseId={caseItem.Id}");
    }

    /// <summary>
    /// Upgrade tier
    /// </summary>
    [RelayCommand]
    private async Task UpgradeTierAsync()
    {
        await Shell.Current.GoToAsync("//Billing");
    }

    /// <summary>
    /// Refresh dashboard data
    /// </summary>
    [RelayCommand]
    private async Task RefreshAsync()
    {
        await LoadDashboardAsync();
    }

    /// <summary>
    /// Calculate storage percentage
    /// </summary>
    public double StoragePercentage
    {
        get
        {
            if (StorageAvailableMB == 0) return 0;
            return (double)StorageUsedMB / StorageAvailableMB * 100;
        }
    }

    /// <summary>
    /// Get storage color based on usage
    /// </summary>
    public Color StorageColor
    {
        get
        {
            var percentage = StoragePercentage;
            if (percentage >= 90) return Colors.Red;
            if (percentage >= 75) return Colors.Orange;
            return Colors.Green;
        }
    }
}
