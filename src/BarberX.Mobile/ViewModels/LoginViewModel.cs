namespace Evident.Mobile.ViewModels;

using System.Windows.Input;
using Evident.Mobile.Services;

/// <summary>
/// ViewModel for login page
/// </summary>
public class LoginViewModel : BaseViewModel
{
    private readonly AuthService _authService;
    private string _email = string.Empty;
    private string _password = string.Empty;
    private string _errorMessage = string.Empty;

    public LoginViewModel(AuthService authService)
    {
        _authService = authService;
        Title = "Login";
        
        LoginCommand = new Command(async () => await LoginAsync(), () => !IsBusy);
        RegisterCommand = new Command(async () => await NavigateToRegisterAsync());
    }

    public string Email
    {
        get => _email;
        set => SetProperty(ref _email, value);
    }

    public string Password
    {
        get => _password;
        set => SetProperty(ref _password, value);
    }

    public string ErrorMessage
    {
        get => _errorMessage;
        set => SetProperty(ref _errorMessage, value);
    }

    public ICommand LoginCommand { get; }
    public ICommand RegisterCommand { get; }

    private async Task LoginAsync()
    {
        if (string.IsNullOrWhiteSpace(Email) || string.IsNullOrWhiteSpace(Password))
        {
            ErrorMessage = "Please enter email and password";
            return;
        }

        await ExecuteAsync(async () =>
        {
            ErrorMessage = string.Empty;
            
            var (success, errorMessage) = await _authService.LoginAsync(Email, Password);
            
            if (success)
            {
                await Shell.Current.GoToAsync("//MainPage");
            }
            else
            {
                ErrorMessage = errorMessage ?? "Login failed";
            }
        });
    }

    private async Task NavigateToRegisterAsync()
    {
        await Shell.Current.GoToAsync("//RegisterPage");
    }
}
