using System.Collections.ObjectModel;
using CommunityToolkit.Mvvm.ComponentModel;
using CommunityToolkit.Mvvm.Input;
using Evident.Shared.Models;

namespace Evident.Mobile.ViewModels;

public partial class CasesViewModel : BaseViewModel
{
    [ObservableProperty]
    private ObservableCollection<CaseItem> cases = new();

    [ObservableProperty]
    private CaseItem? selectedCase;

    [ObservableProperty]
    private string searchText = string.Empty;

    public CasesViewModel()
    {
        Title = "Cases";
    }

    public async Task LoadCasesAsync()
    {
        if (IsBusy) return;

        try
        {
            IsBusy = true;
            Cases.Clear();

            // TODO: Load from API
            // For now, add sample data
            Cases.Add(new CaseItem
            {
                Id = "1",
                CaseNumber = "ATL-L-002794-25",
                Title = "Civil Rights Violation",
                ClientName = "Devon Tyler Barber",
                Status = "Active",
                StatusColor = Colors.Green,
                DocumentCount = 15,
                VideoCount = 3,
                UpdatedAt = DateTime.Now.AddDays(-2)
            });

            Cases.Add(new CaseItem
            {
                Id = "2",
                CaseNumber = "ATL-DC-007956-25",
                Title = "Municipal Court Matter",
                ClientName = "Devon Tyler Barber",
                Status = "Pending",
                StatusColor = Colors.Orange,
                DocumentCount = 8,
                VideoCount = 1,
                UpdatedAt = DateTime.Now.AddDays(-5)
            });
        }
        catch (Exception ex)
        {
            await Shell.Current.DisplayAlert("Error", $"Failed to load cases: {ex.Message}", "OK");
        }
        finally
        {
            IsBusy = false;
        }
    }

    [RelayCommand]
    private async Task Search()
    {
        await LoadCasesAsync();
        // TODO: Filter cases based on SearchText
    }

    [RelayCommand]
    private async Task CreateCase()
    {
        string caseNumber = await Shell.Current.DisplayPromptAsync(
            "New Case",
            "Enter case number:",
            placeholder: "ATL-L-XXXXXX-XX");

        if (!string.IsNullOrWhiteSpace(caseNumber))
        {
            // TODO: Create new case via API
            await LoadCasesAsync();
        }
    }

    [RelayCommand]
    private async Task CaseSelected()
    {
        if (SelectedCase == null) return;

        await Shell.Current.GoToAsync($"casedetail?id={SelectedCase.Id}");
        SelectedCase = null;
    }
}

public class CaseItem
{
    public string Id { get; set; } = string.Empty;
    public string CaseNumber { get; set; } = string.Empty;
    public string Title { get; set; } = string.Empty;
    public string ClientName { get; set; } = string.Empty;
    public string Status { get; set; } = string.Empty;
    public Color StatusColor { get; set; } = Colors.Gray;
    public int DocumentCount { get; set; }
    public int VideoCount { get; set; }
    public DateTime UpdatedAt { get; set; }
    public string ThumbnailUrl { get; set; } = string.Empty;
}
