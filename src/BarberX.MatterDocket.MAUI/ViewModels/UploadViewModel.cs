using System.Collections.ObjectModel;
using CommunityToolkit.Mvvm.ComponentModel;
using CommunityToolkit.Mvvm.Input;
using Evident.MatterDocket.MAUI.Services;
using Evident.MatterDocket.MAUI.Models;

namespace Evident.MatterDocket.MAUI.ViewModels;

public partial class UploadViewModel : BaseViewModel
{
    private readonly IUploadService _uploadService;
    private readonly IAnalysisService _analysisService;
    private readonly ITierService _tierService;

    [ObservableProperty]
    private string _selectedFilePath;

    [ObservableProperty]
    private string _selectedFileName;

    [ObservableProperty]
    private long _selectedFileSize;

    [ObservableProperty]
    private string _fileType = "PDF"; // PDF or Video

    [ObservableProperty]
    private double _uploadProgress;

    [ObservableProperty]
    private bool _isUploading;

    [ObservableProperty]
    private bool _uploadComplete;

    [ObservableProperty]
    private string _uploadedFileId;

    [ObservableProperty]
    private bool _runAnalysisAfterUpload = true;

    [ObservableProperty]
    private string _analysisType = "timeline"; // timeline, transcription, ocr

    [ObservableProperty]
    private ObservableCollection<string> _analysisTypes = new()
    {
        "timeline",
        "transcription",
        "ocr",
        "full_analysis"
    };

    public UploadViewModel(
        IUploadService uploadService,
        IAnalysisService analysisService,
        ITierService tierService)
    {
        _uploadService = uploadService;
        _analysisService = analysisService;
        _tierService = tierService;
        Title = "Upload Evidence";
    }

    /// <summary>
    /// Select a file to upload
    /// </summary>
    [RelayCommand]
    private async Task SelectFileAsync()
    {
        try
        {
            var customFileType = FileType == "PDF" 
                ? new FilePickerFileType(new Dictionary<DevicePlatform, IEnumerable<string>>
                {
                    { DevicePlatform.iOS, new[] { "com.adobe.pdf" } },
                    { DevicePlatform.Android, new[] { "application/pdf" } },
                    { DevicePlatform.WinUI, new[] { ".pdf" } },
                    { DevicePlatform.MacCatalyst, new[] { "pdf" } }
                })
                : new FilePickerFileType(new Dictionary<DevicePlatform, IEnumerable<string>>
                {
                    { DevicePlatform.iOS, new[] { "public.movie" } },
                    { DevicePlatform.Android, new[] { "video/mp4", "video/mpeg" } },
                    { DevicePlatform.WinUI, new[] { ".mp4", ".mpeg", ".avi", ".mov" } },
                    { DevicePlatform.MacCatalyst, new[] { "mp4", "mov" } }
                });

            var options = new PickOptions
            {
                FileTypes = customFileType,
                PickerTitle = $"Select {FileType} File"
            };

            var result = await FilePicker.Default.PickAsync(options);
            if (result != null)
            {
                SelectedFilePath = result.FullPath;
                SelectedFileName = result.FileName;

                // Get file size
                var fileInfo = new FileInfo(result.FullPath);
                SelectedFileSize = fileInfo.Length;

                // Check tier limits
                var canUpload = FileType == "PDF"
                    ? await _tierService.CanUploadPdfAsync(SelectedFileSize)
                    : await _tierService.CanUploadVideoAsync(SelectedFileSize);

                if (!canUpload)
                {
                    var feature = FileType == "PDF" ? "large_pdf" : "large_video";
                    ErrorMessage = _tierService.GetUpgradeMessage(feature);
                    SelectedFilePath = null;
                    SelectedFileName = null;
                    SelectedFileSize = 0;
                }
            }
        }
        catch (Exception ex)
        {
            SetError($"Failed to select file: {ex.Message}");
        }
    }

    /// <summary>
    /// Upload the selected file
    /// </summary>
    [RelayCommand]
    private async Task UploadFileAsync()
    {
        if (string.IsNullOrEmpty(SelectedFilePath))
        {
            SetError("Please select a file first.");
            return;
        }

        await ExecuteAsync(async () =>
        {
            IsUploading = true;
            UploadProgress = 0;

            var progress = new Progress<double>(percent =>
            {
                UploadProgress = percent;
            });

            ApiResponse<UploadResponse> result;

            if (FileType == "PDF")
            {
                result = await _uploadService.UploadPdfAsync(SelectedFilePath, progress);
            }
            else
            {
                result = await _uploadService.UploadVideoAsync(SelectedFilePath, progress);
            }

            if (result.Success)
            {
                UploadedFileId = result.Data.FileId.ToString();
                UploadComplete = true;

                // Automatically start analysis if requested
                if (RunAnalysisAfterUpload)
                {
                    await StartAnalysisAsync();
                }
            }
            else
            {
                SetError(result.Error);
            }

            IsUploading = false;

        }, "Upload failed");
    }

    /// <summary>
    /// Start AI analysis on uploaded file
    /// </summary>
    [RelayCommand]
    private async Task StartAnalysisAsync()
    {
        if (string.IsNullOrEmpty(UploadedFileId))
        {
            SetError("No file uploaded yet.");
            return;
        }

        // Check if user can use AI
        if (!await _tierService.CanUseAiAnalysisAsync())
        {
            SetError(_tierService.GetUpgradeMessage("ai_analysis"));
            return;
        }

        await ExecuteAsync(async () =>
        {
            var result = await _analysisService.StartAnalysisAsync(
                int.Parse(UploadedFileId),
                AnalysisType
            );

            if (result.Success)
            {
                // Navigate to analysis view
                await Shell.Current.GoToAsync($"//Analysis?analysisId={result.Data.AnalysisId}");
            }
            else
            {
                SetError(result.Error);
            }

        }, "Failed to start analysis");
    }

    /// <summary>
    /// Reset upload form
    /// </summary>
    [RelayCommand]
    private void ResetUpload()
    {
        SelectedFilePath = null;
        SelectedFileName = null;
        SelectedFileSize = 0;
        UploadProgress = 0;
        UploadComplete = false;
        UploadedFileId = null;
        IsUploading = false;
        ClearError();
    }

    /// <summary>
    /// Select PDF file type
    /// </summary>
    [RelayCommand]
    private void SelectPdfType()
    {
        FileType = "PDF";
        ResetUpload();
    }

    /// <summary>
    /// Select Video file type
    /// </summary>
    [RelayCommand]
    private void SelectVideoType()
    {
        FileType = "Video";
        ResetUpload();
    }

    /// <summary>
    /// Get formatted file size
    /// </summary>
    public string FormattedFileSize
    {
        get
        {
            if (SelectedFileSize == 0) return "0 B";

            string[] sizes = { "B", "KB", "MB", "GB" };
            int order = 0;
            double size = SelectedFileSize;

            while (size >= 1024 && order < sizes.Length - 1)
            {
                order++;
                size /= 1024;
            }

            return $"{size:0.##} {sizes[order]}";
        }
    }
}
