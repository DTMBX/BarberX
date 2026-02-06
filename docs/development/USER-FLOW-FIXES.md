# Evident User Flow Issues & Fixes

## Critical Issues Identified

### 1. **Broken Registration Links** (CRITICAL)

**Problem**: Pricing page links to `/auth/register` but route is `/register` or `/auth/signup`
**Impact**: Users clicking "Start Free Trial" get 404 errors
**Files Affected**:

- `pricing.html` (lines 46, 71, 94, 263)
- `landing.html` (any registration CTAs)

### 2. **Inconsistent Route Naming**

**Problem**: Multiple routes for same functionality

- `/register` → redirects to `auth.signup`
- `/auth/signup` → actual handler
- Pricing links to `/auth/register` (doesn't exist)

### 3. **Missing Tier Parameter Handling**

**Problem**: Registration links include `?tier=professional` but signup doesn't use it
**Impact**: Users can't start with paid tiers, always get FREE
**Files Affected**:

- `auth_routes.py` signup function
- `templates/auth/signup.html` (missing tier input)

### 4. **Checkout Button Not Wired**

**Problem**: Pricing page has JavaScript `checkout(plan)` but function doesn't exist
**Impact**: Payment flow broken
**Files Affected**:

- `pricing.html` (missing script)

## Fixes to Implement

### Fix 1: Update All Registration Links

```html
<!-- BEFORE ->
<a href="/auth/register">...</a>

<!-- AFTER ->
<a href="/register">...</a>
<!-- OR ->
<a href="/auth/signup">...</a>
```

### Fix 2: Add Tier Parameter Support to Signup

```python
# In auth_routes.py signup()
tier_param = request.args.get('tier', 'free').lower()
tier_map = {
    'free': TierLevel.FREE,
    'professional': TierLevel.PRO,
    'premium': TierLevel.PREMIUM
}
initial_tier = tier_map.get(tier_param, TierLevel.FREE)
```

### Fix 3: Add Checkout JavaScript to Pricing

```javascript
function checkout(plan) {
  // Redirect to registration with plan parameter
  window.location.href = `/register?tier=${plan}&checkout=true`;
}
```

### Fix 4: Create /auth/register Alias Route

```python
# In auth_routes.py
@auth_bp.route('/register', methods=['GET', 'POST'])
def register_alias():
    """Alias for signup - maintain backward compatibility"""
    return signup()
```

### Fix 5: Add Visual Tier Selection to Signup Page

- Show which tier they're signing up for
- Display tier benefits
- Trial period notice (for paid tiers)
