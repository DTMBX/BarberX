using Evident.Mobile.ViewModels;

namespace Evident.Mobile.Views;

public partial class CasesPage : ContentPage
{
    public CasesPage(CasesViewModel viewModel)
    {
        InitializeComponent();
        BindingContext = viewModel;
    }

    protected override async void OnAppearing()
    {
        base.OnAppearing();
        if (BindingContext is CasesViewModel vm)
        {
            await vm.LoadCasesAsync();
        }
    }
}
