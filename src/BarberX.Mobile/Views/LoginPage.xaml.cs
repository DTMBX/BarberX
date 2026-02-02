namespace Evident.Mobile.Views;

using Evident.Mobile.ViewModels;

public partial class LoginPage : ContentPage
{
    public LoginPage(LoginViewModel viewModel)
    {
        InitializeComponent();
        BindingContext = viewModel;
    }
}
