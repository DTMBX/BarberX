namespace Evident.Shared.Services;

using System.Net.Http.Headers;
using System.Net.Http.Json;
using System.Text.Json;
using Evident.Shared.Models;

/// <summary>
/// HTTP-based API client implementation for all platforms
/// </summary>
public class ApiClient : IApiClient
{
    private readonly HttpClient _httpClient;
    private readonly JsonSerializerOptions _jsonOptions;
    private string? _authToken;

    public ApiClient(HttpClient httpClient)
    {
        _httpClient = httpClient;
        _jsonOptions = new JsonSerializerOptions
        {
            PropertyNameCaseInsensitive = true,
            PropertyNamingPolicy = JsonNamingPolicy.CamelCase
        };
    }

    public void SetAuthToken(string token)
    {
        _authToken = token;
        _httpClient.DefaultRequestHeaders.Authorization = new AuthenticationHeaderValue("Bearer", token);
    }

    // Authentication
    public async Task<AuthResponse> LoginAsync(string email, string password)
    {
        var response = await _httpClient.PostAsJsonAsync("/auth/login", new { email, password });
        return await response.Content.ReadFromJsonAsync<AuthResponse>(_jsonOptions) ?? new AuthResponse();
    }

    public async Task<AuthResponse> RegisterAsync(string email, string password, string fullName)
    {
        var response = await _httpClient.PostAsJsonAsync("/auth/register", new { email, password, full_name = fullName });
        return await response.Content.ReadFromJsonAsync<AuthResponse>(_jsonOptions) ?? new AuthResponse();
    }

    public async Task LogoutAsync()
    {
        await _httpClient.PostAsync("/auth/logout", null);
        _authToken = null;
        _httpClient.DefaultRequestHeaders.Authorization = null;
    }

    public async Task<UserProfile> GetProfileAsync()
    {
        return await _httpClient.GetFromJsonAsync<UserProfile>("/auth/profile", _jsonOptions) ?? new UserProfile();
    }

    // BWC Analysis
    public async Task<AnalysisResponse> UploadVideoAsync(Stream videoStream, AnalysisRequest request, IProgress<double>? progress = null)
    {
        using var content = new MultipartFormDataContent();
        
        var streamContent = new StreamContent(videoStream);
        streamContent.Headers.ContentType = new MediaTypeHeaderValue("video/mp4");
        content.Add(streamContent, "file", request.FileName ?? "video.mp4");
        
        if (!string.IsNullOrEmpty(request.CaseNumber))
            content.Add(new StringContent(request.CaseNumber), "case_number");
        if (!string.IsNullOrEmpty(request.OfficerName))
            content.Add(new StringContent(request.OfficerName), "officer_name");
        if (request.IncidentDate.HasValue)
            content.Add(new StringContent(request.IncidentDate.Value.ToString("yyyy-MM-dd")), "incident_date");
        if (!string.IsNullOrEmpty(request.Location))
            content.Add(new StringContent(request.Location), "location");
        if (!string.IsNullOrEmpty(request.Description))
            content.Add(new StringContent(request.Description), "description");

        var response = await _httpClient.PostAsync("/api/upload", content);
        response.EnsureSuccessStatusCode();
        
        return await response.Content.ReadFromJsonAsync<AnalysisResponse>(_jsonOptions) ?? new AnalysisResponse();
    }

    public async Task<AnalysisResponse> GetAnalysisStatusAsync(string analysisId)
    {
        return await _httpClient.GetFromJsonAsync<AnalysisResponse>($"/api/analysis/{analysisId}/status", _jsonOptions) ?? new AnalysisResponse();
    }

    public async Task<AnalysisResponse> GetAnalysisResultsAsync(string analysisId)
    {
        return await _httpClient.GetFromJsonAsync<AnalysisResponse>($"/api/analysis/{analysisId}", _jsonOptions) ?? new AnalysisResponse();
    }

    public async Task<List<AnalysisResponse>> GetUserAnalysesAsync()
    {
        return await _httpClient.GetFromJsonAsync<List<AnalysisResponse>>("/api/analyses", _jsonOptions) ?? new List<AnalysisResponse>();
    }

    public async Task<bool> DeleteAnalysisAsync(string analysisId)
    {
        var response = await _httpClient.DeleteAsync($"/api/analysis/{analysisId}");
        return response.IsSuccessStatusCode;
    }

