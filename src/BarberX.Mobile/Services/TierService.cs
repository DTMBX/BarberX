using Evident.Shared.Models;

namespace Evident.Mobile.Services;

public interface ITierService
{
    Task<bool> CanAccessFeatureAsync(string featureName);
    Task<UsageLimits> GetUsageLimitsAsync();
    Task<SubscriptionInfo> GetSubscriptionInfoAsync();
    Task<bool> UpgradeSubscriptionAsync(string tierName);
    Task<bool> CheckUsageLimitAsync(string limitType, int increment = 0);
}

public class TierService : ITierService
{
    private readonly IApiClient _apiClient;

    public TierService(IApiClient apiClient)
    {
        _apiClient = apiClient;
    }

    public async Task<bool> CanAccessFeatureAsync(string featureName)
    {
        try
        {
            var subscription = await _apiClient.GetSubscriptionInfoAsync();
            var limits = GetTierLimits(subscription.Tier);
            
            return limits.Features.ContainsKey(featureName) && 
                   limits.Features[featureName];
        }
        catch
        {
            // Default to free tier restrictions
            return false;
        }
    }

    public async Task<UsageLimits> GetUsageLimitsAsync()
    {
        try
        {
            var subscription = await _apiClient.GetSubscriptionInfoAsync();
            var usage = await _apiClient.GetUsageStatsAsync();
            
            return GetTierLimits(subscription.Tier, usage);
        }
        catch
        {
            return GetFreeTierLimits();
        }
    }

    public async Task<SubscriptionInfo> GetSubscriptionInfoAsync()
    {
        try
        {
            return await _apiClient.GetSubscriptionInfoAsync();
        }
        catch
        {
            return new SubscriptionInfo
            {
                Tier = "FREE",
                IsActive = true,
                Features = new Dictionary<string, object>
                {
                    { "api_access", false },
                    { "timeline_builder", false },
                    { "forensic_analysis", false }
                }
            };
        }
    }

    public async Task<bool> UpgradeSubscriptionAsync(string tierName)
    {
        try
        {
            return await _apiClient.UpgradeSubscriptionAsync(tierName);
        }
        catch
        {
            return false;
        }
    }

    public async Task<bool> CheckUsageLimitAsync(string limitType, int increment = 0)
    {
        try
        {
            var limits = await GetUsageLimitsAsync();
            
            return limitType switch
            {
                "bwc_videos_per_month" => limits.BwcVideosProcessed + increment <= limits.BwcVideosPerMonth,
                "pdf_documents_per_month" => limits.PdfDocumentsProcessed + increment <= limits.PdfDocumentsPerMonth,
                "transcription_minutes_per_month" => limits.TranscriptionMinutesUsed + increment <= limits.TranscriptionMinutesPerMonth,
                "storage_gb" => limits.StorageUsedGb + (increment * 0.001) <= limits.StorageGb,
                _ => true
            };
        }
        catch
        {
            return false;
        }
    }

    private UsageLimits GetTierLimits(string tier, UsageStats? usage = null)
    {
        return tier.ToUpper() switch
        {
            "FREE" => GetFreeTierLimits(usage),
            "STARTER" => GetStarterTierLimits(usage),
            "PROFESSIONAL" => GetProfessionalTierLimits(usage),
            "PREMIUM" => GetPremiumTierLimits(usage),
            "ENTERPRISE" => GetEnterpriseTierLimits(usage),
            _ => GetFreeTierLimits(usage)
        };
    }

    private UsageLimits GetFreeTierLimits(UsageStats? usage = null)
    {
        return new UsageLimits
        {
            Tier = "FREE",
            BwcVideosPerMonth = 1,
            BwcVideosProcessed = usage?.BwcVideosProcessed ?? 0,
            PdfDocumentsPerMonth = 1,
            PdfDocumentsProcessed = usage?.PdfDocumentsProcessed ?? 0,
            TranscriptionMinutesPerMonth = 10,
            TranscriptionMinutesUsed = usage?.TranscriptionMinutesUsed ?? 0,
            StorageGb = 1,
            StorageUsedGb = usage?.StorageUsedMb / 1024.0 ?? 0,
            Features = new Dictionary<string, object>
            {
                { "api_access", false },
                { "timeline_builder", false },
                { "forensic_analysis", false },
                { "priority_support", false },
                { "white_label", false }
            }
        };
    }

