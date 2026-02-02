using Evident.MatterDocket.MAUI.Models;

namespace Evident.MatterDocket.MAUI.Services;

public interface IChatGptService
{
    Task<ApiResponse<ChatResponse>> SendMessageAsync(ChatRequest request);
    Task<ApiResponse<MessagesResponse>> GetConversationMessagesAsync(int conversationId);
    Task<ApiResponse<ApiKeyValidation>> ValidateApiKeyAsync(string apiKey);
    Task<ApiResponse<string>> StoreApiKeyAsync(string apiKey, string provider = "openai");
    Task<string?> GetStoredApiKeyAsync();
}

public class ChatGptService : IChatGptService
{
    private readonly IApiService _apiService;
    private const string ApiKeyStorageKey = "openai_api_key";

    public ChatGptService(IApiService apiService)
    {
        _apiService = apiService;
    }

    /// <summary>
    /// Send a message and get GPT response
    /// </summary>
    public async Task<ApiResponse<ChatResponse>> SendMessageAsync(ChatRequest request)
    {
        try
        {
            // Check if API key is configured
            var apiKey = await GetStoredApiKeyAsync();
            if (string.IsNullOrEmpty(apiKey))
            {
                return new ApiResponse<ChatResponse>
                {
                    Success = false,
                    Error = "No OpenAI API key configured. Please add your API key in settings."
                };
            }

            var response = await _apiService.PostAsync<ChatResponse>("/chat/completions", request);
            return response;
        }
        catch (Exception ex)
        {
            return new ApiResponse<ChatResponse>
            {
                Success = false,
                Error = $"Failed to send message: {ex.Message}"
            };
        }
    }

    /// <summary>
    /// Get all messages in a conversation
    /// </summary>
    public async Task<ApiResponse<MessagesResponse>> GetConversationMessagesAsync(int conversationId)
    {
        try
        {
            return await _apiService.GetAsync<MessagesResponse>($"/conversations/{conversationId}/messages");
        }
        catch (Exception ex)
        {
            return new ApiResponse<MessagesResponse>
            {
                Success = false,
                Error = $"Failed to get messages: {ex.Message}"
            };
        }
    }

    /// <summary>
    /// Validate an OpenAI API key
    /// </summary>
    public async Task<ApiResponse<ApiKeyValidation>> ValidateApiKeyAsync(string apiKey)
    {
        try
        {
            var request = new { api_key = apiKey };
            return await _apiService.PostAsync<ApiKeyValidation>("/openai/validate-key", request);
        }
        catch (Exception ex)
        {
            return new ApiResponse<ApiKeyValidation>
            {
                Success = false,
                Error = $"Failed to validate API key: {ex.Message}"
            };
        }
    }

    /// <summary>
    /// Store encrypted API key on server
    /// </summary>
    public async Task<ApiResponse<string>> StoreApiKeyAsync(string apiKey, string provider = "openai")
    {
        try
        {
            // Validate first
            var validation = await ValidateApiKeyAsync(apiKey);
            if (!validation.Success || validation.Data == null || !validation.Data.Valid)
            {
                return new ApiResponse<string>
                {
                    Success = false,
                    Error = validation.Data?.Error ?? "Invalid API key"
                };
            }

            // Store on server (encrypted)
            var request = new StoreApiKeyRequest
            {
                Provider = provider,
                ApiKey = apiKey
            };

            var response = await _apiService.PostAsync<object>("/user/api-keys", request);

            if (response.Success)
            {
                // Also store locally in SecureStorage
                await SecureStorage.SetAsync(ApiKeyStorageKey, apiKey);

                return new ApiResponse<string>
                {
                    Success = true,
                    Data = "API key stored successfully"
                };
            }

            return new ApiResponse<string>
            {
                Success = false,
                Error = response.Error ?? "Failed to store API key"
            };
        }
        catch (Exception ex)
        {
            return new ApiResponse<string>
            {
                Success = false,
                Error = $"Failed to store API key: {ex.Message}"
            };
        }
    }

    /// <summary>
    /// Get stored API key from SecureStorage
    /// </summary>
    public async Task<string?> GetStoredApiKeyAsync()
    {
        try
        {
            return await SecureStorage.GetAsync(ApiKeyStorageKey);
        }
        catch
        {
            return null;
        }
    }
}
