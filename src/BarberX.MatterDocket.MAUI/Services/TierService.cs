using Evident.MatterDocket.MAUI.Helpers;
using Evident.MatterDocket.MAUI.Models;
using System.Threading.Tasks;

namespace Evident.MatterDocket.MAUI.Services
{
    public interface ITierService
    {
        Task<ApiResponse<UserTier>> GetCurrentTierAsync();
        Task<bool> CanUploadPdfAsync(long fileSize);
        Task<bool> CanUploadVideoAsync(long fileSize);
        Task<bool> CanUseAiAnalysisAsync();
        string GetUpgradeMessage(string feature);
        long GetMaxPdfSize(string tier);
        long GetMaxVideoSize(string tier);
        bool IsFeatureAvailable(string feature, string tier);
    }

    public class TierService : ITierService
    {
        private readonly IApiService _apiService;
        private readonly IUserService _userService;

        public TierService(IApiService apiService, IUserService userService)
        {
            _apiService = apiService;
            _userService = userService;
        }

        /// <summary>
        /// Get the current user's tier information
        /// </summary>
        public async Task<ApiResponse<UserTier>> GetCurrentTierAsync()
        {
            try
            {
                var profileResponse = await _userService.GetProfileAsync();
                if (!profileResponse.Success)
                {
                    return new ApiResponse<UserTier>
                    {
                        Success = false,
                        Error = profileResponse.Error
                    };
                }

                var tier = profileResponse.Data.Tier?.ToUpper() ?? "FREE";
                
                return new ApiResponse<UserTier>
                {
                    Success = true,
                    Data = new UserTier
                    {
                        Name = tier,
                        MaxPdfSizeMB = GetMaxPdfSize(tier) / (1024 * 1024),
                        MaxVideoSizeMB = GetMaxVideoSize(tier) / (1024 * 1024),
                        CanUseAi = tier != "FREE",
                        CanUploadVideo = tier != "FREE"
                    }
                };
            }
            catch (Exception ex)
            {
                return new ApiResponse<UserTier>
                {
                    Success = false,
                    Error = $"Failed to get tier info: {ex.Message}"
                };
            }
        }

        /// <summary>
        /// Check if user can upload a PDF of given size
        /// </summary>
        public async Task<bool> CanUploadPdfAsync(long fileSize)
        {
            var tierResponse = await GetCurrentTierAsync();
            if (!tierResponse.Success) return false;

            var maxSize = GetMaxPdfSize(tierResponse.Data.Name);
            return fileSize <= maxSize;
        }

        /// <summary>
        /// Check if user can upload a video of given size
        /// </summary>
        public async Task<bool> CanUploadVideoAsync(long fileSize)
        {
            var tierResponse = await GetCurrentTierAsync();
            if (!tierResponse.Success) return false;

            // FREE tier cannot upload videos at all
            if (tierResponse.Data.Name == "FREE") return false;

            var maxSize = GetMaxVideoSize(tierResponse.Data.Name);
            return fileSize <= maxSize;
        }

        /// <summary>
        /// Check if user can use AI analysis features
        /// </summary>
        public async Task<bool> CanUseAiAnalysisAsync()
        {
            var tierResponse = await GetCurrentTierAsync();
            if (!tierResponse.Success) return false;

            // Only PRO, PREMIUM, and ENTERPRISE can use AI
            return tierResponse.Data.Name != "FREE";
        }

        /// <summary>
        /// Get the maximum PDF file size for a tier (in bytes)
        /// </summary>
        public long GetMaxPdfSize(string tier)
        {
            return tier?.ToUpper() switch
            {
                "FREE" => Constants.TierLimits.FreePdfMaxSize,
                "PRO" => Constants.TierLimits.ProPdfMaxSize,
                "PREMIUM" => Constants.TierLimits.PremiumPdfMaxSize,
                "ENTERPRISE" => Constants.TierLimits.EnterprisePdfMaxSize,
                _ => Constants.TierLimits.FreePdfMaxSize
            };
        }

        /// <summary>
        /// Get the maximum video file size for a tier (in bytes)
        /// </summary>
        public long GetMaxVideoSize(string tier)
        {
            return tier?.ToUpper() switch
            {
                "FREE" => 0, // No video uploads on FREE
                "PRO" => Constants.TierLimits.ProVideoMaxSize,
                "PREMIUM" => Constants.TierLimits.PremiumVideoMaxSize,
                "ENTERPRISE" => Constants.TierLimits.EnterpriseVideoMaxSize,
                _ => 0
            };
        }

        /// <summary>
        /// Check if a feature is available for a specific tier
        /// </summary>
        public bool IsFeatureAvailable(string feature, string tier)
        {
            var tierUpper = tier?.ToUpper() ?? "FREE";
            var featureLower = feature?.ToLower() ?? "";

            return featureLower switch
            {
                "video_upload" => tierUpper != "FREE",
                "ai_analysis" => tierUpper != "FREE",
                "ai_transcription" => tierUpper != "FREE",
                "ocr" => tierUpper != "FREE",
                "timeline_generation" => tierUpper != "FREE",
                "priority_processing" => tierUpper == "PREMIUM" || tierUpper == "ENTERPRISE",
                "self_hosted" => tierUpper == "ENTERPRISE",
                "api_access" => true, // All tiers have API access
                "pdf_upload" => true, // All tiers can upload PDFs
                _ => false
            };
        }

        /// <summary>
        /// Get an upgrade message for a feature
        /// </summary>
        public string GetUpgradeMessage(string feature)
        {
            return feature?.ToLower() switch
            {
                "video_upload" => "Upgrade to PRO or higher to upload video evidence.",
                "ai_analysis" => "Upgrade to PRO or higher to use AI-powered analysis.",
                "ai_transcription" => "Upgrade to PRO or higher to transcribe video evidence.",
                "ocr" => "Upgrade to PRO or higher to extract text from PDFs.",
                "timeline_generation" => "Upgrade to PRO or higher to generate case timelines.",
                "priority_processing" => "Upgrade to PREMIUM for priority AI processing.",
                "self_hosted" => "Upgrade to ENTERPRISE for self-hosted deployment.",
                "large_pdf" => "Your PDF exceeds the size limit. Upgrade to increase limits.",
                "large_video" => "Your video exceeds the size limit. Upgrade to increase limits.",
                _ => "Upgrade your plan to access this feature."
            };
        }
    }

    /// <summary>
    /// Represents user tier information
    /// </summary>
    public class UserTier
    {
        public string Name { get; set; }
        public long MaxPdfSizeMB { get; set; }
        public long MaxVideoSizeMB { get; set; }
        public bool CanUseAi { get; set; }
        public bool CanUploadVideo { get; set; }
    }
}
