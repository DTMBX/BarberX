namespace Evident.Shared.Models;

public class Case
{
    public string Id { get; set; } = string.Empty;
    public string CaseNumber { get; set; } = string.Empty;
    public string Title { get; set; } = string.Empty;
    public string Description { get; set; } = string.Empty;
    public string Status { get; set; } = string.Empty;
    public DateTime CreatedAt { get; set; }
    public DateTime UpdatedAt { get; set; }
    public string ClientName { get; set; } = string.Empty;
    public List<string> Tags { get; set; } = new();
    public int DocumentCount { get; set; }
    public int VideoCount { get; set; }
    public string ThumbnailUrl { get; set; } = string.Empty;
}

public class CaseDetail : Case
{
    public List<Document> Documents { get; set; } = new();
    public List<VideoAnalysis> Videos { get; set; } = new();
    public List<Timeline> TimelineEvents { get; set; } = new();
    public Dictionary<string, string> Metadata { get; set; } = new();
}

public class Document
{
    public string Id { get; set; } = string.Empty;
    public string FileName { get; set; } = string.Empty;
    public string FileType { get; set; } = string.Empty;
    public long FileSize { get; set; }
    public DateTime UploadedAt { get; set; }
    public string Url { get; set; } = string.Empty;
    public bool IsEncrypted { get; set; }
}

public class VideoAnalysis
{
    public string Id { get; set; } = string.Empty;
    public string VideoUrl { get; set; } = string.Empty;
    public string ThumbnailUrl { get; set; } = string.Empty;
    public TimeSpan Duration { get; set; }
    public string TranscriptUrl { get; set; } = string.Empty;
    public DateTime AnalyzedAt { get; set; }
    public List<string> KeyFindings { get; set; } = new();
    public Dictionary<string, object> Metadata { get; set; } = new();
}

public class Timeline
{
    public DateTime Timestamp { get; set; }
    public string Event { get; set; } = string.Empty;
    public string Description { get; set; } = string.Empty;
    public string Source { get; set; } = string.Empty;
}
