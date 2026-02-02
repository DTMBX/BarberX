using System.Collections.ObjectModel;
using CommunityToolkit.Mvvm.ComponentModel;
using CommunityToolkit.Mvvm.Input;

namespace Evident.Mobile.ViewModels;

[QueryProperty(nameof(VideoId), "id")]
public partial class VideoAnalysisViewModel : BaseViewModel
{
    [ObservableProperty]
    private string videoId = string.Empty;

    [ObservableProperty]
    private string videoUrl = string.Empty;

    [ObservableProperty]
    private string videoTitle = "Video Analysis";

    [ObservableProperty]
    private TimeSpan duration;

    [ObservableProperty]
    private TimeSpan currentPosition;

    [ObservableProperty]
    private bool isPlaying;

    [ObservableProperty]
    private ObservableCollection<string> keyFindings = new();

    [ObservableProperty]
    private string transcriptUrl = string.Empty;

    [ObservableProperty]
    private DateTime analyzedAt;

    public VideoAnalysisViewModel()
    {
        Title = "Video Analysis";
    }

    partial void OnVideoIdChanged(string value)
    {
        if (!string.IsNullOrEmpty(value))
        {
            _ = LoadVideoAnalysisAsync();
        }
    }

    private async Task LoadVideoAnalysisAsync()
    {
        if (IsBusy) return;

        try
        {
            IsBusy = true;

            // TODO: Load from API
            VideoTitle = $"Analysis #{VideoId}";
            VideoUrl = "https://example.com/video.mp4";
            Duration = TimeSpan.FromMinutes(15);
            AnalyzedAt = DateTime.Now.AddDays(-5);

            KeyFindings.Add("Officer identification visible at 00:45");
            KeyFindings.Add("Use of force incident at 03:22");
            KeyFindings.Add("Miranda rights read at 08:15");
            KeyFindings.Add("Witness statement recorded at 12:30");
        }
        catch (Exception ex)
        {
            await Shell.Current.DisplayAlert("Error", $"Failed to load video analysis: {ex.Message}", "OK");
        }
        finally
        {
            IsBusy = false;
        }
    }

    [RelayCommand]
    private void PlayPause()
    {
        IsPlaying = !IsPlaying;
    }

    [RelayCommand]
    private async Task ViewTranscript()
    {
        if (!string.IsNullOrEmpty(TranscriptUrl))
        {
            await Shell.Current.GoToAsync($"transcriptviewer?url={Uri.EscapeDataString(TranscriptUrl)}");
        }
        else
        {
            await Shell.Current.DisplayAlert("Transcript", "Transcript not available for this video.", "OK");
        }
    }

    [RelayCommand]
    private async Task Share()
    {
        try
        {
            await Share.Default.RequestAsync(new ShareTextRequest
            {
                Title = VideoTitle,
                Text = $"Video Analysis: {VideoUrl}"
            });
        }
        catch (Exception ex)
        {
            await Shell.Current.DisplayAlert("Error", $"Failed to share: {ex.Message}", "OK");
        }
    }

    [RelayCommand]
    private async Task ExportReport()
    {
        await Shell.Current.DisplayAlert("Export", "Report export will be available soon.", "OK");
    }
}
