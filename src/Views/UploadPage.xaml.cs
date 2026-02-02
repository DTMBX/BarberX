using Evident.MatterDocket.MAUI.ViewModels;

namespace Evident.MatterDocket.MAUI.Views;

public partial class UploadPage : ContentPage
{
    public UploadPage(UploadViewModel viewModel)
    {
        InitializeComponent();
        BindingContext = viewModel;
    }
}
