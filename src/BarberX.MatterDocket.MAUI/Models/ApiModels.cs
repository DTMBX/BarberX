using System.Text.Json.Serialization;

namespace Evident.MatterDocket.MAUI.Models;

// Chat UI Helper Properties
public partial class ChatMessage
{
    public bool IsUserMessage => Role?.ToLower() == "user";
    public bool IsAssistantMessage => Role?.ToLower() == "assistant";
    public bool IsSystemMessage => Role?.ToLower() == "system";
    public bool IsMarkdownRendered => IsAssistantMessage && !string.IsNullOrEmpty(Content);
    public DateTime Timestamp { get; set; } = DateTime.Now; // For UI display
}

public partial class EvidenceItem
{
    public long FileSize { get; set; }
    public string FileType => Type; // Alias for UI binding
    public string? TranscriptionText { get; set; } // For chat context
}

// Generic API Response
public class ApiResponse<T>
{
    public bool Success { get; set; }
    public T? Data { get; set; }
    public string? Error { get; set; }
}

// Authentication Models
public class LoginRequest
{
    [JsonPropertyName("email")]
    public string Email { get; set; } = string.Empty;
    
    [JsonPropertyName("password")]
    public string Password { get; set; } = string.Empty;
}

public class RegisterRequest
{
    [JsonPropertyName("email")]
    public string Email { get; set; } = string.Empty;
    
    [JsonPropertyName("password")]
    public string Password { get; set; } = string.Empty;
    
    [JsonPropertyName("name")]
    public string Name { get; set; } = string.Empty;
}

public class LoginResponse
{
    [JsonPropertyName("token")]
    public string Token { get; set; } = string.Empty;
    
    [JsonPropertyName("expires_in")]
    public int ExpiresIn { get; set; }
    
    [JsonPropertyName("user")]
    public User User { get; set; } = new();
}

public class RefreshTokenResponse
{
    [JsonPropertyName("token")]
    public string Token { get; set; } = string.Empty;
    
    [JsonPropertyName("expires_in")]
    public int ExpiresIn { get; set; }
}

// User Models
public class User
{
    [JsonPropertyName("id")]
    public int Id { get; set; }
    
    [JsonPropertyName("email")]
    public string Email { get; set; } = string.Empty;
    
    [JsonPropertyName("name")]
    public string Name { get; set; } = string.Empty;
    
    [JsonPropertyName("tier")]
    public string Tier { get; set; } = "FREE";
    
    [JsonPropertyName("role")]
    public string Role { get; set; } = "user";
    
    [JsonPropertyName("is_active")]
    public bool IsActive { get; set; } = true;
    
    [JsonPropertyName("created_at")]
    public DateTime? CreatedAt { get; set; }
    
    [JsonPropertyName("last_login")]
    public DateTime? LastLogin { get; set; }
}

public class UserProfileResponse
{
    [JsonPropertyName("user")]
    public User User { get; set; } = new();
}

public class UpdateProfileRequest
{
    [JsonPropertyName("name")]
    public string? Name { get; set; }
}

public class ChangePasswordRequest
{
    [JsonPropertyName("current_password")]
    public string CurrentPassword { get; set; } = string.Empty;
    
    [JsonPropertyName("new_password")]
    public string NewPassword { get; set; } = string.Empty;
}

// Upload Models
public class UploadResponse
{
    [JsonPropertyName("file_id")]
    public int FileId { get; set; }
    
    [JsonPropertyName("filename")]
    public string Filename { get; set; } = string.Empty;
    
    [JsonPropertyName("original_filename")]
    public string OriginalFilename { get; set; } = string.Empty;
    
    [JsonPropertyName("size")]
    public long Size { get; set; }
    
    [JsonPropertyName("uploaded_at")]
    public DateTime UploadedAt { get; set; }
    
    [JsonPropertyName("path")]
    public string Path { get; set; } = string.Empty;
    
    [JsonPropertyName("status")]
    public string? Status { get; set; }
}

public class UploadStatusResponse
{
    [JsonPropertyName("file_id")]
    public int FileId { get; set; }
    
    [JsonPropertyName("status")]
    public string Status { get; set; } = string.Empty;
    
    [JsonPropertyName("progress")]
    public int Progress { get; set; }
    
    [JsonPropertyName("message")]
    public string? Message { get; set; }
}

// Analysis Models
public class StartAnalysisRequest
{
    [JsonPropertyName("file_id")]
    public int FileId { get; set; }
    
