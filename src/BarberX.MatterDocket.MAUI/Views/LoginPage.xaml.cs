using BarberX.MatterDocket.MAUI.ViewModels;

namespace BarberX.MatterDocket.MAUI.Views;

public partial class LoginPage : ContentPage
{
    public LoginPage(LoginViewModel viewModel)
    {
        InitializeComponent();
        BindingContext = viewModel;
    }
}