    // PDF Processing
    public async Task<PdfUploadResponse> UploadPdfAsync(Stream pdfStream, string fileName, IProgress<double>? progress = null)
    {
        using var content = new MultipartFormDataContent();
        
        var streamContent = new StreamContent(pdfStream);
        streamContent.Headers.ContentType = new MediaTypeHeaderValue("application/pdf");
        content.Add(streamContent, "file", fileName);

        var response = await _httpClient.PostAsync("/api/upload/pdf", content);
        response.EnsureSuccessStatusCode();
        
        return await response.Content.ReadFromJsonAsync<PdfUploadResponse>(_jsonOptions) ?? new PdfUploadResponse();
    }

    public async Task<List<PdfDocument>> GetUserPdfsAsync()
    {
        return await _httpClient.GetFromJsonAsync<List<PdfDocument>>("/api/pdfs", _jsonOptions) ?? new List<PdfDocument>();
    }

    public async Task<PdfAnalysisResult> AnalyzePdfAsync(string pdfId)
    {
        var response = await _httpClient.PostAsync($"/api/pdf/{pdfId}/analyze", null);
        response.EnsureSuccessStatusCode();
        return await response.Content.ReadFromJsonAsync<PdfAnalysisResult>(_jsonOptions) ?? new PdfAnalysisResult();
    }

    public async Task<bool> DeletePdfAsync(string pdfId)
    {
        var response = await _httpClient.DeleteAsync($"/api/pdf/{pdfId}");
        return response.IsSuccessStatusCode;
    }

    // Legal Analysis
    public async Task<ViolationScanResult> ScanViolationsAsync(string transcript, Dictionary<string, object>? context = null)
    {
        var payload = new { transcript, context };
        var response = await _httpClient.PostAsJsonAsync("/api/legal/scan-violations", payload);
        response.EnsureSuccessStatusCode();
        return await response.Content.ReadFromJsonAsync<ViolationScanResult>(_jsonOptions) ?? new ViolationScanResult();
    }

    public async Task<ComplianceCheckResult> CheckComplianceAsync(Dictionary<string, object> evidence)
    {
        var payload = new { evidence };
        var response = await _httpClient.PostAsJsonAsync("/api/legal/check-compliance", payload);
        response.EnsureSuccessStatusCode();
        return await response.Content.ReadFromJsonAsync<ComplianceCheckResult>(_jsonOptions) ?? new ComplianceCheckResult();
    }

    public async Task<CombinedLegalAnalysis> RunCombinedAnalysisAsync(string transcript, Dictionary<string, object> evidence)
    {
        var payload = new { transcript, evidence };
        var response = await _httpClient.PostAsJsonAsync("/api/legal/combined-analysis", payload);
        response.EnsureSuccessStatusCode();
        return await response.Content.ReadFromJsonAsync<CombinedLegalAnalysis>(_jsonOptions) ?? new CombinedLegalAnalysis();
    }

    // Transcription & OCR
    public async Task<TranscriptionResult> TranscribeAudioAsync(Stream audioStream, string language = "en")
    {
        using var content = new MultipartFormDataContent();
        
        var streamContent = new StreamContent(audioStream);
        streamContent.Headers.ContentType = new MediaTypeHeaderValue("audio/mpeg");
        content.Add(streamContent, "file", "audio.mp3");
        content.Add(new StringContent(language), "language");

        var response = await _httpClient.PostAsync("/api/evidence/transcribe", content);
        response.EnsureSuccessStatusCode();
        
        return await response.Content.ReadFromJsonAsync<TranscriptionResult>(_jsonOptions) ?? new TranscriptionResult();
    }

    public async Task<OcrResult> ExtractTextAsync(Stream imageStream, string language = "eng")
    {
        using var content = new MultipartFormDataContent();
        
        var streamContent = new StreamContent(imageStream);
        streamContent.Headers.ContentType = new MediaTypeHeaderValue("image/png");
        content.Add(streamContent, "file", "image.png");
        content.Add(new StringContent(language), "language");

        var response = await _httpClient.PostAsync("/api/evidence/ocr", content);
        response.EnsureSuccessStatusCode();
        
        return await response.Content.ReadFromJsonAsync<OcrResult>(_jsonOptions) ?? new OcrResult();
    }

    // Subscription & Usage
    public async Task<UsageStats> GetUsageStatsAsync()
    {
        return await _httpClient.GetFromJsonAsync<UsageStats>("/api/usage/stats", _jsonOptions) ?? new UsageStats();
    }

    public async Task<SubscriptionInfo> GetSubscriptionInfoAsync()
    {
        return await _httpClient.GetFromJsonAsync<SubscriptionInfo>("/api/subscription/info", _jsonOptions) ?? new SubscriptionInfo();
    }

    public async Task<bool> UpgradeSubscriptionAsync(string tierName)
    {
        var response = await _httpClient.PostAsJsonAsync("/api/subscription/upgrade", new { tier = tierName });
        return response.IsSuccessStatusCode;
    }
}