    [JsonPropertyName("analysis_type")]
    public string AnalysisType { get; set; } = "full";
}

public class StartAnalysisResponse
{
    [JsonPropertyName("analysis_id")]
    public string AnalysisId { get; set; } = string.Empty;
    
    [JsonPropertyName("file_id")]
    public int FileId { get; set; }
    
    [JsonPropertyName("analysis_type")]
    public string AnalysisType { get; set; } = string.Empty;
    
    [JsonPropertyName("status")]
    public string Status { get; set; } = string.Empty;
    
    [JsonPropertyName("created_at")]
    public DateTime CreatedAt { get; set; }
}

public class AnalysisResponse
{
    [JsonPropertyName("analysis_id")]
    public string AnalysisId { get; set; } = string.Empty;
    
    [JsonPropertyName("status")]
    public string Status { get; set; } = string.Empty;
    
    [JsonPropertyName("progress")]
    public int Progress { get; set; }
    
    [JsonPropertyName("results")]
    public AnalysisResults? Results { get; set; }
    
    [JsonPropertyName("completed_at")]
    public DateTime? CompletedAt { get; set; }
}

public class AnalysisResults
{
    [JsonPropertyName("transcription")]
    public string? Transcription { get; set; }
    
    [JsonPropertyName("entities")]
    public List<string>? Entities { get; set; }
    
    [JsonPropertyName("timeline")]
    public List<TimelineEvent>? Timeline { get; set; }
}

public class TimelineEvent
{
    [JsonPropertyName("timestamp")]
    public string Timestamp { get; set; } = string.Empty;
    
    [JsonPropertyName("event")]
    public string Event { get; set; } = string.Empty;
    
    [JsonPropertyName("confidence")]
    public double Confidence { get; set; }
}

public class AnalysisStatusResponse
{
    [JsonPropertyName("analysis_id")]
    public string AnalysisId { get; set; } = string.Empty;
    
    [JsonPropertyName("status")]
    public string Status { get; set; } = string.Empty;
    
    [JsonPropertyName("progress")]
    public int Progress { get; set; }
    
    [JsonPropertyName("estimated_completion")]
    public DateTime? EstimatedCompletion { get; set; }
}

public class AnalysisListResponse
{
    [JsonPropertyName("analyses")]
    public List<AnalysisSummary> Analyses { get; set; } = new();
    
    [JsonPropertyName("total")]
    public int Total { get; set; }
    
    [JsonPropertyName("page")]
    public int Page { get; set; }
    
    [JsonPropertyName("limit")]
    public int Limit { get; set; }
}

public class AnalysisSummary
{
    [JsonPropertyName("id")]
    public string Id { get; set; } = string.Empty;
    
    [JsonPropertyName("file_id")]
    public int FileId { get; set; }
    
    [JsonPropertyName("status")]
    public string Status { get; set; } = string.Empty;
    
    [JsonPropertyName("created_at")]
    public DateTime CreatedAt { get; set; }
}

// Evidence Models
public class Evidence
{
    [JsonPropertyName("id")]
    public int Id { get; set; }
    
    [JsonPropertyName("type")]
    public string Type { get; set; } = string.Empty;
    
    [JsonPropertyName("filename")]
    public string Filename { get; set; } = string.Empty;
    
    [JsonPropertyName("size")]
    public long Size { get; set; }
    
    [JsonPropertyName("status")]
    public string Status { get; set; } = "pending";
    
    [JsonPropertyName("uploaded_at")]
    public DateTime UploadedAt { get; set; }
}

public class EvidenceListResponse
{
    [JsonPropertyName("evidence")]
    public List<Evidence> Evidence { get; set; } = new();
    
    [JsonPropertyName("total")]
    public int Total { get; set; }
    
    [JsonPropertyName("page")]
    public int Page { get; set; }
    
    [JsonPropertyName("limit")]
    public int Limit { get; set; }
}

public class EvidenceResponse
{
    [JsonPropertyName("evidence")]
    public Evidence Evidence { get; set; } = new();
}

public class TranscribeJobResponse
{
    [JsonPropertyName("job_id")]
    public string JobId { get; set; } = string.Empty;
    
    [JsonPropertyName("evidence_id")]
    public int EvidenceId { get; set; }
    
    [JsonPropertyName("status")]
    public string Status { get; set; } = string.Empty;
    
