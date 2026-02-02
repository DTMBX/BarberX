using System.Collections.ObjectModel;
using CommunityToolkit.Mvvm.ComponentModel;
using CommunityToolkit.Mvvm.Input;
using Evident.MatterDocket.MAUI.Models;
using Evident.MatterDocket.MAUI.Services;

namespace Evident.MatterDocket.MAUI.ViewModels;

public partial class ChatViewModel : ObservableObject
{
    private readonly IChatGptService _chatService;
    private readonly IProjectService _projectService;
    private readonly IEvidenceService _evidenceService;

    [ObservableProperty]
    private Project? currentProject;

    [ObservableProperty]
    private Conversation? currentConversation;

    [ObservableProperty]
    private string messageText = string.Empty;

    [ObservableProperty]
    private bool isAssistantTyping;

    [ObservableProperty]
    private bool showLegalTools;

    [ObservableProperty]
    private ObservableCollection<ChatMessage> messages = new();

    [ObservableProperty]
    private ObservableCollection<EvidenceItem> attachedEvidence = new();

    public bool CanSendMessage => !string.IsNullOrWhiteSpace(MessageText) && !IsAssistantTyping;
    public bool HasAttachedEvidence => AttachedEvidence.Count > 0;

    public ChatViewModel(
        IChatGptService chatService,
        IProjectService projectService,
        IEvidenceService evidenceService)
    {
        _chatService = chatService;
        _projectService = projectService;
        _evidenceService = evidenceService;
    }

    [RelayCommand]
    public async Task LoadConversationAsync()
    {
        if (CurrentProject == null || CurrentConversation == null)
            return;

        try
        {
            var response = await _chatService.GetConversationMessagesAsync(CurrentConversation.Id);
            
            if (response.Success && response.Data != null)
            {
                Messages.Clear();
                foreach (var msg in response.Data.Messages)
                {
                    Messages.Add(msg);
                }
            }
        }
        catch (Exception ex)
        {
            await Shell.Current.DisplayAlert("Error", $"Failed to load conversation: {ex.Message}", "OK");
        }
    }

    [RelayCommand]
    async Task SendMessageAsync()
    {
        if (!CanSendMessage)
            return;

        var userMessage = MessageText.Trim();
        MessageText = string.Empty;

        // Add user message to UI immediately
        var userChatMessage = new ChatMessage
        {
            Role = "user",
            Content = userMessage,
            Timestamp = DateTime.Now
        };
        Messages.Add(userChatMessage);

        // Scroll to bottom
        // TODO: Implement auto-scroll

        IsAssistantTyping = true;

        try
        {
            // Build context from attached evidence
            var context = await BuildContextFromEvidenceAsync();

            var request = new ChatRequest
            {
                Message = userMessage,
                ConversationId = CurrentConversation?.Id,
                ProjectId = CurrentProject?.Id ?? 0,
                Context = context,
                AttachedEvidenceIds = AttachedEvidence.Select(e => e.Id).ToList()
            };

            var response = await _chatService.SendMessageAsync(request);

            if (response.Success && response.Data != null)
            {
                // Add assistant response to UI
                var assistantMessage = new ChatMessage
                {
                    Role = "assistant",
                    Content = response.Data.Content,
                    Model = response.Data.Model,
                    TokensUsed = response.Data.TokensUsed,
                    Timestamp = DateTime.Now
                };
                Messages.Add(assistantMessage);

                // Update conversation ID if this was first message
                if (CurrentConversation == null && response.Data.ConversationId > 0)
                {
                    CurrentConversation = new Conversation
                    {
                        Id = response.Data.ConversationId,
                        Title = TruncateTitle(userMessage)
                    };
                }

                // Clear attached evidence after successful send
                AttachedEvidence.Clear();
                OnPropertyChanged(nameof(HasAttachedEvidence));
            }
            else
            {
                await Shell.Current.DisplayAlert("Error", response.Error ?? "Failed to send message", "OK");
            }
        }
        catch (Exception ex)
        {
            await Shell.Current.DisplayAlert("Error", $"Failed to send message: {ex.Message}", "OK");
        }
        finally
        {
            IsAssistantTyping = false;
        }
    }

    [RelayCommand]
    async Task AttachEvidenceAsync()
    {
        try
        {
            // TODO: Show evidence picker (from current case)
            await Shell.Current.DisplayAlert("Coming Soon", "Evidence attachment will be available soon", "OK");
        }
        catch (Exception ex)
        {
            await Shell.Current.DisplayAlert("Error", $"Failed to attach evidence: {ex.Message}", "OK");
        }
    }

    [RelayCommand]
    void RemoveEvidence(EvidenceItem evidence)
    {
        AttachedEvidence.Remove(evidence);
        OnPropertyChanged(nameof(HasAttachedEvidence));
    }

