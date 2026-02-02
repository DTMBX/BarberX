using Evident.MatterDocket.MAUI.ViewModels;

namespace Evident.MatterDocket.MAUI.Views;

public partial class LoginPage : ContentPage
{
    public LoginPage(LoginViewModel viewModel)
    {
        InitializeComponent();
        BindingContext = viewModel;
    }
}