    [JsonPropertyName("started_at")]
    public DateTime StartedAt { get; set; }
}

// Subscription Models
public class SubscriptionResponse
{
    [JsonPropertyName("tier")]
    public string Tier { get; set; } = string.Empty;
    
    [JsonPropertyName("plan_details")]
    public PlanDetails PlanDetails { get; set; } = new();
}

public class PlanDetails
{
    [JsonPropertyName("name")]
    public string Name { get; set; } = string.Empty;
    
    [JsonPropertyName("billing_period")]
    public string BillingPeriod { get; set; } = string.Empty;
    
    [JsonPropertyName("next_billing_date")]
    public DateTime? NextBillingDate { get; set; }
    
    [JsonPropertyName("amount")]
    public decimal Amount { get; set; }
}

public class UsageResponse
{
    [JsonPropertyName("uploads")]
    public UsageLimit Uploads { get; set; } = new();
    
    [JsonPropertyName("analyses")]
    public UsageLimit Analyses { get; set; } = new();
    
    [JsonPropertyName("storage_mb")]
    public UsageLimit StorageMb { get; set; } = new();
}

public class UsageLimit
{
    [JsonPropertyName("count")]
    public int Count { get; set; }
    
    [JsonPropertyName("used")]
    public int Used { get; set; }
    
    [JsonPropertyName("limit")]
    public int Limit { get; set; }
}

// Billing Models
public class CreateCheckoutRequest
{
    [JsonPropertyName("price_id")]
    public string PriceId { get; set; } = string.Empty;
    
    [JsonPropertyName("tier")]
    public string Tier { get; set; } = string.Empty;
}

public class CheckoutSessionResponse
{
    [JsonPropertyName("session_id")]
    public string SessionId { get; set; } = string.Empty;
    
    [JsonPropertyName("url")]
    public string Url { get; set; } = string.Empty;
}

public class BillingPortalResponse
{
    [JsonPropertyName("url")]
    public string Url { get; set; } = string.Empty;
}

// Error Models
public class ErrorResponse
{
    [JsonPropertyName("error")]
    public string Error { get; set; } = string.Empty;
}

// Additional Models for Services

public partial class EvidenceItem
{
    [JsonPropertyName("id")]
    public int Id { get; set; }
    
    [JsonPropertyName("filename")]
    public string Filename { get; set; } = string.Empty;
    
    [JsonPropertyName("type")]
    public string Type { get; set; } = string.Empty;
    
    [JsonPropertyName("size")]
    public long Size { get; set; }
    
    [JsonPropertyName("uploaded_at")]
    public DateTime UploadedAt { get; set; }
    
    [JsonPropertyName("status")]
    public string Status { get; set; } = "pending";
}

public class EvidenceDetails
{
    [JsonPropertyName("id")]
    public int Id { get; set; }
    
    [JsonPropertyName("filename")]
    public string Filename { get; set; } = string.Empty;
    
    [JsonPropertyName("original_filename")]
    public string OriginalFilename { get; set; } = string.Empty;
    
    [JsonPropertyName("type")]
    public string Type { get; set; } = string.Empty;
    
    [JsonPropertyName("size")]
    public long Size { get; set; }
    
    [JsonPropertyName("path")]
    public string Path { get; set; } = string.Empty;
    
    [JsonPropertyName("uploaded_at")]
    public DateTime UploadedAt { get; set; }
    
    [JsonPropertyName("status")]
    public string Status { get; set; } = "pending";
    
    [JsonPropertyName("transcription")]
    public string? Transcription { get; set; }
    
    [JsonPropertyName("ocr_text")]
    public string? OcrText { get; set; }
}

public class TranscriptionResult
{
    [JsonPropertyName("evidence_id")]
    public int EvidenceId { get; set; }
    
    [JsonPropertyName("text")]
    public string Text { get; set; } = string.Empty;
    
    [JsonPropertyName("language")]
    public string Language { get; set; } = "en";
    
    [JsonPropertyName("confidence")]
    public double Confidence { get; set; }
    
    [JsonPropertyName("duration")]
    public double Duration { get; set; }
}

public class OcrResult
{
    [JsonPropertyName("evidence_id")]
    public int EvidenceId { get; set; }
    
    [JsonPropertyName("text")]
    public string Text { get; set; } = string.Empty;
    
    [JsonPropertyName("pages")]
    public int Pages { get; set; }
    
