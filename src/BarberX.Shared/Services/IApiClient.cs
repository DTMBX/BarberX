namespace Evident.Shared.Services;

using Evident.Shared.Models;

/// <summary>
/// Shared API client interface for all platforms
/// </summary>
public interface IApiClient
{
    // Authentication
    Task<AuthResponse> LoginAsync(string email, string password);
    Task<AuthResponse> RegisterAsync(string email, string password, string fullName);
    Task LogoutAsync();
    Task<UserProfile> GetProfileAsync();
    
    // BWC Analysis
    Task<AnalysisResponse> UploadVideoAsync(Stream videoStream, AnalysisRequest request, IProgress<double>? progress = null);
    Task<AnalysisResponse> GetAnalysisStatusAsync(string analysisId);
    Task<AnalysisResponse> GetAnalysisResultsAsync(string analysisId);
    Task<List<AnalysisResponse>> GetUserAnalysesAsync();
    Task<bool> DeleteAnalysisAsync(string analysisId);
    
    // PDF Processing
    Task<PdfUploadResponse> UploadPdfAsync(Stream pdfStream, string fileName, IProgress<double>? progress = null);
    Task<List<PdfDocument>> GetUserPdfsAsync();
    Task<PdfAnalysisResult> AnalyzePdfAsync(string pdfId);
    Task<bool> DeletePdfAsync(string pdfId);
    
    // Legal Analysis
    Task<ViolationScanResult> ScanViolationsAsync(string transcript, Dictionary<string, object>? context = null);
    Task<ComplianceCheckResult> CheckComplianceAsync(Dictionary<string, object> evidence);
    Task<CombinedLegalAnalysis> RunCombinedAnalysisAsync(string transcript, Dictionary<string, object> evidence);
    
    // Transcription & OCR
    Task<TranscriptionResult> TranscribeAudioAsync(Stream audioStream, string language = "en");
    Task<OcrResult> ExtractTextAsync(Stream imageStream, string language = "eng");
    
    // Subscription & Usage
    Task<UsageStats> GetUsageStatsAsync();
    Task<SubscriptionInfo> GetSubscriptionInfoAsync();
    Task<bool> UpgradeSubscriptionAsync(string tierName);
}

public class AuthResponse
{
    public bool Success { get; set; }
    public string? Token { get; set; }
    public string? UserId { get; set; }
    public string? Email { get; set; }
    public string? ErrorMessage { get; set; }
}

public class UserProfile
{
    public string? Id { get; set; }
    public string? Email { get; set; }
    public string? FullName { get; set; }
    public string? Organization { get; set; }
    public string Tier { get; set; } = "FREE";
    public DateTime CreatedAt { get; set; }
}

public class PdfUploadResponse
{
    public string? PdfId { get; set; }
    public string? FileName { get; set; }
    public long FileSize { get; set; }
    public DateTime UploadedAt { get; set; }
}

public class PdfDocument
{
    public string? Id { get; set; }
    public string? FileName { get; set; }
    public long FileSize { get; set; }
    public int PageCount { get; set; }
    public DateTime UploadedAt { get; set; }
    public bool IsAnalyzed { get; set; }
}

public class PdfAnalysisResult
{
    public string? PdfId { get; set; }
    public string? ExtractedText { get; set; }
    public List<Entity>? Entities { get; set; }
    public Dictionary<string, object>? Metadata { get; set; }
}

public class ViolationScanResult
{
    public List<Violation>? Violations { get; set; }
    public int TotalViolations { get; set; }
    public int CriticalViolations { get; set; }
    public Dictionary<string, int>? ViolationsByType { get; set; }
}

public class ComplianceCheckResult
{
    public bool IsCompliant { get; set; }
    public double ComplianceScore { get; set; }
    public List<ComplianceIssue>? Issues { get; set; }
    public List<string>? Recommendations { get; set; }
}

public class CombinedLegalAnalysis
{
    public ViolationScanResult? ViolationScan { get; set; }
    public ComplianceCheckResult? ComplianceCheck { get; set; }
    public string? Summary { get; set; }
    public List<string>? ActionItems { get; set; }
}

public class TranscriptionResult
{
    public string? Text { get; set; }
    public List<TranscriptSegment>? Segments { get; set; }
    public double DurationSeconds { get; set; }
    public string Language { get; set; } = "en";
}

public class OcrResult
{
    public string? Text { get; set; }
    public double Confidence { get; set; }
    public string Language { get; set; } = "eng";
}

public class UsageStats
{
    public int BwcVideosProcessed { get; set; }
    public int PdfDocumentsProcessed { get; set; }
    public int TranscriptionMinutesUsed { get; set; }
    public int LegalAnalysesRun { get; set; }
    public double StorageUsedMb { get; set; }
    public Dictionary<string, int>? MonthlyLimits { get; set; }
}

public class SubscriptionInfo
{
    public string Tier { get; set; } = "FREE";
    public DateTime? SubscriptionStart { get; set; }
    public DateTime? SubscriptionEnd { get; set; }
    public bool IsActive { get; set; }
    public Dictionary<string, object>? Features { get; set; }
}
