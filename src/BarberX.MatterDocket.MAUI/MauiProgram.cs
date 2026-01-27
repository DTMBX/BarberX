using Microsoft.Extensions.Logging;
using BarberX.MatterDocket.MAUI.Services;
using BarberX.MatterDocket.MAUI.ViewModels;
using BarberX.MatterDocket.MAUI.Views;

namespace BarberX.MatterDocket.MAUI;

public static class MauiProgram
{
	public static MauiApp CreateMauiApp()
	{
		var builder = MauiApp.CreateBuilder();
		builder
			.UseMauiApp<App>()
			.ConfigureFonts(fonts =>
			{
				fonts.AddFont("OpenSans-Regular.ttf", "OpenSansRegular");
				fonts.AddFont("OpenSans-Semibold.ttf", "OpenSansSemibold");
			});

#if DEBUG
		builder.Logging.AddDebug();
#endif

		// Register Core Services
		builder.Services.AddSingleton<IApiService, ApiService>();
		builder.Services.AddSingleton<IAuthService, AuthService>();
		
		// Register Feature Services
		builder.Services.AddSingleton<IUploadService, UploadService>();
		builder.Services.AddSingleton<IAnalysisService, AnalysisService>();
		builder.Services.AddSingleton<IUserService, UserService>();
		builder.Services.AddSingleton<IBillingService, BillingService>();
		builder.Services.AddSingleton<IEvidenceService, EvidenceService>();
		builder.Services.AddSingleton<ITierService, TierService>();
		builder.Services.AddSingleton<ICaseService, CaseService>();
		
		// Register ChatGPT Services
		builder.Services.AddSingleton<IChatGptService, ChatGptService>();
		builder.Services.AddSingleton<IProjectService, ProjectService>();

		// Register ViewModels
		builder.Services.AddTransient<LoginViewModel>();
		builder.Services.AddTransient<DashboardViewModel>();
		builder.Services.AddTransient<UploadViewModel>();
		builder.Services.AddTransient<ChatViewModel>();

		// Register Pages
		builder.Services.AddTransient<LoginPage>();
		builder.Services.AddTransient<DashboardPage>();
		builder.Services.AddTransient<UploadPage>();
		builder.Services.AddTransient<ChatPage>();

		return builder.Build();
	}
}