    [RelayCommand]
    void ToggleLegalTools()
    {
        ShowLegalTools = !ShowLegalTools;
    }

    [RelayCommand]
    async Task RunLegalToolAsync(string toolType)
    {
        // Legal tool instructions from LEGAL-AI-TOOLS.md
        var toolInstructions = GetLegalToolInstructions(toolType);
        
        if (string.IsNullOrEmpty(toolInstructions))
        {
            await Shell.Current.DisplayAlert("Error", "Unknown legal tool", "OK");
            return;
        }

        // Add system message indicating tool activation
        Messages.Add(new ChatMessage
        {
            Role = "system",
            Content = $"Activated {GetToolDisplayName(toolType)}",
            Timestamp = DateTime.Now
        });

        // Send analysis request
        MessageText = toolInstructions;
        await SendMessageAsync();
    }

    [RelayCommand]
    async Task SelectProjectAsync()
    {
        try
        {
            // TODO: Show project picker
            await Shell.Current.DisplayAlert("Coming Soon", "Project selection will be available soon", "OK");
        }
        catch (Exception ex)
        {
            await Shell.Current.DisplayAlert("Error", $"Failed to select project: {ex.Message}", "OK");
        }
    }

    [RelayCommand]
    async Task OpenProjectSettingsAsync()
    {
        if (CurrentProject == null)
        {
            await Shell.Current.DisplayAlert("No Project", "Please select a project first", "OK");
            return;
        }

        try
        {
            // TODO: Navigate to project settings page
            await Shell.Current.DisplayAlert("Coming Soon", "Project settings will be available soon", "OK");
        }
        catch (Exception ex)
        {
            await Shell.Current.DisplayAlert("Error", $"Failed to open settings: {ex.Message}", "OK");
        }
    }

    private async Task<string> BuildContextFromEvidenceAsync()
    {
        if (!HasAttachedEvidence)
            return string.Empty;

        var contextBuilder = new System.Text.StringBuilder();
        contextBuilder.AppendLine("Attached Evidence:");
        contextBuilder.AppendLine();

        foreach (var evidence in AttachedEvidence)
        {
            contextBuilder.AppendLine($"File: {evidence.Filename}");
            contextBuilder.AppendLine($"Type: {evidence.FileType}");
            
            // Include transcription/OCR text if available
            if (!string.IsNullOrEmpty(evidence.TranscriptionText))
            {
                contextBuilder.AppendLine("Content:");
                contextBuilder.AppendLine(evidence.TranscriptionText);
            }
            
            contextBuilder.AppendLine();
        }

        return contextBuilder.ToString();
    }

    private string GetLegalToolInstructions(string toolType)
    {
        return toolType.ToLower() switch
        {
            "brady" => "Analyze the attached evidence for potential Brady violations. Identify exculpatory evidence, disclosure failures, and materiality issues. Provide severity ratings and suggested remedies.",
            
            "fourth" => "Conduct a Fourth Amendment analysis of the attached evidence. Evaluate probable cause, reasonable suspicion, consent, warrant issues, and exclusionary rule applicability. Cite relevant case law.",
            
            "miranda" => "Analyze the interrogation evidence for Miranda violations. Evaluate custody, interrogation, warnings, waiver, and invocation. Flag suppressible statements.",
            
            "timeline" => "Create a detailed chronological timeline from the attached evidence. Extract all temporal references, flag conflicts between sources, and highlight gaps. Output as a formatted table.",
            
            "inconsistency" => "Compare all statements in the attached evidence and identify contradictions, omissions, impossible claims, and impeachment material. Create a comparison matrix.",
            
            "chain" => "Audit the chain of custody for the attached evidence. Check for completeness, gaps, integrity issues, and legal standards. Flag any breaks in the chain.",
            
            "caselaw" => "Research relevant case law for the legal issues in the attached evidence. Find binding precedent, persuasive authority, and organize by strength. Flag negative authority to distinguish.",
            
            _ => string.Empty
        };
    }

    private string GetToolDisplayName(string toolType)
    {
        return toolType.ToLower() switch
        {
            "brady" => "Brady Violation Detector 🔍",
            "fourth" => "Fourth Amendment Analyzer ⚖️",
            "miranda" => "Miranda Violation Checker 🗣️",
            "timeline" => "Timeline Generator 📅",
            "inconsistency" => "Inconsistency Detector 📝",
            "chain" => "Chain of Custody Verifier 🔗",
            "caselaw" => "Case Law Finder 📚",
            _ => "Legal Analysis Tool"
        };
    }

    private string TruncateTitle(string message, int maxLength = 50)
    {
        if (message.Length <= maxLength)
            return message;

        return message.Substring(0, maxLength - 3) + "...";
    }

    partial void OnMessageTextChanged(string value)
    {
        OnPropertyChanged(nameof(CanSendMessage));
    }
}
