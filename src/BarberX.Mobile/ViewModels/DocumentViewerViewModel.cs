using CommunityToolkit.Mvvm.ComponentModel;
using CommunityToolkit.Mvvm.Input;

namespace Evident.Mobile.ViewModels;

[QueryProperty(nameof(DocumentUrl), "url")]
public partial class DocumentViewerViewModel : BaseViewModel
{
    [ObservableProperty]
    private string documentUrl = string.Empty;

    [ObservableProperty]
    private string documentTitle = "Document";

    [ObservableProperty]
    private bool isLoading = true;

    public DocumentViewerViewModel()
    {
        Title = "Document Viewer";
    }

    partial void OnDocumentUrlChanged(string value)
    {
        if (!string.IsNullOrEmpty(value))
        {
            IsLoading = false;
            DocumentTitle = Path.GetFileName(Uri.UnescapeDataString(value));
        }
    }

    [RelayCommand]
    private async Task Share()
    {
        try
        {
            await Share.Default.RequestAsync(new ShareTextRequest
            {
                Title = DocumentTitle,
                Text = DocumentUrl
            });
        }
        catch (Exception ex)
        {
            await Shell.Current.DisplayAlert("Error", $"Failed to share: {ex.Message}", "OK");
        }
    }

    [RelayCommand]
    private async Task Download()
    {
        await Shell.Current.DisplayAlert("Download", "Document download will be available soon.", "OK");
    }
}
