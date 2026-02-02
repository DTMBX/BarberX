using Evident.MatterDocket.MAUI.Helpers;
using Evident.MatterDocket.MAUI.Models;

namespace Evident.MatterDocket.MAUI.Services;

public interface IAuthService
{
    Task<LoginResult> LoginAsync(string email, string password);
    Task<LoginResult> RegisterAsync(string email, string password, string name);
    Task<bool> LogoutAsync();
    Task<bool> IsAuthenticatedAsync();
    Task<User?> GetCurrentUserAsync();
    Task<bool> RefreshTokenAsync();
}

public class AuthService : IAuthService
{
    private readonly ApiService _apiService;
    private User? _currentUser;

    public AuthService(ApiService apiService)
    {
        _apiService = apiService;
    }

    public async Task<LoginResult> LoginAsync(string email, string password)
    {
        try
        {
            var request = new LoginRequest
            {
                Email = email,
                Password = password
            };

            var response = await _apiService.PostAsync<LoginResponse>("/auth/login", request);

            if (response.Success && response.Data != null)
            {
                await StoreAuthDataAsync(response.Data);
                
                return new LoginResult 
                { 
                    Success = true, 
                    User = response.Data.User 
                };
            }

            return new LoginResult 
            { 
                Success = false, 
                ErrorMessage = response.Error ?? "Login failed. Please check your credentials." 
            };
        }
        catch (Exception ex)
        {
            return new LoginResult 
            { 
                Success = false, 
                ErrorMessage = $"Connection error: {ex.Message}" 
            };
        }
    }
    
    public async Task<LoginResult> RegisterAsync(string email, string password, string name)
    {
        try
        {
            var request = new RegisterRequest
            {
                Email = email,
                Password = password,
                Name = name
            };

            var response = await _apiService.PostAsync<LoginResponse>("/auth/register", request);

            if (response.Success && response.Data != null)
            {
                await StoreAuthDataAsync(response.Data);
                
                return new LoginResult 
                { 
                    Success = true, 
                    User = response.Data.User 
                };
            }

            return new LoginResult 
            { 
                Success = false, 
                ErrorMessage = response.Error ?? "Registration failed." 
            };
        }
        catch (Exception ex)
        {
            return new LoginResult 
            { 
                Success = false, 
                ErrorMessage = $"Connection error: {ex.Message}" 
            };
        }
    }

    public async Task<bool> LogoutAsync()
    {
        try
        {
            // Call logout endpoint (optional, as JWT is stateless)
            await _apiService.PostAsync<object>("/auth/logout", new {});
            
            // Clear auth token
            await _apiService.SetAuthTokenAsync(string.Empty);
            
            // Clear secure storage
            SecureStorage.Remove(Constants.AuthTokenKey);
            SecureStorage.Remove(Constants.UserIdKey);
            SecureStorage.Remove(Constants.UserEmailKey);
            SecureStorage.Remove(Constants.UserTierKey);
            SecureStorage.Remove(Constants.TokenExpiryKey);
            
            // Clear cached user
            _currentUser = null;
            
            return true;
        }
        catch
        {
            return false;
        }
    }

    public async Task<bool> IsAuthenticatedAsync()
    {
        try
        {
            var token = await _apiService.GetAuthTokenAsync();
            if (string.IsNullOrEmpty(token))
                return false;
            
            // Check if token is expired
            var expiryStr = await SecureStorage.GetAsync(Constants.TokenExpiryKey);
            if (!string.IsNullOrEmpty(expiryStr) && DateTime.TryParse(expiryStr, out var expiry))
            {
                if (expiry <= DateTime.UtcNow)
                {
                    // Token expired, try to refresh
                    return await RefreshTokenAsync();
                }
            }
            
            return true;
        }
        catch
        {
            return false;
        }
    }
    
    public async Task<bool> RefreshTokenAsync()
    {
        try
        {
            var response = await _apiService.PostAsync<RefreshTokenResponse>("/auth/refresh", new {});
            
            if (response.Success && response.Data != null)
            {
                // Update token
                await _apiService.SetAuthTokenAsync(response.Data.Token);
                
                // Update expiry
                var expiry = DateTime.UtcNow.AddSeconds(response.Data.ExpiresIn);
                await SecureStorage.SetAsync(Constants.TokenExpiryKey, expiry.ToString("o"));
                
                return true;
            }
            
            // Refresh failed, clear auth
            await LogoutAsync();
            return false;
        }
        catch
        {
            await LogoutAsync();
            return false;
        }
    }

    public async Task<User?> GetCurrentUserAsync()
    {
        if (_currentUser != null)
            return _currentUser;

        try
        {
            // Try to get from API
            var response = await _apiService.GetAsync<UserProfileResponse>("/auth/me");
            
            if (response.Success && response.Data?.User != null)
            {
                _currentUser = response.Data.User;
                return _currentUser;
            }
            
            // Fallback to cached data
            var userId = await SecureStorage.GetAsync(Constants.UserIdKey);
            var email = await SecureStorage.GetAsync(Constants.UserEmailKey);
            var tier = await SecureStorage.GetAsync(Constants.UserTierKey);

            if (!string.IsNullOrEmpty(userId) && !string.IsNullOrEmpty(email))
            {
                _currentUser = new User
                {
                    Id = int.Parse(userId),
                    Email = email,
                    Tier = tier ?? "FREE"
                };
                return _currentUser;
            }
        }
        catch
        {
            // Failed to retrieve user
        }

        return null;
    }
    
    private async Task StoreAuthDataAsync(LoginResponse loginResponse)
    {
        // Store authentication token
        await _apiService.SetAuthTokenAsync(loginResponse.Token);
        
        // Calculate and store expiry
        var expiry = DateTime.UtcNow.AddSeconds(loginResponse.ExpiresIn);
        await SecureStorage.SetAsync(Constants.TokenExpiryKey, expiry.ToString("o"));
        
        // Store user info in secure storage
        await SecureStorage.SetAsync(Constants.UserIdKey, loginResponse.User.Id.ToString());
        await SecureStorage.SetAsync(Constants.UserEmailKey, loginResponse.User.Email);
        await SecureStorage.SetAsync(Constants.UserTierKey, loginResponse.User.Tier);
        
        // Cache current user
        _currentUser = loginResponse.User;
    }
}

public class LoginResult
{
    public bool Success { get; set; }
    public User? User { get; set; }
    public string? ErrorMessage { get; set; }
}