    private UsageLimits GetStarterTierLimits(UsageStats? usage = null)
    {
        return new UsageLimits
        {
            Tier = "STARTER",
            BwcVideosPerMonth = 5,
            BwcVideosProcessed = usage?.BwcVideosProcessed ?? 0,
            PdfDocumentsPerMonth = 5,
            PdfDocumentsProcessed = usage?.PdfDocumentsProcessed ?? 0,
            TranscriptionMinutesPerMonth = 60,
            TranscriptionMinutesUsed = usage?.TranscriptionMinutesUsed ?? 0,
            StorageGb = 5,
            StorageUsedGb = usage?.StorageUsedMb / 1024.0 ?? 0,
            Features = new Dictionary<string, object>
            {
                { "api_access", true },
                { "timeline_builder", false },
                { "forensic_analysis", false },
                { "priority_support", false },
                { "white_label", false }
            }
        };
    }

    private UsageLimits GetProfessionalTierLimits(UsageStats? usage = null)
    {
        return new UsageLimits
        {
            Tier = "PROFESSIONAL",
            BwcVideosPerMonth = 25,
            BwcVideosProcessed = usage?.BwcVideosProcessed ?? 0,
            PdfDocumentsPerMonth = 25,
            PdfDocumentsProcessed = usage?.PdfDocumentsProcessed ?? 0,
            TranscriptionMinutesPerMonth = 300,
            TranscriptionMinutesUsed = usage?.TranscriptionMinutesUsed ?? 0,
            StorageGb = 25,
            StorageUsedGb = usage?.StorageUsedMb / 1024.0 ?? 0,
            Features = new Dictionary<string, object>
            {
                { "api_access", true },
                { "timeline_builder", true },
                { "forensic_analysis", true },
                { "priority_support", false },
                { "white_label", false }
            }
        };
    }

    private UsageLimits GetPremiumTierLimits(UsageStats? usage = null)
    {
        return new UsageLimits
        {
            Tier = "PREMIUM",
            BwcVideosPerMonth = -1, // Unlimited
            BwcVideosProcessed = usage?.BwcVideosProcessed ?? 0,
            PdfDocumentsPerMonth = -1, // Unlimited
            PdfDocumentsProcessed = usage?.PdfDocumentsProcessed ?? 0,
            TranscriptionMinutesPerMonth = -1, // Unlimited
            TranscriptionMinutesUsed = usage?.TranscriptionMinutesUsed ?? 0,
            StorageGb = 100,
            StorageUsedGb = usage?.StorageUsedMb / 1024.0 ?? 0,
            Features = new Dictionary<string, object>
            {
                { "api_access", true },
                { "timeline_builder", true },
                { "forensic_analysis", true },
                { "priority_support", true },
                { "white_label", false }
            }
        };
    }

    private UsageLimits GetEnterpriseTierLimits(UsageStats? usage = null)
    {
        return new UsageLimits
        {
            Tier = "ENTERPRISE",
            BwcVideosPerMonth = -1, // Unlimited
            BwcVideosProcessed = usage?.BwcVideosProcessed ?? 0,
            PdfDocumentsPerMonth = -1, // Unlimited
            PdfDocumentsProcessed = usage?.PdfDocumentsProcessed ?? 0,
            TranscriptionMinutesPerMonth = -1, // Unlimited
            TranscriptionMinutesUsed = usage?.TranscriptionMinutesUsed ?? 0,
            StorageGb = -1, // Unlimited
            StorageUsedGb = usage?.StorageUsedMb / 1024.0 ?? 0,
            Features = new Dictionary<string, object>
            {
                { "api_access", true },
                { "timeline_builder", true },
                { "forensic_analysis", true },
                { "priority_support", true },
                { "white_label", true }
            }
        };
    }
}

public class UsageLimits
{
    public string Tier { get; set; } = "FREE";
    public int BwcVideosPerMonth { get; set; }
    public int BwcVideosProcessed { get; set; }
    public int PdfDocumentsPerMonth { get; set; }
    public int PdfDocumentsProcessed { get; set; }
    public int TranscriptionMinutesPerMonth { get; set; }
    public int TranscriptionMinutesUsed { get; set; }
    public double StorageGb { get; set; }
    public double StorageUsedGb { get; set; }
    public Dictionary<string, object> Features { get; set; } = new();
}
