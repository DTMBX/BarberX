namespace Evident.Mobile.Services;

using Evident.Shared.Services;

/// <summary>
/// Authentication service for mobile app
/// </summary>
public class AuthService
{
    private readonly IApiClient _apiClient;
    private const string TokenKey = "auth_token";
    private const string UserIdKey = "user_id";

    public AuthService(IApiClient apiClient)
    {
        _apiClient = apiClient;
    }

    public bool IsAuthenticated => !string.IsNullOrEmpty(GetStoredToken());

    public async Task<(bool Success, string? ErrorMessage)> LoginAsync(string email, string password)
    {
        try
        {
            var response = await _apiClient.LoginAsync(email, password);
            
            if (response.Success && !string.IsNullOrEmpty(response.Token))
            {
                await SecureStorage.SetAsync(TokenKey, response.Token);
                await SecureStorage.SetAsync(UserIdKey, response.UserId ?? "");
                
                if (_apiClient is ApiClient client)
                {
                    client.SetAuthToken(response.Token);
                }
                
                return (true, null);
            }
            
            return (false, response.ErrorMessage ?? "Login failed");
        }
        catch (Exception ex)
        {
            return (false, ex.Message);
        }
    }

    public async Task<(bool Success, string? ErrorMessage)> RegisterAsync(string email, string password, string fullName)
    {
        try
        {
            var response = await _apiClient.RegisterAsync(email, password, fullName);
            
            if (response.Success && !string.IsNullOrEmpty(response.Token))
            {
                await SecureStorage.SetAsync(TokenKey, response.Token);
                await SecureStorage.SetAsync(UserIdKey, response.UserId ?? "");
                
                if (_apiClient is ApiClient client)
                {
                    client.SetAuthToken(response.Token);
                }
                
                return (true, null);
            }
            
            return (false, response.ErrorMessage ?? "Registration failed");
        }
        catch (Exception ex)
        {
            return (false, ex.Message);
        }
    }

    public async Task LogoutAsync()
    {
        try
        {
            await _apiClient.LogoutAsync();
        }
        catch
        {
            // Continue with local logout even if API call fails
        }
        
        SecureStorage.Remove(TokenKey);
        SecureStorage.Remove(UserIdKey);
    }

    public async Task<bool> RestoreSessionAsync()
    {
        var token = GetStoredToken();
        
        if (string.IsNullOrEmpty(token))
            return false;

        if (_apiClient is ApiClient client)
        {
            client.SetAuthToken(token);
        }

        try
        {
            // Verify token is still valid
            await _apiClient.GetProfileAsync();
            return true;
        }
        catch
        {
            // Token expired or invalid
            await LogoutAsync();
            return false;
        }
    }

    private string? GetStoredToken()
    {
        try
        {
            return SecureStorage.GetAsync(TokenKey).Result;
        }
        catch
        {
            return null;
        }
    }
}
