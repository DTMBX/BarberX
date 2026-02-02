using Evident.MatterDocket.MAUI.ViewModels;

namespace Evident.MatterDocket.MAUI.Views;

public partial class DashboardPage : ContentPage
{
    public DashboardPage(DashboardViewModel viewModel)
    {
        InitializeComponent();
        BindingContext = viewModel;
    }

    protected override async void OnAppearing()
    {
        base.OnAppearing();
        
        // Load dashboard data when page appears
        if (BindingContext is DashboardViewModel viewModel)
        {
            await viewModel.LoadDashboardCommand.ExecuteAsync(null);
        }
    }
}
