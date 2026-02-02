namespace Evident.Web.Controllers;

using Microsoft.AspNetCore.Mvc;
using Microsoft.AspNetCore.Authorization;
using Evident.Shared.Models;
using Evident.Web.Services;

[ApiController]
[Route("api/[controller]")]
[Authorize]
public class AnalysisController : ControllerBase
{
    private readonly IAnalysisService _analysisService;
    private readonly ILogger<AnalysisController> _logger;

    public AnalysisController(IAnalysisService analysisService, ILogger<AnalysisController> logger)
    {
        _analysisService = analysisService;
        _logger = logger;
    }

    /// <summary>
    /// Upload BWC video for analysis
    /// </summary>
    [HttpPost("upload")]
    [RequestSizeLimit(500_000_000)] // 500MB limit
    public async Task<ActionResult<AnalysisResponse>> UploadVideo(
        IFormFile file,
        [FromForm] string? caseNumber = null,
        [FromForm] string? officerName = null,
        [FromForm] DateTime? incidentDate = null,
        [FromForm] string? location = null,
        [FromForm] string? description = null)
    {
        try
        {
            if (file == null || file.Length == 0)
                return BadRequest(new { error = "No file provided" });

            var userId = User.FindFirst("user_id")?.Value;
            if (string.IsNullOrEmpty(userId))
                return Unauthorized();

            var request = new AnalysisRequest
            {
                FileName = file.FileName,
                CaseNumber = caseNumber,
                OfficerName = officerName,
                IncidentDate = incidentDate,
                Location = location,
                Description = description
            };

            using var stream = file.OpenReadStream();
            var response = await _analysisService.UploadAndAnalyzeAsync(userId, stream, request);

            return Ok(response);
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error uploading video");
            return StatusCode(500, new { error = "Upload failed", message = ex.Message });
        }
    }

    /// <summary>
    /// Get analysis status
    /// </summary>
    [HttpGet("{analysisId}/status")]
    public async Task<ActionResult<AnalysisResponse>> GetStatus(string analysisId)
    {
        try
        {
            var userId = User.FindFirst("user_id")?.Value;
            if (string.IsNullOrEmpty(userId))
                return Unauthorized();

            var response = await _analysisService.GetAnalysisStatusAsync(userId, analysisId);
            
            if (response == null)
                return NotFound(new { error = "Analysis not found" });

            return Ok(response);
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error getting analysis status");
            return StatusCode(500, new { error = "Failed to get status" });
        }
    }

    /// <summary>
    /// Get analysis results
    /// </summary>
    [HttpGet("{analysisId}")]
    public async Task<ActionResult<AnalysisResponse>> GetResults(string analysisId)
    {
        try
        {
            var userId = User.FindFirst("user_id")?.Value;
            if (string.IsNullOrEmpty(userId))
                return Unauthorized();

            var response = await _analysisService.GetAnalysisResultsAsync(userId, analysisId);
            
            if (response == null)
                return NotFound(new { error = "Analysis not found" });

            return Ok(response);
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error getting analysis results");
            return StatusCode(500, new { error = "Failed to get results" });
        }
    }

    /// <summary>
    /// Get all user analyses
    /// </summary>
    [HttpGet]
    public async Task<ActionResult<List<AnalysisResponse>>> GetUserAnalyses()
    {
        try
        {
            var userId = User.FindFirst("user_id")?.Value;
            if (string.IsNullOrEmpty(userId))
                return Unauthorized();

            var analyses = await _analysisService.GetUserAnalysesAsync(userId);
            return Ok(analyses);
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error getting user analyses");
            return StatusCode(500, new { error = "Failed to get analyses" });
        }
    }

    /// <summary>
    /// Delete analysis
    /// </summary>
    [HttpDelete("{analysisId}")]
    public async Task<ActionResult> DeleteAnalysis(string analysisId)
    {
        try
        {
            var userId = User.FindFirst("user_id")?.Value;
            if (string.IsNullOrEmpty(userId))
                return Unauthorized();

            var success = await _analysisService.DeleteAnalysisAsync(userId, analysisId);
            
            if (!success)
                return NotFound(new { error = "Analysis not found" });

            return NoContent();
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error deleting analysis");
            return StatusCode(500, new { error = "Failed to delete analysis" });
        }
    }

    /// <summary>
    /// Download analysis report
    /// </summary>
    [HttpGet("{analysisId}/report/{format}")]
    public async Task<ActionResult> DownloadReport(string analysisId, string format)
    {
        try
        {
            var userId = User.FindFirst("user_id")?.Value;
            if (string.IsNullOrEmpty(userId))
                return Unauthorized();

            var (stream, contentType, fileName) = await _analysisService.GetReportAsync(userId, analysisId, format);
            
            if (stream == null)
                return NotFound(new { error = "Report not found" });

            return File(stream, contentType, fileName);
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Error downloading report");
            return StatusCode(500, new { error = "Failed to download report" });
        }
    }
}
