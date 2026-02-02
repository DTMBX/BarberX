namespace Evident.Web.Services;

using Evident.Shared.Models;

/// <summary>
/// Service interface for BWC analysis operations
/// </summary>
public interface IAnalysisService
{
    Task<AnalysisResponse> UploadAndAnalyzeAsync(string userId, Stream videoStream, AnalysisRequest request);
    Task<AnalysisResponse?> GetAnalysisStatusAsync(string userId, string analysisId);
    Task<AnalysisResponse?> GetAnalysisResultsAsync(string userId, string analysisId);
    Task<List<AnalysisResponse>> GetUserAnalysesAsync(string userId);
    Task<bool> DeleteAnalysisAsync(string userId, string analysisId);
    Task<(Stream? stream, string contentType, string fileName)> GetReportAsync(string userId, string analysisId, string format);
}
