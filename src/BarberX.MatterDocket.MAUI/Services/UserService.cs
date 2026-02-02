using Evident.MatterDocket.MAUI.Models;

namespace Evident.MatterDocket.MAUI.Services;

public interface IUserService
{
    Task<ApiResponse<UserProfile>> GetProfileAsync();
    Task<bool> UpdateProfileAsync(string name);
    Task<bool> ChangePasswordAsync(string currentPassword, string newPassword);
    Task<SubscriptionResponse?> GetSubscriptionAsync();
    Task<ApiResponse<UserUsage>> GetUsageStatsAsync();
}

public class UserService : IUserService
{
    private readonly ApiService _apiService;

    public UserService(ApiService apiService)
    {
        _apiService = apiService;
    }

    public async Task<ApiResponse<UserProfile>> GetProfileAsync()
    {
        try
        {
            var response = await _apiService.GetAsync<UserProfile>("/user/profile");
            return response;
        }
        catch
        {
            return new ApiResponse<UserProfile> { Success = false, Error = "Failed to get profile" };
        }
    }

    public async Task<bool> UpdateProfileAsync(string name)
    {
        try
        {
            var request = new UpdateProfileRequest { Name = name };
            var response = await _apiService.PutAsync<UserProfileResponse>("/user/profile", request);
            return response.Success;
        }
        catch
        {
            return false;
        }
    }

    public async Task<bool> ChangePasswordAsync(string currentPassword, string newPassword)
    {
        try
        {
            var request = new ChangePasswordRequest
            {
                CurrentPassword = currentPassword,
                NewPassword = newPassword
            };

            var response = await _apiService.PostAsync<object>("/user/change-password", request);
            return response.Success;
        }
        catch
        {
            return false;
        }
    }

    public async Task<SubscriptionResponse?> GetSubscriptionAsync()
    {
        try
        {
            var response = await _apiService.GetAsync<SubscriptionResponse>("/user/subscription");
            return response.Success ? response.Data : null;
        }
        catch
        {
            return null;
        }
    }

    public async Task<ApiResponse<UserUsage>> GetUsageStatsAsync()
    {
        try
        {
            var response = await _apiService.GetAsync<UserUsage>("/user/usage");
            return response;
        }
        catch
        {
            return new ApiResponse<UserUsage> { Success = false, Error = "Failed to get usage stats" };
        }
    }
}
