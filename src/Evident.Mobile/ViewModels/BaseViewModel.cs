namespace Evident.Mobile.ViewModels;

using CommunityToolkit.Mvvm.ComponentModel;

/// <summary>
/// Base ViewModel using CommunityToolkit's ObservableObject for source-generator support
/// </summary>
public abstract class BaseViewModel : ObservableObject
{
    private bool _isBusy;
    private string _title = string.Empty;

    public bool IsBusy
    {
        get => _isBusy;
        set => SetProperty(ref _isBusy, value);
    }

    public string Title
    {
        get => _title;
        set => SetProperty(ref _title, value);
    }

    protected async Task ExecuteAsync(Func<Task> operation, string? loadingMessage = null)
    {
        if (IsBusy)
            return;

        IsBusy = true;

        try
        {
            await operation();
        }
        catch (Exception ex)
        {
            await HandleErrorAsync(ex);
        }
        finally
        {
            IsBusy = false;
        }
    }

    protected virtual async Task HandleErrorAsync(Exception exception)
    {
        await Application.Current?.MainPage?.DisplayAlert(
            "Error",
            exception.Message,
            "OK") ?? Task.CompletedTask;
    }
}
