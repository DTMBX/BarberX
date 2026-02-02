using System.Collections.ObjectModel;
using CommunityToolkit.Mvvm.ComponentModel;
using CommunityToolkit.Mvvm.Input;
using Evident.Shared.Models;

namespace Evident.Mobile.ViewModels;

[QueryProperty(nameof(CaseId), "id")]
public partial class CaseDetailViewModel : BaseViewModel
{
    [ObservableProperty]
    private string caseId = string.Empty;

    [ObservableProperty]
    private string caseNumber = string.Empty;

    [ObservableProperty]
    private string caseTitle = string.Empty;

    [ObservableProperty]
    private string description = string.Empty;

    [ObservableProperty]
    private string clientName = string.Empty;

    [ObservableProperty]
    private string status = string.Empty;

    [ObservableProperty]
    private DateTime createdAt;

    [ObservableProperty]
    private DateTime updatedAt;

    [ObservableProperty]
    private ObservableCollection<Document> documents = new();

    [ObservableProperty]
    private ObservableCollection<VideoAnalysis> videos = new();

    [ObservableProperty]
    private ObservableCollection<Timeline> timelineEvents = new();

    public CaseDetailViewModel()
    {
        Title = "Case Details";
    }

    partial void OnCaseIdChanged(string value)
    {
        if (!string.IsNullOrEmpty(value))
        {
            _ = LoadCaseDetailsAsync();
        }
    }

    private async Task LoadCaseDetailsAsync()
    {
        if (IsBusy) return;

        try
        {
            IsBusy = true;

            // TODO: Load from API
            // For now, use sample data
            CaseNumber = "ATL-L-002794-25";
            CaseTitle = "Civil Rights Violation";
            Description = "Case involving alleged civil rights violations by law enforcement officers.";
            ClientName = "Devon Tyler Barber";
            Status = "Active";
            CreatedAt = DateTime.Now.AddMonths(-3);
            UpdatedAt = DateTime.Now.AddDays(-2);

            // Sample documents
            Documents.Add(new Document
            {
                Id = "1",
                FileName = "Complaint.pdf",
                FileType = "PDF",
                FileSize = 1024000,
                UploadedAt = DateTime.Now.AddMonths(-2)
            });

            // Sample videos
            Videos.Add(new VideoAnalysis
            {
                Id = "1",
                VideoUrl = "https://example.com/video1.mp4",
                Duration = TimeSpan.FromMinutes(15),
                AnalyzedAt = DateTime.Now.AddDays(-5)
            });

            // Sample timeline
            TimelineEvents.Add(new Timeline
            {
                Timestamp = DateTime.Now.AddMonths(-3),
                Event = "Case Filed",
                Description = "Initial complaint filed with court",
                Source = "Court Records"
            });
        }
        catch (Exception ex)
        {
            await Shell.Current.DisplayAlert("Error", $"Failed to load case details: {ex.Message}", "OK");
        }
        finally
        {
            IsBusy = false;
        }
    }

    [RelayCommand]
    private async Task ViewDocuments()
    {
        await Shell.Current.GoToAsync("documents");
    }

    [RelayCommand]
    private async Task ViewVideos()
    {
        await Shell.Current.GoToAsync("analysis");
    }

    [RelayCommand]
    private async Task ViewDocument(Document document)
    {
        await Shell.Current.GoToAsync($"documentviewer?url={Uri.EscapeDataString(document.Url)}");
    }

    [RelayCommand]
    private async Task ViewVideo(VideoAnalysis video)
    {
        await Shell.Current.GoToAsync($"videoanalysis?id={video.Id}");
    }
}