    [JsonPropertyName("confidence")]
    public double Confidence { get; set; }
}

public class AnalysisListItem
{
    [JsonPropertyName("id")]
    public string Id { get; set; } = string.Empty;
    
    [JsonPropertyName("file_id")]
    public int FileId { get; set; }
    
    [JsonPropertyName("type")]
    public string Type { get; set; } = string.Empty;
    
    [JsonPropertyName("status")]
    public string Status { get; set; } = string.Empty;
    
    [JsonPropertyName("created_at")]
    public DateTime CreatedAt { get; set; }
    
    [JsonPropertyName("summary")]
    public string? Summary { get; set; }
}

public class UserProfile
{
    [JsonPropertyName("id")]
    public int Id { get; set; }
    
    [JsonPropertyName("email")]
    public string Email { get; set; } = string.Empty;
    
    [JsonPropertyName("name")]
    public string Name { get; set; } = string.Empty;
    
    [JsonPropertyName("tier")]
    public string Tier { get; set; } = "FREE";
    
    [JsonPropertyName("role")]
    public string Role { get; set; } = "user";
    
    [JsonPropertyName("is_active")]
    public bool IsActive { get; set; } = true;
    
    [JsonPropertyName("created_at")]
    public DateTime? CreatedAt { get; set; }
    
    [JsonPropertyName("last_login")]
    public DateTime? LastLogin { get; set; }
}

public class UserUsage
{
    [JsonPropertyName("total_cases")]
    public int TotalCases { get; set; }
    
    [JsonPropertyName("active_cases")]
    public int ActiveCases { get; set; }
    
    [JsonPropertyName("storage_used_mb")]
    public long StorageUsedMB { get; set; }
    
    [JsonPropertyName("storage_limit_mb")]
    public long StorageLimitMB { get; set; }
    
    [JsonPropertyName("uploads_this_month")]
    public int UploadsThisMonth { get; set; }
    
    [JsonPropertyName("analyses_this_month")]
    public int AnalysesThisMonth { get; set; }
}

public class UserSubscription
{
    [JsonPropertyName("tier")]
    public string Tier { get; set; } = "FREE";
    
    [JsonPropertyName("plan_name")]
    public string PlanName { get; set; } = string.Empty;
    
    [JsonPropertyName("status")]
    public string Status { get; set; } = "active";
    
    [JsonPropertyName("billing_period")]
    public string? BillingPeriod { get; set; }
    
    [JsonPropertyName("next_billing_date")]
    public DateTime? NextBillingDate { get; set; }
    
    [JsonPropertyName("amount")]
    public decimal? Amount { get; set; }
}

public class CheckoutSession
{
    [JsonPropertyName("session_id")]
    public string SessionId { get; set; } = string.Empty;
    
    [JsonPropertyName("url")]
    public string Url { get; set; } = string.Empty;
    
    [JsonPropertyName("tier")]
    public string Tier { get; set; } = string.Empty;
}

public class BillingPortal
{
    [JsonPropertyName("url")]
    public string Url { get; set; } = string.Empty;
}

// ChatGPT Integration Models

public class ChatRequest
{
    [JsonPropertyName("project_id")]
    public int ProjectId { get; set; }
    
    [JsonPropertyName("conversation_id")]
    public int? ConversationId { get; set; }
    
    [JsonPropertyName("message")]
    public string Message { get; set; } = string.Empty;
    
    [JsonPropertyName("include_context")]
    public bool IncludeContext { get; set; } = true;
    
    [JsonPropertyName("stream")]
    public bool Stream { get; set; } = false;
    
    [JsonPropertyName("context")]
    public string? Context { get; set; }
    
    [JsonPropertyName("evidence_ids")]
    public List<int>? AttachedEvidenceIds { get; set; }
}

public class ChatResponse
{
    [JsonPropertyName("conversation_id")]
    public int ConversationId { get; set; }
    
    [JsonPropertyName("message_id")]
    public int MessageId { get; set; }
    
    [JsonPropertyName("role")]
    public string Role { get; set; } = "assistant";
    
    [JsonPropertyName("content")]
    public string Content { get; set; } = string.Empty;
    
    [JsonPropertyName("tokens_used")]
    public int TokensUsed { get; set; }
    
    [JsonPropertyName("model")]
    public string Model { get; set; } = string.Empty;
}

public partial class ChatMessage
{
    [JsonPropertyName("id")]
    public int Id { get; set; }
    
