namespace Evident.Shared.Models;

/// <summary>
/// Shared data model for BWC analysis requests across all platforms
/// </summary>
public class AnalysisRequest
{
    public string? FileName { get; set; }
    public string? CaseNumber { get; set; }
    public string? OfficerName { get; set; }
    public DateTime? IncidentDate { get; set; }
    public string? Location { get; set; }
    public string? Description { get; set; }
    public AnalysisOptions? Options { get; set; }
}

public class AnalysisOptions
{
    public bool EnableTranscription { get; set; } = true;
    public bool EnableViolationScanning { get; set; } = true;
    public bool EnableComplianceCheck { get; set; } = true;
    public bool EnableEntityExtraction { get; set; } = true;
    public string TranscriptionLanguage { get; set; } = "en";
}

public class AnalysisResponse
{
    public string? AnalysisId { get; set; }
    public string Status { get; set; } = "pending";
    public int Progress { get; set; }
    public string? CurrentStep { get; set; }
    public DateTime CreatedAt { get; set; }
    public DateTime? CompletedAt { get; set; }
    public AnalysisResults? Results { get; set; }
    public string? ErrorMessage { get; set; }
}

public class AnalysisResults
{
    public TranscriptResult? Transcript { get; set; }
    public List<Violation>? Violations { get; set; }
    public ComplianceReport? Compliance { get; set; }
    public List<Entity>? Entities { get; set; }
    public TimelineData? Timeline { get; set; }
    public int TotalSpeakers { get; set; }
    public int TotalSegments { get; set; }
    public double DurationSeconds { get; set; }
}

public class TranscriptResult
{
    public string? Text { get; set; }
    public List<TranscriptSegment>? Segments { get; set; }
    public List<Speaker>? Speakers { get; set; }
}

public class TranscriptSegment
{
    public int Id { get; set; }
    public double StartTime { get; set; }
    public double EndTime { get; set; }
    public string? Text { get; set; }
    public string? Speaker { get; set; }
    public double Confidence { get; set; }
}

public class Speaker
{
    public string? Id { get; set; }
    public string? Name { get; set; }
    public int SegmentCount { get; set; }
}

public class Violation
{
    public string? Type { get; set; }
    public string? Severity { get; set; }
    public string? Description { get; set; }
    public double Timestamp { get; set; }
    public string? Context { get; set; }
    public List<string>? LegalReferences { get; set; }
}

public class ComplianceReport
{
    public bool IsCompliant { get; set; }
    public List<ComplianceIssue>? Issues { get; set; }
    public double ComplianceScore { get; set; }
}

public class ComplianceIssue
{
    public string? Rule { get; set; }
    public string? Description { get; set; }
    public string? Severity { get; set; }
    public string? Recommendation { get; set; }
}

public class Entity
{
    public string? Type { get; set; }
    public string? Value { get; set; }
    public double Confidence { get; set; }
    public List<int>? SegmentIds { get; set; }
}

public class TimelineData
{
    public List<TimelineEvent>? Events { get; set; }
}

public class TimelineEvent
{
    public double Timestamp { get; set; }
    public string? Type { get; set; }
    public string? Description { get; set; }
    public string? Severity { get; set; }
}
