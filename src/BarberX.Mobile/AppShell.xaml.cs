using Evident.Mobile.Views;

namespace Evident.Mobile
{
    public partial class AppShell : Shell
    {
        public AppShell()
        {
            InitializeComponent();
            RegisterRoutes();
        }

        private void RegisterRoutes()
        {
            // Register detail pages for navigation
            Routing.RegisterRoute("analysisdetail", typeof(AnalysisDetailPage));
            Routing.RegisterRoute("casedetail", typeof(CaseDetailPage));
            Routing.RegisterRoute("documentviewer", typeof(DocumentViewerPage));
            Routing.RegisterRoute("videoanalysis", typeof(VideoAnalysisPage));
            Routing.RegisterRoute("transcriptviewer", typeof(TranscriptViewerPage));
        }

        private async void OnHelpClicked(object sender, EventArgs e)
        {
            await Shell.Current.GoToAsync("//settings");
            // Navigate to help section
        }

        private async void OnLogoutClicked(object sender, EventArgs e)
        {
            bool confirm = await DisplayAlert(
                "Logout", 
                "Are you sure you want to logout?", 
                "Yes", 
                "No");

            if (confirm)
            {
                // Clear user session
                Preferences.Clear();
                SecureStorage.RemoveAll();
                
                // Navigate to login
                Application.Current.MainPage = new NavigationPage(new LoginPage());
            }
        }
    }
}
