using Evident.MatterDocket.MAUI.Models;
using System.Collections.Generic;
using System.Threading.Tasks;

namespace Evident.MatterDocket.MAUI.Services
{
    public interface IEvidenceService
    {
        Task<ApiResponse<List<EvidenceItem>>> GetEvidenceListAsync(int caseId);
        Task<ApiResponse<EvidenceDetails>> GetEvidenceAsync(int evidenceId);
        Task<ApiResponse<TranscriptionResult>> TranscribeVideoAsync(int evidenceId);
        Task<ApiResponse<OcrResult>> ExtractTextFromPdfAsync(int evidenceId);
        Task<ApiResponse<bool>> DeleteEvidenceAsync(int evidenceId);
    }

    public class EvidenceService : IEvidenceService
    {
        private readonly IApiService _apiService;

        public EvidenceService(IApiService apiService)
        {
            _apiService = apiService;
        }

        /// <summary>
        /// Get list of evidence items for a specific case
        /// </summary>
        public async Task<ApiResponse<List<EvidenceItem>>> GetEvidenceListAsync(int caseId)
        {
            try
            {
                return await _apiService.GetAsync<List<EvidenceItem>>($"/evidence/list?case_id={caseId}");
            }
            catch (Exception ex)
            {
                return new ApiResponse<List<EvidenceItem>>
                {
                    Success = false,
                    Error = $"Failed to get evidence list: {ex.Message}"
                };
            }
        }

        /// <summary>
        /// Get detailed information about a specific evidence item
        /// </summary>
        public async Task<ApiResponse<EvidenceDetails>> GetEvidenceAsync(int evidenceId)
        {
            try
            {
                return await _apiService.GetAsync<EvidenceDetails>($"/evidence/{evidenceId}");
            }
            catch (Exception ex)
            {
                return new ApiResponse<EvidenceDetails>
                {
                    Success = false,
                    Error = $"Failed to get evidence details: {ex.Message}"
                };
            }
        }

        /// <summary>
        /// Transcribe video evidence using AI (Whisper)
        /// </summary>
        public async Task<ApiResponse<TranscriptionResult>> TranscribeVideoAsync(int evidenceId)
        {
            try
            {
                var payload = new { evidence_id = evidenceId };
                return await _apiService.PostAsync<TranscriptionResult>("/evidence/transcribe", payload);
            }
            catch (Exception ex)
            {
                return new ApiResponse<TranscriptionResult>
                {
                    Success = false,
                    Error = $"Failed to transcribe video: {ex.Message}"
                };
            }
        }

        /// <summary>
        /// Extract text from PDF evidence using OCR
        /// </summary>
        public async Task<ApiResponse<OcrResult>> ExtractTextFromPdfAsync(int evidenceId)
        {
            try
            {
                var payload = new { evidence_id = evidenceId };
                return await _apiService.PostAsync<OcrResult>("/evidence/ocr", payload);
            }
            catch (Exception ex)
            {
                return new ApiResponse<OcrResult>
                {
                    Success = false,
                    Error = $"Failed to extract text: {ex.Message}"
                };
            }
        }

        /// <summary>
        /// Delete an evidence item
        /// </summary>
        public async Task<ApiResponse<bool>> DeleteEvidenceAsync(int evidenceId)
        {
            try
            {
                var response = await _apiService.DeleteAsync($"/evidence/{evidenceId}");
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
                    Error = $"Failed to delete evidence: {ex.Message}"
                };
            }
        }
    }
}
