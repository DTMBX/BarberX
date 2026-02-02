using Evident.MatterDocket.MAUI.Models;

namespace Evident.MatterDocket.MAUI.Services;

public interface IBillingService
{
    Task<CheckoutSessionResponse?> CreateCheckoutSessionAsync(string priceId, string tier);
    Task<BillingPortalResponse?> CreatePortalSessionAsync();
}

public class BillingService : IBillingService
{
    private readonly ApiService _apiService;

    public BillingService(ApiService apiService)
    {
        _apiService = apiService;
    }

    public async Task<CheckoutSessionResponse?> CreateCheckoutSessionAsync(string priceId, string tier)
    {
        try
        {
            var request = new CreateCheckoutRequest
            {
                PriceId = priceId,
                Tier = tier
            };

            var response = await _apiService.PostAsync<CheckoutSessionResponse>("/billing/create-checkout-session", request);
            return response.Success ? response.Data : null;
        }
        catch
        {
            return null;
        }
    }

    public async Task<BillingPortalResponse?> CreatePortalSessionAsync()
    {
        try
        {
            var response = await _apiService.PostAsync<BillingPortalResponse>("/billing/portal", new {});
            return response.Success ? response.Data : null;
        }
        catch
        {
            return null;
        }
    }
}
