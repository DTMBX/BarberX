using Evident.MatterDocket.MAUI.Models;
using System.Collections.Generic;
using System.Threading.Tasks;

namespace Evident.MatterDocket.MAUI.Services
{
    public interface ICaseService
    {
        Task<ApiResponse<List<CaseListItem>>> GetCasesAsync(int page = 1, int perPage = 20);
        Task<ApiResponse<CaseDetails>> GetCaseAsync(int caseId);
        Task<ApiResponse<CaseDetails>> CreateCaseAsync(CreateCaseRequest request);
        Task<ApiResponse<CaseDetails>> UpdateCaseAsync(int caseId, UpdateCaseRequest request);
        Task<ApiResponse<bool>> DeleteCaseAsync(int caseId);
        Task<ApiResponse<List<CaseListItem>>> SearchCasesAsync(string query);
    }

    public class CaseService : ICaseService
    {
        private readonly IApiService _apiService;

        public CaseService(IApiService apiService)
        {
            _apiService = apiService;
        }

        /// <summary>
        /// Get a paginated list of cases
        /// </summary>
        public async Task<ApiResponse<List<CaseListItem>>> GetCasesAsync(int page = 1, int perPage = 20)
        {
            try
            {
                return await _apiService.GetAsync<List<CaseListItem>>($"/cases?page={page}&per_page={perPage}");
            }
            catch (Exception ex)
            {
                return new ApiResponse<List<CaseListItem>>
                {
                    Success = false,
                    Error = $"Failed to get cases: {ex.Message}"
                };
            }
        }

        /// <summary>
        /// Get detailed information about a specific case
        /// </summary>
        public async Task<ApiResponse<CaseDetails>> GetCaseAsync(int caseId)
        {
            try
            {
                return await _apiService.GetAsync<CaseDetails>($"/cases/{caseId}");
            }
            catch (Exception ex)
            {
                return new ApiResponse<CaseDetails>
                {
                    Success = false,
                    Error = $"Failed to get case details: {ex.Message}"
                };
            }
        }

        /// <summary>
        /// Create a new case
        /// </summary>
        public async Task<ApiResponse<CaseDetails>> CreateCaseAsync(CreateCaseRequest request)
        {
            try
            {
                return await _apiService.PostAsync<CaseDetails>("/cases", request);
            }
            catch (Exception ex)
            {
                return new ApiResponse<CaseDetails>
                {
                    Success = false,
                    Error = $"Failed to create case: {ex.Message}"
                };
            }
        }

        /// <summary>
        /// Update an existing case
        /// </summary>
        public async Task<ApiResponse<CaseDetails>> UpdateCaseAsync(int caseId, UpdateCaseRequest request)
        {
            try
            {
                return await _apiService.PutAsync<CaseDetails>($"/cases/{caseId}", request);
            }
            catch (Exception ex)
            {
                return new ApiResponse<CaseDetails>
                {
                    Success = false,
                    Error = $"Failed to update case: {ex.Message}"
                };
            }
        }

        /// <summary>
        /// Delete a case
        /// </summary>
        public async Task<ApiResponse<bool>> DeleteCaseAsync(int caseId)
        {
            try
            {
                var response = await _apiService.DeleteAsync($"/cases/{caseId}");
                return new ApiResponse<bool>
                {
                    Success = response.Success,
                    Data = response.Success,
                    Error = response.Error
                };
            }
            catch (Exception ex)
            {
                return new ApiResponse<bool>
                {
                    Success = false,
                    Data = false,
                    Error = $"Failed to delete case: {ex.Message}"
                };
            }
        }

        /// <summary>
        /// Search cases by query string
        /// </summary>
        public async Task<ApiResponse<List<CaseListItem>>> SearchCasesAsync(string query)
        {
            try
            {
                var encodedQuery = System.Net.WebUtility.UrlEncode(query);
                return await _apiService.GetAsync<List<CaseListItem>>($"/cases/search?q={encodedQuery}");
            }
            catch (Exception ex)
            {
                return new ApiResponse<List<CaseListItem>>
                {
                    Success = false,
                    Error = $"Failed to search cases: {ex.Message}"
                };
            }
        }
    }

    /// <summary>
    /// Request model for creating a new case
    /// </summary>
    public class CreateCaseRequest
    {
        public string CaseNumber { get; set; }
        public string Title { get; set; }
        public string Description { get; set; }
        public string ClientName { get; set; }
        public DateTime? IncidentDate { get; set; }
        public string Status { get; set; } = "Open";
    }

    /// <summary>
    /// Request model for updating a case
    /// </summary>
    public class UpdateCaseRequest
    {
        public string Title { get; set; }
        public string Description { get; set; }
        public string ClientName { get; set; }
        public DateTime? IncidentDate { get; set; }
        public string Status { get; set; }
    }

    /// <summary>
    /// List item model for cases (summary view)
    /// </summary>
    public class CaseListItem
    {
        public int Id { get; set; }
        public string CaseNumber { get; set; }
        public string Title { get; set; }
        public string ClientName { get; set; }
        public string Status { get; set; }
        public DateTime CreatedAt { get; set; }
        public DateTime? LastModified { get; set; }
        public int EvidenceCount { get; set; }
    }

    /// <summary>
    /// Detailed case model
    /// </summary>
    public class CaseDetails
    {
        public int Id { get; set; }
        public string CaseNumber { get; set; }
        public string Title { get; set; }
        public string Description { get; set; }
        public string ClientName { get; set; }
        public DateTime? IncidentDate { get; set; }
        public string Status { get; set; }
        public DateTime CreatedAt { get; set; }
        public DateTime? LastModified { get; set; }
        public List<EvidenceItem> Evidence { get; set; }
        public List<AnalysisListItem> Analyses { get; set; }
    }
}
