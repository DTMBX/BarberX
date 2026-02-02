using Evident.MatterDocket.MAUI.Models;

namespace Evident.MatterDocket.MAUI.Services;

public interface IProjectService
{
    Task<ApiResponse<ProjectsResponse>> GetProjectsAsync();
    Task<ApiResponse<Project>> CreateProjectAsync(CreateProjectRequest request);
    Task<ApiResponse<Project>> UpdateProjectAsync(int projectId, CreateProjectRequest request);
    Task<ApiResponse<bool>> DeleteProjectAsync(int projectId);
    Task<ApiResponse<ConversationsResponse>> GetConversationsAsync(int projectId);
}

public class ProjectService : IProjectService
{
    private readonly IApiService _apiService;

    public ProjectService(IApiService apiService)
    {
        _apiService = apiService;
    }

    /// <summary>
    /// Get all projects for current user
    /// </summary>
    public async Task<ApiResponse<ProjectsResponse>> GetProjectsAsync()
    {
        try
        {
            return await _apiService.GetAsync<ProjectsResponse>("/projects");
        }
        catch (Exception ex)
        {
            return new ApiResponse<ProjectsResponse>
            {
                Success = false,
                Error = $"Failed to get projects: {ex.Message}"
            };
        }
    }

    /// <summary>
    /// Create a new project
    /// </summary>
    public async Task<ApiResponse<Project>> CreateProjectAsync(CreateProjectRequest request)
    {
        try
        {
            return await _apiService.PostAsync<Project>("/projects", request);
        }
        catch (Exception ex)
        {
            return new ApiResponse<Project>
            {
                Success = false,
                Error = $"Failed to create project: {ex.Message}"
            };
        }
    }

    /// <summary>
    /// Update project settings
    /// </summary>
    public async Task<ApiResponse<Project>> UpdateProjectAsync(int projectId, CreateProjectRequest request)
    {
        try
        {
            return await _apiService.PutAsync<Project>($"/projects/{projectId}", request);
        }
        catch (Exception ex)
        {
            return new ApiResponse<Project>
            {
                Success = false,
                Error = $"Failed to update project: {ex.Message}"
            };
        }
    }

    /// <summary>
    /// Delete a project
    /// </summary>
    public async Task<ApiResponse<bool>> DeleteProjectAsync(int projectId)
    {
        try
        {
            var response = await _apiService.DeleteAsync($"/projects/{projectId}");
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
                Error = $"Failed to delete project: {ex.Message}"
            };
        }
    }

    /// <summary>
    /// Get conversations for a project
    /// </summary>
    public async Task<ApiResponse<ConversationsResponse>> GetConversationsAsync(int projectId)
    {
        try
        {
            return await _apiService.GetAsync<ConversationsResponse>($"/conversations?project_id={projectId}");
        }
        catch (Exception ex)
        {
            return new ApiResponse<ConversationsResponse>
            {
                Success = false,
                Error = $"Failed to get conversations: {ex.Message}"
            };
        }
    }
}
