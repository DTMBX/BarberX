namespace Evident.Web.Services;

using System.Net.Http.Headers;
using System.Text.Json;
using Evident.Shared.Models;

/// <summary>
/// Analysis service that proxies requests to Flask backend
/// This allows ASP.NET Core to serve as API gateway while Flask handles AI processing
/// </summary>
public class FlaskProxyAnalysisService : IAnalysisService
{
    private readonly HttpClient _httpClient;
    private readonly ILogger<FlaskProxyAnalysisService> _logger;
    private readonly JsonSerializerOptions _jsonOptions;

    public FlaskProxyAnalysisService(HttpClient httpClient, ILogger<FlaskProxyAnalysisService> logger)
    {
        _httpClient = httpClient;
        _logger = logger;
        _jsonOptions = new JsonSerializerOptions
        {
            PropertyNameCaseInsensitive = true,
            PropertyNamingPolicy = JsonNamingPolicy.CamelCase
        };
    }

    public async Task<AnalysisResponse> UploadAndAnalyzeAsync(string userId, Stream videoStream, AnalysisRequest request)
    {
        using var content = new MultipartFormDataContent();
        
        var streamContent = new StreamContent(videoStream);
        streamContent.Headers.ContentType = new MediaTypeHeaderValue("video/mp4");
        content.Add(streamContent, "file", request.FileName ?? "video.mp4");
        
        content.Add(new StringContent(userId), "user_id");
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
        
        var json = await response.Content.ReadAsStringAsync();
        return JsonSerializer.Deserialize<AnalysisResponse>(json, _jsonOptions) ?? new AnalysisResponse();
    }

    public async Task<AnalysisResponse?> GetAnalysisStatusAsync(string userId, string analysisId)
    {
        try
        {
            var response = await _httpClient.GetAsync($"/api/analysis/{analysisId}/status");
            
            if (response.StatusCode == System.Net.HttpStatusCode.NotFound)
                return null;
            
            response.EnsureSuccessStatusCode();
            
            var json = await response.Content.ReadAsStringAsync();
            return JsonSerializer.Deserialize<AnalysisResponse>(json, _jsonOptions);
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error getting analysis status from Flask backend");
            throw;
        }
    }

    public async Task<AnalysisResponse?> GetAnalysisResultsAsync(string userId, string analysisId)
    {
        try
        {
            var response = await _httpClient.GetAsync($"/api/analysis/{analysisId}");
            
            if (response.StatusCode == System.Net.HttpStatusCode.NotFound)
                return null;
            
            response.EnsureSuccessStatusCode();
            
            var json = await response.Content.ReadAsStringAsync();
            return JsonSerializer.Deserialize<AnalysisResponse>(json, _jsonOptions);
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error getting analysis results from Flask backend");
            throw;
        }
    }

    public async Task<List<AnalysisResponse>> GetUserAnalysesAsync(string userId)
    {
        try
        {
            var response = await _httpClient.GetAsync($"/api/analyses?user_id={userId}");
            response.EnsureSuccessStatusCode();
            
            var json = await response.Content.ReadAsStringAsync();
            return JsonSerializer.Deserialize<List<AnalysisResponse>>(json, _jsonOptions) ?? new List<AnalysisResponse>();
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error getting user analyses from Flask backend");
            throw;
        }
    }

    public async Task<bool> DeleteAnalysisAsync(string userId, string analysisId)
    {
        try
        {
            var response = await _httpClient.DeleteAsync($"/api/analysis/{analysisId}");
            return response.IsSuccessStatusCode;
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error deleting analysis from Flask backend");
            return false;
        }
    }

    public async Task<(Stream? stream, string contentType, string fileName)> GetReportAsync(string userId, string analysisId, string format)
    {
        try
        {
            var response = await _httpClient.GetAsync($"/api/analysis/{analysisId}/report/{format}");
            
            if (!response.IsSuccessStatusCode)
                return (null, "", "");
            
            var stream = await response.Content.ReadAsStreamAsync();
            var contentType = response.Content.Headers.ContentType?.MediaType ?? "application/octet-stream";
            var fileName = $"BWC_Analysis_{analysisId}.{format}";
            
            return (stream, contentType, fileName);
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error downloading report from Flask backend");
            return (null, "", "");
        }
    }
}
