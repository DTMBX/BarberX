# Netlify Forms Setup - Evident Early Access

## ✅ Form Configuration Complete

The early access form at `_includes/connect.html` is properly configured for Netlify Forms with **zero server-side code or JavaScript required**.

### Form Setup Checklist

✅ **Form Attributes:**

- `name="early-access"` - Unique form identifier
- `method="POST"` - Required for Netlify Forms
- `data-netlify="true"` - Enables Netlify form detection
- `netlify-honeypot="bot-field"` - Spam protection

✅ **Hidden Fields:**

- `<input type="hidden" name="form-name" value="early-access" />` - Required for Netlify

✅ **Spam Protection:**

- Honeypot field (`bot-field`) hidden with CSS
- Bots will fill it out, humans won't see it

✅ **Form Fields:**

- `email` (required) - Email address input
- `interest` (required) - Role selection dropdown with 4 options:
  - Just Curious
  - Supporter
  - Developer / Contributor
  - Ethics / Security Reviewer

✅ **Dynamic Redirects:**

- JavaScript updates action URL based on selected role
- Redirects to role-specific thank you pages:
  - `/thank-you/curious/`
  - `/thank-you/supporter/`
  - `/thank-you/developer/`
  - `/thank-you/reviewer/`

## How It Works

1. **Deploy Time:** Netlify parses the HTML and detects the form automatically
2. **User Submits:** Form data is sent to Netlify's servers
3. **Data Stored:** Submission appears in Netlify dashboard under Forms
4. **Redirect:** User is sent to the appropriate thank you page
5. **No Code:** All processing happens on Netlify's infrastructure

## Accessing Submissions

1. Go to Netlify dashboard
2. Select your Evident site
3. Click **Forms** in sidebar
4. View all submissions for **early-access** form
5. Export as CSV or integrate with Zapier, Slack, etc.

## Data Collected Per Submission

- **Email Address** (text)
- **Interest/Role** (dropdown selection)
- **Timestamp** (automatic)
- **Referrer** (automatic)
- **IP Address** (optional, can be disabled)

## Spam Protection

- **Honeypot field** catches bots
- **Netlify's built-in spam filtering** (optional)
- **reCAPTCHA** can be added if needed

## Cost

- **Free tier:** 100 submissions/month
- **Pro tier:** 1,000 submissions/month
- Additional submissions available in higher plans

## No Server Required

✅ No backend code
✅ No database
✅ No API calls
✅ No hosting costs for form processing
✅ Automatic spam filtering
✅ Instant notifications (optional)

## Form Detection Status

Form detection is **ENABLED** in your Netlify site settings.

The form will be automatically detected on the next deploy after any HTML changes.
