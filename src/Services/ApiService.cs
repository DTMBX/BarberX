using System.Net.Http.Headers;
using System.Net.Http.Json;
using System.Text.Json;
using Evident.MatterDocket.MAUI.Helpers;
using Evident.MatterDocket.MAUI.Models;

namespace Evident.MatterDocket.MAUI.Services;

public interface IApiService
{
    Task<ApiResponse<T>> GetAsync<T>(string endpoint);
    Task<ApiResponse<T>> PostAsync<T>(string endpoint, object data);
    Task<ApiResponse<T>> PutAsync<T>(string endpoint, object data);
    Task<ApiResponse<bool>> DeleteAsync(string endpoint);
    Task<ApiResponse<T>> PostMultipartAsync<T>(string endpoint, MultipartFormDataContent content, IProgress<double>? progress = null);
}

public class ApiService : IApiService
{
    private readonly HttpClient _httpClient;
    private readonly JsonSerializerOptions _jsonOptions;

    public ApiService()
    {
        _httpClient = new HttpClient
        {
            BaseAddress = new Uri(Constants.ApiBaseUrl),
            Timeout = TimeSpan.FromSeconds(Constants.ApiTimeoutSeconds)
        };

        _jsonOptions = new JsonSerializerOptions
        {
            PropertyNameCaseInsensitive = true,
            DefaultIgnoreCondition = System.Text.Json.Serialization.JsonIgnoreCondition.WhenWritingNull
        };
    }

    public async Task<bool> SetAuthTokenAsync(string token)
    {
        if (string.IsNullOrEmpty(token))
        {
            _httpClient.DefaultRequestHeaders.Authorization = null;
            await SecureStorage.SetAsync(Constants.AuthTokenKey, string.Empty);
            return true;
        }

        _httpClient.DefaultRequestHeaders.Authorization = new AuthenticationHeaderValue("Bearer", token);
        await SecureStorage.SetAsync(Constants.AuthTokenKey, token);
        return true;
    }

    public async Task<string?> GetAuthTokenAsync()
    {
        try
        {
            return await SecureStorage.GetAsync(Constants.AuthTokenKey);
        }
        catch
        {
            return null;
        }
    }

    public async Task<ApiResponse<T>> GetAsync<T>(string endpoint)
    {
        try
        {
            var response = await _httpClient.GetAsync(endpoint);
            
            if (response.IsSuccessStatusCode)
            {
                var content = await response.Content.ReadFromJsonAsync<T>(_jsonOptions);
                return new ApiResponse<T> { Success = true, Data = content };
            }

            var errorText = await response.Content.ReadAsStringAsync();
            var errorMessage = TryExtractError(errorText);
            return new ApiResponse<T> { Success = false, Error = errorMessage };
        }
        catch (Exception ex)
        {
            return new ApiResponse<T> { Success = false, Error = ex.Message };
        }
    }

    public async Task<ApiResponse<T>> PostAsync<T>(string endpoint, object data)
    {
        try
        {
            var response = await _httpClient.PostAsJsonAsync(endpoint, data, _jsonOptions);
            
            if (response.IsSuccessStatusCode)
            {
                var content = await response.Content.ReadFromJsonAsync<T>(_jsonOptions);
                return new ApiResponse<T> { Success = true, Data = content };
            }

            var errorText = await response.Content.ReadAsStringAsync();
            var errorMessage = TryExtractError(errorText);
            return new ApiResponse<T> { Success = false, Error = errorMessage };
        }
        catch (Exception ex)
        {
            return new ApiResponse<T> { Success = false, Error = ex.Message };
        }
    }

    public async Task<ApiResponse<T>> PutAsync<T>(string endpoint, object data)
    {
        try
        {
            var response = await _httpClient.PutAsJsonAsync(endpoint, data, _jsonOptions);
            
            if (response.IsSuccessStatusCode)
            {
                var content = await response.Content.ReadFromJsonAsync<T>(_jsonOptions);
                return new ApiResponse<T> { Success = true, Data = content };
            }

            var errorText = await response.Content.ReadAsStringAsync();
            var errorMessage = TryExtractError(errorText);
            return new ApiResponse<T> { Success = false, Error = errorMessage };
        }
        catch (Exception ex)
        {
            return new ApiResponse<T> { Success = false, Error = ex.Message };
        }
    }

    public async Task<ApiResponse<bool>> DeleteAsync(string endpoint)
    {
        try
        {
            var response = await _httpClient.DeleteAsync(endpoint);
            
            if (!response.IsSuccessStatusCode)
            {
                var errorText = await response.Content.ReadAsStringAsync();
                var errorMessage = TryExtractError(errorText);
                return new ApiResponse<bool> { Success = false, Error = errorMessage };
            }
            
            return new ApiResponse<bool> 
            { 
                Success = response.IsSuccessStatusCode,
                Data = response.IsSuccessStatusCode 
            };
        }
        catch (Exception ex)
        {
            return new ApiResponse<bool> { Success = false, Error = ex.Message };
        }
    }
    
    public async Task<ApiResponse<T>> PostMultipartAsync<T>(string endpoint, MultipartFormDataContent content, IProgress<double>? progress = null)
    {
        try
        {
            // For progress tracking, we'd need a custom HttpClient with progress handler
            // For now, simple implementation
            var response = await _httpClient.PostAsync(endpoint, content);
            
            if (response.IsSuccessStatusCode)
            {
                var result = await response.Content.ReadFromJsonAsync<T>(_jsonOptions);
                return new ApiResponse<T> { Success = true, Data = result };
            }

            var errorText = await response.Content.ReadAsStringAsync();
            var errorMessage = TryExtractError(errorText);
            return new ApiResponse<T> { Success = false, Error = errorMessage };
        }
        catch (Exception ex)
        {
            return new ApiResponse<T> { Success = false, Error = ex.Message };
        }
    }
    
    private string TryExtractError(string errorText)
    {
        try
        {
            var errorResponse = JsonSerializer.Deserialize<ErrorResponse>(errorText, _jsonOptions);
            return errorResponse?.Error ?? errorText;
        }
        catch
        {
            return errorText;
        }
    }
}
