namespace Evident.MatterDocket.MAUI.Helpers;

public static class Constants
{
    // API Configuration
    #if DEBUG
    public const string ApiBaseUrl = "http://localhost:5000/api/v1";
    #else
    public const string ApiBaseUrl = "https://Evident.info/api/v1";
    #endif
    
    public const string WebsiteUrl = "https://Evident.info";
    public const int ApiTimeoutSeconds = 30;
    
    // Application Info
    public const string AppName = "Evident Matter Docket (DTMB)";
    public const string AppVersion = "1.0.0";
    public const string ShortName = "DTMB";
    
    // Storage Keys
    public const string AuthTokenKey = "auth_token";
    public const string RefreshTokenKey = "refresh_token";
    public const string UserIdKey = "user_id";
    public const string UserEmailKey = "user_email";
    public const string UserTierKey = "user_tier";
    public const string TokenExpiryKey = "token_expiry";
    
    // Database
    public const string DatabaseFilename = "Evident_matterdocket.db";
    public const SQLite.SQLiteOpenFlags DatabaseFlags =
        SQLite.SQLiteOpenFlags.ReadWrite |
        SQLite.SQLiteOpenFlags.Create |
        SQLite.SQLiteOpenFlags.SharedCache;
    
    // UI Constants
    public const int MaxFileUploadSizeMB = 100;
    public const int DefaultPageSize = 20;
    public const int CacheDurationHours = 24;
    
    // Tier Limits (sync with backend)
    public static class TierLimits
    {
        // PDF Limits in bytes
        public const long FreePdfMaxSize = 10 * 1024 * 1024; // 10 MB
        public const long ProPdfMaxSize = 100 * 1024 * 1024; // 100 MB
        public const long PremiumPdfMaxSize = 500 * 1024 * 1024; // 500 MB
        public const long EnterprisePdfMaxSize = 5000L * 1024 * 1024; // 5 GB
        
        // Video Limits in bytes
        public const long ProVideoMaxSize = 1024L * 1024 * 1024; // 1 GB
        public const long PremiumVideoMaxSize = 5L * 1024 * 1024 * 1024; // 5 GB
        public const long EnterpriseVideoMaxSize = 20L * 1024 * 1024 * 1024; // 20 GB
        
        // Legacy MB/GB values for display
        public const int FreePdfSizeMB = 10;
        public const int ProPdfSizeMB = 100;
        public const int PremiumPdfSizeMB = 500;
        public const int EnterpriseMaxPdfSizeMB = 5000;
        
        public const int ProVideoSizeGB = 1;
        public const int PremiumVideoSizeGB = 5;
        public const int EnterpriseVideoSizeGB = 20;
    }
    
    // Branding Colors (from manifest.json)
    public const string PrimaryGold = "#d4a574";
    public const string BackgroundDark = "#0f0f0f";
    public const string SurfaceDark = "#1a1a1a";
}
