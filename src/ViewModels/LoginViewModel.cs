using System.Windows.Input;
using CommunityToolkit.Mvvm.ComponentModel;
using CommunityToolkit.Mvvm.Input;
using Evident.MatterDocket.MAUI.Services;

namespace Evident.MatterDocket.MAUI.ViewModels;

public partial class LoginViewModel : BaseViewModel
{
    private readonly IAuthService _authService;

    [ObservableProperty]
    private string _email = string.Empty;

    [ObservableProperty]
    private string _password = string.Empty;

    [ObservableProperty]
    private bool _rememberMe = true;

    public LoginViewModel(IAuthService authService)
    {
        _authService = authService;
        Title = "Login to Evident Matter Docket";
    }

    [RelayCommand]
    private async Task LoginAsync()
    {
        // Validate input
        if (string.IsNullOrWhiteSpace(Email))
        {
            ErrorMessage = "Please enter your email address.";
            return;
        }

        if (string.IsNullOrWhiteSpace(Password))
        {
            ErrorMessage = "Please enter your password.";
            return;
        }

        if (!IsValidEmail(Email))
        {
            ErrorMessage = "Please enter a valid email address.";
            return;
        }

        IsBusy = true;
        ErrorMessage = string.Empty;

        try
        {
            var result = await _authService.LoginAsync(Email, Password);

            if (result.Success)
            {
                // Navigate to dashboard
                await Shell.Current.GoToAsync("//Dashboard");
            }
            else
            {
                ErrorMessage = result.ErrorMessage ?? "Login failed. Please try again.";
            }
        }
        catch (Exception ex)
        {
            ErrorMessage = $"An error occurred: {ex.Message}";
        }
        finally
        {
            IsBusy = false;
            Password = string.Empty; // Clear password for security
        }
    }

    [RelayCommand]
    private async Task NavigateToRegisterAsync()
    {
        // Navigate to in-app registration page
        await Shell.Current.GoToAsync("//Register");
    }

    [RelayCommand]
    private async Task RegisterAsync()
    {
        // Validate input
        if (string.IsNullOrWhiteSpace(Email))
        {
            ErrorMessage = "Please enter your email address.";
            return;
        }

        if (string.IsNullOrWhiteSpace(Password))
        {
            ErrorMessage = "Please enter your password.";
            return;
        }

        if (!IsValidEmail(Email))
        {
            ErrorMessage = "Please enter a valid email address.";
            return;
        }

        if (Password.Length < 8)
        {
            ErrorMessage = "Password must be at least 8 characters long.";
            return;
        }

        IsBusy = true;
        ErrorMessage = string.Empty;

        try
        {
            var name = Email.Split('@')[0]; // Use email prefix as default name
            var result = await _authService.RegisterAsync(Email, Password, name);

            if (result.Success)
            {
                // Navigate to dashboard
                await Shell.Current.GoToAsync("//Dashboard");
            }
            else
            {
                ErrorMessage = result.ErrorMessage ?? "Registration failed. Please try again.";
            }
        }
        catch (Exception ex)
        {
            ErrorMessage = $"An error occurred: {ex.Message}";
        }
        finally
        {
            IsBusy = false;
            Password = string.Empty; // Clear password for security
        }
    }

    [RelayCommand]
    private async Task ForgotPasswordAsync()
    {
        // Open forgot password page in browser
        await Browser.OpenAsync("https://Evident.info/auth/forgot-password", BrowserLaunchMode.SystemPreferred);
    }

    private bool IsValidEmail(string email)
    {
        try
        {
            var addr = new System.Net.Mail.MailAddress(email);
            return addr.Address == email;
        }
        catch
        {
            return false;
        }
    }
}
