using Evident.MatterDocket.MAUI.Models;

namespace Evident.MatterDocket.MAUI.Services;

public interface IAnalysisService
{
    Task<ApiResponse<StartAnalysisResponse>> StartAnalysisAsync(int fileId, string analysisType = "full");
    Task<AnalysisResponse?> GetAnalysisAsync(string analysisId);
    Task<AnalysisStatusResponse?> GetAnalysisStatusAsync(string analysisId);
    Task<AnalysisListResponse?> ListAnalysesAsync(int page = 1, int limit = 20);
}

public class AnalysisService : IAnalysisService
{
    private readonly ApiService _apiService;

    public AnalysisService(ApiService apiService)
    {
        _apiService = apiService;
    }

    public async Task<ApiResponse<StartAnalysisResponse>> StartAnalysisAsync(int fileId, string analysisType = "full")
    {
        try
        {
            var request = new StartAnalysisRequest
            {
                FileId = fileId,
                AnalysisType = analysisType
            };

            var response = await _apiService.PostAsync<StartAnalysisResponse>("/analysis/start", request);
            return response;
        }
        catch
        {
            return new ApiResponse<StartAnalysisResponse> { Success = false, Error = "Failed to start analysis" };
        }
    }

    public async Task<AnalysisResponse?> GetAnalysisAsync(string analysisId)
    {
        try
        {
            var response = await _apiService.GetAsync<AnalysisResponse>($"/analysis/{analysisId}");
            return response.Success ? response.Data : null;
        }
        catch
        {
            return null;
        }
    }

    public async Task<AnalysisStatusResponse?> GetAnalysisStatusAsync(string analysisId)
    {
        try
        {
            var response = await _apiService.GetAsync<AnalysisStatusResponse>($"/analysis/{analysisId}/status");
            return response.Success ? response.Data : null;
        }
        catch
        {
            return null;
        }
    }

    public async Task<AnalysisListResponse?> ListAnalysesAsync(int page = 1, int limit = 20)
    {
        try
        {
            var response = await _apiService.GetAsync<AnalysisListResponse>($"/analysis/list?page={page}&limit={limit}");
            return response.Success ? response.Data : null;
        }
        catch
        {
            return null;
        }
    }
}
