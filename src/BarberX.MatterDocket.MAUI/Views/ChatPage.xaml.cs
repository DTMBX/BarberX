using Evident.MatterDocket.MAUI.ViewModels;

namespace Evident.MatterDocket.MAUI.Views;

public partial class ChatPage : ContentPage
{
    public ChatPage(ChatViewModel viewModel)
    {
        InitializeComponent();
        BindingContext = viewModel;
    }

    private void OnMessageInputCompleted(object sender, EventArgs e)
    {
        // Send message when user presses Enter
        if (BindingContext is ChatViewModel viewModel && viewModel.CanSendMessage)
        {
            viewModel.SendMessageCommand.Execute(null);
        }
    }

    protected override void OnAppearing()
    {
        base.OnAppearing();
        
        // Focus message input
        MessageInput.Focus();
        
        // Load conversation history
        if (BindingContext is ChatViewModel viewModel)
        {
            Task.Run(async () => await viewModel.LoadConversationAsync());
        }
    }

    protected override void OnDisappearing()
    {
        base.OnDisappearing();
        
        // Unfocus to hide keyboard
        MessageInput.Unfocus();
    }
}
