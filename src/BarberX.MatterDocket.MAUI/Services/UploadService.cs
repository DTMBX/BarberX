using Evident.MatterDocket.MAUI.Models;

namespace Evident.MatterDocket.MAUI.Services;

public interface IUploadService
{
    Task<ApiResponse<UploadResponse>> UploadPdfAsync(string filePath, IProgress<double>? progress = null);
    Task<ApiResponse<UploadResponse>> UploadVideoAsync(string filePath, IProgress<double>? progress = null);
    Task<UploadStatusResponse?> GetUploadStatusAsync(int fileId);
}

public class UploadService : IUploadService
{
    private readonly ApiService _apiService;

    public UploadService(ApiService apiService)
    {
        _apiService = apiService;
    }

    public async Task<ApiResponse<UploadResponse>> UploadPdfAsync(string filePath, IProgress<double>? progress = null)
    {
        try
        {
            if (!File.Exists(filePath))
            {
                return new ApiResponse<UploadResponse>
                {
                    Success = false,
                    Error = "File not found"
                };
            }

            var fileInfo = new FileInfo(filePath);
            var fileName = fileInfo.Name;

            using var fileStream = File.OpenRead(filePath);
            using var content = new MultipartFormDataContent();
            using var streamContent = new StreamContent(fileStream);

            streamContent.Headers.ContentType = new System.Net.Http.Headers.MediaTypeHeaderValue("application/pdf");
            content.Add(streamContent, "file", fileName);

            var response = await _apiService.PostMultipartAsync<UploadResponse>("/upload/pdf", content, progress);

            if (response.Success)
            {
                return response;
            }
            else
            {
                return new ApiResponse<UploadResponse> 
                {
                    Success = false,
                    Error = response.Error ?? "Upload failed"
                };
            }
        }
        catch (Exception ex)
        {
            return new ApiResponse<UploadResponse>
            {
                Success = false,
                Error = $"Upload error: {ex.Message}"
            };
        }
    }

    public async Task<ApiResponse<UploadResponse>> UploadVideoAsync(string filePath, IProgress<double>? progress = null)
    {
        try
        {
            if (!File.Exists(filePath))
            {
                return new ApiResponse<UploadResponse>
                {
                    Success = false,
                    Error = "File not found"
                };
            }

            var fileInfo = new FileInfo(filePath);
            var fileName = fileInfo.Name;
            var extension = fileInfo.Extension.ToLower();

            // Determine content type
            var contentType = extension switch
            {
                ".mp4" => "video/mp4",
                ".mov" => "video/quicktime",
                ".avi" => "video/x-msvideo",
                ".mkv" => "video/x-matroska",
                ".webm" => "video/webm",
                _ => "application/octet-stream"
            };

            using var fileStream = File.OpenRead(filePath);
            using var content = new MultipartFormDataContent();
            using var streamContent = new StreamContent(fileStream);

            streamContent.Headers.ContentType = new System.Net.Http.Headers.MediaTypeHeaderValue(contentType);
            content.Add(streamContent, "file", fileName);

            var response = await _apiService.PostMultipartAsync<UploadResponse>("/upload/video", content, progress);

            if (response.Success)
            {
                return response;
            }
            else
            {
                return new ApiResponse<UploadResponse>
                {
                    Success = false,
                    Error = response.Error ?? "Upload failed"
                };
            }
        }
        catch (Exception ex)
        {
            return new ApiResponse<UploadResponse>
            {
                Success = false,
                Error = $"Upload error: {ex.Message}"
            };
        }
    }

    public async Task<UploadStatusResponse?> GetUploadStatusAsync(int fileId)
    {
        try
        {
            var response = await _apiService.GetAsync<UploadStatusResponse>($"/upload/status/{fileId}");
            return response.Success ? response.Data : null;
        }
        catch
        {
            return null;
        }
    }
}

public class UploadResult
{
    public bool Success { get; set; }
    public int FileId { get; set; }
    public string? Filename { get; set; }
    public long Size { get; set; }
    public string? Status { get; set; }
    public string? ErrorMessage { get; set; }
}
