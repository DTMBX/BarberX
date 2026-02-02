namespace Evident.Mobile.Views;

using Evident.Mobile.ViewModels;

public partial class AnalysisListPage : ContentPage
{
    private readonly AnalysisListViewModel _viewModel;

    public AnalysisListPage(AnalysisListViewModel viewModel)
    {
        InitializeComponent();
        _viewModel = viewModel;
        BindingContext = _viewModel;
    }

    protected override async void OnAppearing()
    {
        base.OnAppearing();
        await _viewModel.InitializeAsync();
    }
}
