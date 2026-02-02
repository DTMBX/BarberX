using CommunityToolkit.Mvvm.ComponentModel;
using CommunityToolkit.Mvvm.Input;

namespace Evident.Mobile.ViewModels;

[QueryProperty(nameof(TranscriptUrl), "url")]
public partial class TranscriptViewerViewModel : BaseViewModel
{
    [ObservableProperty]
    private string transcriptUrl = string.Empty;

    [ObservableProperty]
    private string transcriptText = string.Empty;

    [ObservableProperty]
    private bool isLoading = true;

    [ObservableProperty]
    private string searchText = string.Empty;

    public TranscriptViewerViewModel()
    {
        Title = "Transcript";
    }

    partial void OnTranscriptUrlChanged(string value)
    {
        if (!string.IsNullOrEmpty(value))
        {
            _ = LoadTranscriptAsync();
        }
    }

    private async Task LoadTranscriptAsync()
    {
        if (IsBusy) return;

        try
        {
            IsBusy = true;
            IsLoading = true;

            // TODO: Load from API
            await Task.Delay(1000); // Simulate loading

            TranscriptText = @"[00:00:00] Officer: Good evening, sir. License and registration please.
[00:00:05] Subject: What's the problem, officer?
[00:00:08] Officer: Your left taillight is out. I need to see your documents.
[00:00:12] Subject: Okay, let me get them from the glove box.
[00:00:15] Officer: Keep your hands where I can see them.
[00:00:18] Subject: I'm just getting my registration like you asked.
[00:00:22] Officer: Step out of the vehicle, please.
[00:00:25] Subject: Why? I haven't done anything wrong.
[00:00:28] Officer: I need you to step out now.
[00:00:32] Subject: Am I being detained?
[00:00:35] Officer: Yes, you are being detained for a traffic violation.";

            IsLoading = false;
        }
        catch (Exception ex)
        {
            await Shell.Current.DisplayAlert("Error", $"Failed to load transcript: {ex.Message}", "OK");
        }
        finally
        {
            IsBusy = false;
        }
    }

    [RelayCommand]
    private void Search()
    {
        if (string.IsNullOrWhiteSpace(SearchText))
        {
            return;
        }

        // TODO: Implement search highlighting
    }

    [RelayCommand]
    private async Task Copy()
    {
        try
        {
            await Clipboard.SetTextAsync(TranscriptText);
            await Shell.Current.DisplayAlert("Success", "Transcript copied to clipboard", "OK");
        }
        catch (Exception ex)
        {
            await Shell.Current.DisplayAlert("Error", $"Failed to copy: {ex.Message}", "OK");
        }
    }

    [RelayCommand]
    private async Task Share()
    {
        try
        {
            await Share.Default.RequestAsync(new ShareTextRequest
            {
                Title = "Transcript",
                Text = TranscriptText
            });
        }
        catch (Exception ex)
        {
            await Shell.Current.DisplayAlert("Error", $"Failed to share: {ex.Message}", "OK");
        }
    }
}
