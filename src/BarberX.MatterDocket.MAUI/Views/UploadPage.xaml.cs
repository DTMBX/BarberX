using BarberX.MatterDocket.MAUI.ViewModels;

namespace BarberX.MatterDocket.MAUI.Views;

public partial class UploadPage : ContentPage
{
    public UploadPage(UploadViewModel viewModel)
    {
        InitializeComponent();
        BindingContext = viewModel;
    }
}
