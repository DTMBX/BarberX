# Evident User Flow Testing Guide

## All Fixes Implemented ✅

### **Fixed Issues:**

1. ✅ Registration links corrected (`/auth/register` → `/register`)
2. ✅ Added `/auth/register` alias route for backward compatibility
3. ✅ Tier parameter now passed and displayed in signup
4. ✅ Trial period messaging added
5. ✅ Signup redirects to checkout for paid tiers

--

## **Complete User Journey Test Cases**

### **Test Case 1: Free Tier Signup**

**Path:** Pricing Page → Free Tier → Registration → Dashboard

**Steps:**

1. Navigate to `/pricing`
2. Click "Get Started Free" button
3. Verify redirects to `/register`
4. Fill out form:
   - Full Name: "Test User"
   - Email: "test@example.com"
   - Password: "SecurePass123!"
   - Confirm Password: "SecurePass123!"
5. Submit form
6. **Expected Result:**
   - Success message: "Account created successfully! Welcome to Evident."
   - Redirects to `/dashboard`
   - User tier: FREE
   - Usage tracking initialized

--

### **Test Case 2: Professional Tier Signup**

**Path:** Pricing Page → Professional Tier → Registration → Checkout

**Steps:**

1. Navigate to `/pricing`
2. Click "Start 14-Day Free Trial" on Professional tier
3. Verify redirects to `/register?tier=professional`
4. **Verify Tier Badge Displays:**
   - Box shows "Signing up for Professional Plan"
   - Shows "✓ 14 days free trial included"
   - Note: "You'll start with a Free account..."
5. Fill out registration form
6. Submit form
7. **Expected Result:**
   - Success message: "Account created! Complete checkout to activate your Professional plan."
   - Session stores: `checkout_tier = 'professional'`
   - Redirects back to `/pricing` to complete payment
   - User tier: FREE (until payment)

--

### **Test Case 3: Premium Tier Signup**

**Path:** Pricing Page → Premium Tier → Registration → Checkout

**Steps:**

1. Navigate to `/pricing`
2. Click "Start 14-Day Free Trial" on Premium tier
3. Verify redirects to `/register?tier=premium`
4. **Verify Tier Badge:**
   - Shows "Premium Plan"
   - Shows trial period
5. Complete registration
6. **Expected Result:**
   - Redirects to pricing for checkout
   - Session stores tier preference

--

### **Test Case 4: Existing User Login**

**Path:** Login Page → Dashboard

**Steps:**

1. Navigate to `/login` or `/auth/login`
2. Enter existing credentials
3. Click "Sign In"
4. **Expected Result:**
   - Welcome message: "Welcome back, [Name]!"
   - Redirects to `/dashboard`
   - Last login timestamp updated

--

### **Test Case 5: Registration Link Variations**

**Test all registration entry points work:**

1. `/register` → ✅ Works
2. `/auth/register` → ✅ Works (alias)
3. `/auth/signup` → ✅ Works
4. `/register?tier=professional` → ✅ Shows tier badge
5. `/register?tier=premium` → ✅ Shows tier badge
6. `/register?tier=free` → ✅ No special badge (default)

--

### **Test Case 6: Password Validation**

**Verify password strength requirements:**

**Invalid Passwords:**

- "12345" → ❌ "Password must be at least 8 characters"
- "short" → ❌ "Password must be at least 8 characters"
- "" → ❌ "Email and password are required"

**Valid Passwords:**

- "LongSecurePassword123!" → ✅ Accepts
- "MyP@ssw0rd" → ✅ Accepts

--

### **Test Case 7: Duplicate Email**

**Prevent duplicate accounts:**

**Steps:**

1. Register with email: "existing@user.com"
2. Logout
3. Try to register again with same email
4. **Expected Result:**
   - Flash message: "An account with this email already exists."
   - Redirects to `/auth/login`

--

### **Test Case 8: Password Mismatch**

**Verify confirm password validation:**

**Steps:**

1. Fill password: "MyPassword123"
2. Fill confirm: "DifferentPassword"
3. Submit
4. **Expected Result:**
   - Flash message: "Passwords do not match."
   - Stays on signup page
   - Form preserves entered data

--

### **Test Case 9: Dashboard Access**

**Verify authentication required:**

**Steps:**

