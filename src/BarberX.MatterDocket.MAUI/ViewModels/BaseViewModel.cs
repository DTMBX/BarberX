using CommunityToolkit.Mvvm.ComponentModel;
using System;
using System.Threading.Tasks;

namespace Evident.MatterDocket.MAUI.ViewModels;

public partial class BaseViewModel : ObservableObject
{
    [ObservableProperty]
    private bool _isBusy;

    [ObservableProperty]
    private string _title = string.Empty;

    [ObservableProperty]
    private string _errorMessage = string.Empty;

    public bool IsNotBusy => !IsBusy;
    public bool HasError => !string.IsNullOrEmpty(ErrorMessage);

    /// <summary>
    /// Clears the current error message
    /// </summary>
    protected void ClearError()
    {
        ErrorMessage = string.Empty;
    }

    /// <summary>
    /// Sets an error message
    /// </summary>
    protected void SetError(string message)
    {
        ErrorMessage = message;
    }

    /// <summary>
    /// Executes an async task with IsBusy management and error handling
    /// </summary>
    protected async Task ExecuteAsync(Func<Task> operation, string errorPrefix = "An error occurred")
    {
        if (IsBusy)
            return;

        try
        {
            IsBusy = true;
            ClearError();
            await operation();
        }
        catch (Exception ex)
        {
            SetError($"{errorPrefix}: {ex.Message}");
        }
        finally
        {
            IsBusy = false;
        }
    }

    /// <summary>
    /// Executes an async task with return value, IsBusy management and error handling
    /// </summary>
    protected async Task<TResult> ExecuteAsync<TResult>(Func<Task<TResult>> operation, string errorPrefix = "An error occurred")
    {
        if (IsBusy)
            return default;

        try
        {
            IsBusy = true;
            ClearError();
            return await operation();
        }
        catch (Exception ex)
        {
            SetError($"{errorPrefix}: {ex.Message}");
            return default;
        }
        finally
        {
            IsBusy = false;
        }
    }
}