    [JsonPropertyName("role")]
    public string Role { get; set; } = string.Empty;
    
    [JsonPropertyName("content")]
    public string Content { get; set; } = string.Empty;
    
    [JsonPropertyName("tokens_used")]
    public int? TokensUsed { get; set; }
    
    [JsonPropertyName("model")]
    public string? Model { get; set; }
    
    [JsonPropertyName("created_at")]
    public DateTime CreatedAt { get; set; }
    
    // UI helpers
    public bool IsUser => Role == "user";
    public bool IsAssistant => Role == "assistant";
    public bool IsSystem => Role == "system";
}

public class Project
{
    [JsonPropertyName("id")]
    public int Id { get; set; }
    
    [JsonPropertyName("name")]
    public string Name { get; set; } = string.Empty;
    
    [JsonPropertyName("description")]
    public string? Description { get; set; }
    
    [JsonPropertyName("custom_instructions")]
    public string? CustomInstructions { get; set; }
    
    [JsonPropertyName("model_preference")]
    public string ModelPreference { get; set; } = "gpt-4";
    
    [JsonPropertyName("max_tokens")]
    public int MaxTokens { get; set; } = 4000;
    
    [JsonPropertyName("temperature")]
    public double Temperature { get; set; } = 0.7;
    
    [JsonPropertyName("conversation_count")]
    public int ConversationCount { get; set; }
    
    [JsonPropertyName("created_at")]
    public DateTime CreatedAt { get; set; }
    
    [JsonPropertyName("updated_at")]
    public DateTime UpdatedAt { get; set; }
}

public class CreateProjectRequest
{
    [JsonPropertyName("name")]
    public string Name { get; set; } = string.Empty;
    
    [JsonPropertyName("description")]
    public string? Description { get; set; }
    
    [JsonPropertyName("custom_instructions")]
    public string? CustomInstructions { get; set; }
    
    [JsonPropertyName("model_preference")]
    public string ModelPreference { get; set; } = "gpt-4";
}

public class Conversation
{
    [JsonPropertyName("id")]
    public int Id { get; set; }
    
    [JsonPropertyName("project_id")]
    public int ProjectId { get; set; }
    
    [JsonPropertyName("title")]
    public string Title { get; set; } = "New Conversation";
    
    [JsonPropertyName("message_count")]
    public int MessageCount { get; set; }
    
    [JsonPropertyName("last_message_at")]
    public DateTime? LastMessageAt { get; set; }
    
    [JsonPropertyName("created_at")]
    public DateTime CreatedAt { get; set; }
}

public class ApiKeyInfo
{
    [JsonPropertyName("id")]
    public int Id { get; set; }
    
    [JsonPropertyName("provider")]
    public string Provider { get; set; } = "openai";
    
    [JsonPropertyName("masked_key")]
    public string MaskedKey { get; set; } = string.Empty;
    
    [JsonPropertyName("is_active")]
    public bool IsActive { get; set; }
    
    [JsonPropertyName("last_validated")]
    public DateTime? LastValidated { get; set; }
}

public class ApiKeyValidation
{
    [JsonPropertyName("valid")]
    public bool Valid { get; set; }
    
    [JsonPropertyName("organization")]
    public string? Organization { get; set; }
    
    [JsonPropertyName("quota_remaining")]
    public long? QuotaRemaining { get; set; }
    
    [JsonPropertyName("models_available")]
    public List<string> ModelsAvailable { get; set; } = new();
    
    [JsonPropertyName("error")]
    public string? Error { get; set; }
}

public class StoreApiKeyRequest
{
    [JsonPropertyName("provider")]
    public string Provider { get; set; } = "openai";
    
    [JsonPropertyName("api_key")]
    public string ApiKey { get; set; } = string.Empty;
}

public class MessagesResponse
{
    [JsonPropertyName("conversation")]
    public Conversation Conversation { get; set; } = new();
    
    [JsonPropertyName("messages")]
    public List<ChatMessage> Messages { get; set; } = new();
}

public class ProjectsResponse
{
    [JsonPropertyName("projects")]
    public List<Project> Projects { get; set; } = new();
}

public class ConversationsResponse
{
    [JsonPropertyName("conversations")]
    public List<Conversation> Conversations { get; set; } = new();
}

public class ApiKeysResponse
{
    [JsonPropertyName("keys")]
    public List<ApiKeyInfo> Keys { get; set; } = new();
}