1. Navigate to `/dashboard` while logged out
2. **Expected Result:**
   - Flash message: "Please log in to access this page."
   - Redirects to `/auth/login?next=/dashboard`
3. Login successfully
4. **Expected Result:**
   - Redirects back to `/dashboard`

--

### **Test Case 10: Logout Flow**

**Verify session termination:**

**Steps:**

1. Login successfully
2. Navigate to `/auth/logout`
3. **Expected Result:**
   - Flash message: "You have been logged out successfully."
   - Redirects to `/` (index)
   - Session cleared
4. Try accessing `/dashboard`
5. **Expected Result:**
   - Redirects to login (not authenticated)

--

## **Edge Cases to Test**

### **EC1: XSS Prevention**

- Input: `<script>alert('xss')</script>` in name field
- **Expected:** Sanitized/escaped output

### **EC2: SQL Injection Prevention**

- Input: `' OR '1'='1` in email field
- **Expected:** Treated as literal string, query fails safely

### **EC3: Long Inputs**

- Input: 500-character name
- **Expected:** Validation error or truncation

### **EC4: Empty Form Submission**

- Submit with all fields empty
- **Expected:** Flash message for required fields

### **EC5: Invalid Email Format**

- Input: "notanemail"
- **Expected:** "Invalid email format"

--

## **Database Verification Queries**

After successful registration, verify in database:

```sql
- Check user created
SELECT id, email, full_name, tier, is_active, is_verified, created_at
FROM users
WHERE email = 'test@example.com';

- Check usage tracking initialized
SELECT * FROM usage_tracking
WHERE user_id = (SELECT id FROM users WHERE email = 'test@example.com');

- Check tier enum value
SELECT tier FROM users WHERE email = 'test@example.com';
- Should return: 0 (FREE), 1 (PRO), 2 (PREMIUM), or 3 (ADMIN)
```

--

## **Browser Console Checks**

Open browser DevTools and verify:

1. **No JavaScript errors** in console
2. **Form validation** triggers before submission
3. **Password visibility toggle** works (if implemented)
4. **Network requests:**
   - POST to `/register` returns 302 redirect
   - Redirect location is correct

--

## **Session/Cookie Verification**

After login, check:

1. **Session cookie** set: `session=[encrypted data]`
2. **Remember me** (if checked): Cookie expires in 30 days
3. **CSRF token** present in form

--

## **Accessibility Testing**

1. **Keyboard Navigation:**
   - Tab through all form fields ✅
   - Submit with Enter key ✅

2. **Screen Reader:**
   - Labels properly associated with inputs ✅
   - Error messages announced ✅

3. **Color Contrast:**
   - Text meets WCAG AA standards ✅

--

## **Performance Metrics**

**Target Metrics:**

- Page load: < 2 seconds
- Form submission: < 500ms
- Database query: < 100ms
- Redirect: < 200ms

--

## **Known Limitations & Future Enhancements**

### **Current Behavior:**

- All new users start with FREE tier (security measure)
- Paid tiers require Stripe checkout (not yet fully implemented)
- Email verification is disabled (development mode)
- Auto-login after registration (development only)

### **Production Requirements:**

1. Enable email verification
2. Disable auto-login
3. Complete Stripe checkout integration
4. Add rate limiting (prevent spam registrations)
5. Add CAPTCHA for bot prevention

--

## **Quick Test Commands**

```bash
# Reset test database
python reset_test_db.py

# Create test users
python create_test_accounts.py

# Run automated tests
pytest tests/test_auth_flow.py -v

# Check logs
tail -f logs/app.log

# Monitor database
watch -n 1 'psql -d Evident -c "SELECT COUNT(*) FROM users;"'
```

--

## **Success Criteria**

All test cases pass when:

- ✅ All registration links work (no 404s)
- ✅ Tier parameters are displayed correctly
- ✅ Users can successfully create accounts
- ✅ Login/logout flows work smoothly
- ✅ Dashboard loads with correct user data
- ✅ No security vulnerabilities
- ✅ All error messages are user-friendly
- ✅ Database integrity maintained

--

## **Rollback Plan**

If issues occur:

1. Revert `auth_routes.py` changes
2. Revert `pricing.html` link changes
3. Revert `signup.html` template
4. Restart Flask app
5. Clear browser cache/cookies

**Backup files created:**

- `auth_routes.py.bak`
- `pricing.html.bak`
- `signup.html.bak`
