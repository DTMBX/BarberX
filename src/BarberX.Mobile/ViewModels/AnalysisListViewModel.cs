namespace Evident.Mobile.ViewModels;

using System.Collections.ObjectModel;
using System.Windows.Input;
using Evident.Shared.Models;
using Evident.Shared.Services;

/// <summary>
/// ViewModel for BWC analysis list
/// </summary>
public class AnalysisListViewModel : BaseViewModel
{
    private readonly IApiClient _apiClient;
    private AnalysisResponse? _selectedAnalysis;

    public AnalysisListViewModel(IApiClient apiClient)
    {
        _apiClient = apiClient;
        Title = "My Analyses";
        
        Analyses = new ObservableCollection<AnalysisResponse>();
        
        LoadAnalysesCommand = new Command(async () => await LoadAnalysesAsync());
        RefreshCommand = new Command(async () => await RefreshAsync());
        ViewAnalysisCommand = new Command<AnalysisResponse>(async (analysis) => await ViewAnalysisAsync(analysis));
        DeleteAnalysisCommand = new Command<AnalysisResponse>(async (analysis) => await DeleteAnalysisAsync(analysis));
        UploadNewCommand = new Command(async () => await NavigateToUploadAsync());
    }

    public ObservableCollection<AnalysisResponse> Analyses { get; }

    public AnalysisResponse? SelectedAnalysis
    {
        get => _selectedAnalysis;
        set => SetProperty(ref _selectedAnalysis, value);
    }

    public ICommand LoadAnalysesCommand { get; }
    public ICommand RefreshCommand { get; }
    public ICommand ViewAnalysisCommand { get; }
    public ICommand DeleteAnalysisCommand { get; }
    public ICommand UploadNewCommand { get; }

    public async Task InitializeAsync()
    {
        await LoadAnalysesAsync();
    }

    private async Task LoadAnalysesAsync()
    {
        await ExecuteAsync(async () =>
        {
            var analyses = await _apiClient.GetUserAnalysesAsync();
            
            Analyses.Clear();
            foreach (var analysis in analyses.OrderByDescending(a => a.CreatedAt))
            {
                Analyses.Add(analysis);
            }
        });
    }

    private async Task RefreshAsync()
    {
        await LoadAnalysesAsync();
    }

    private async Task ViewAnalysisAsync(AnalysisResponse? analysis)
    {
        if (analysis == null)
            return;

        await Shell.Current.GoToAsync($"//AnalysisDetailPage?analysisId={analysis.AnalysisId}");
    }

    private async Task DeleteAnalysisAsync(AnalysisResponse? analysis)
    {
        if (analysis == null)
            return;

        var confirm = await Application.Current?.MainPage?.DisplayAlert(
            "Delete Analysis",
            $"Are you sure you want to delete this analysis?",
            "Delete",
            "Cancel") ?? false;

        if (!confirm)
            return;

        await ExecuteAsync(async () =>
        {
            var success = await _apiClient.DeleteAnalysisAsync(analysis.AnalysisId ?? "");
            
            if (success)
            {
                Analyses.Remove(analysis);
            }
            else
            {
                await Application.Current?.MainPage?.DisplayAlert(
                    "Error",
                    "Failed to delete analysis",
                    "OK");
            }
        });
    }

    private async Task NavigateToUploadAsync()
    {
        await Shell.Current.GoToAsync("//UploadPage");
    }
}
