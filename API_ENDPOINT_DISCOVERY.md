# How to Fix 404 API Errors

## Problem

When you run the Carrd automation script, you see errors like:
```
ERROR | Registration failed with status: 404
```

This happens because the API endpoints in the script are **placeholders** and don't match Carrd's actual API.

## Solution: Discover Real API Endpoints

You need to find the actual API endpoints that Carrd.co uses. Here's how:

### Step 1: Open Browser DevTools

1. Open **Google Chrome** or **Firefox**
2. Press **F12** to open Developer Tools
3. Click on the **Network** tab
4. Check the box for **"Preserve log"** (important!)

### Step 2: Perform Actions on Carrd.co

Navigate to https://carrd.co and perform the actions you want to automate:

#### For Registration Endpoint:
1. Click "Sign Up" or "Get Started"
2. Fill in the registration form
3. Click "Register" or "Create Account"
4. In the Network tab, look for XHR/Fetch requests
5. Find the request that was sent when you clicked register

#### For Site Creation Endpoint:
1. Log into Carrd
2. Create a new site
3. Look for the API call in Network tab

#### For Publishing Endpoint:
1. After editing a site, click "Publish"
2. Look for the publish API call

### Step 3: Identify the Endpoint

In the Network tab, click on the request and look at:
- **Request URL**: This is the endpoint you need (e.g., `https://carrd.co/api/v1/auth/register`)
- **Request Method**: GET or POST
- **Request Headers**: Note any special headers needed
- **Form Data** or **Payload**: Note the data structure

### Step 4: Update the Script

Open `carrd_automation.py` and update the endpoints:

#### Example for Registration:

If you discover the endpoint is `https://carrd.co/api/v1/auth/register`:

```python
# Line ~205 - Update this:
register_url = f"{CARRD_BASE_URL}/api/v1/auth/register"  # ← Change this

# Also update payload structure if needed
payload = {
    'email': temp_email,
    'password': password,
    # Add any other fields you see in the actual request
}
```

#### Example for Site Creation:

If the endpoint is `https://carrd.co/api/v1/sites`:

```python
# Line ~275 - Update this:
create_url = f"{CARRD_BASE_URL}/api/v1/sites"  # ← Change this
```

### Step 5: Update All Endpoints

You need to discover and update these endpoints:

1. **Registration** (`register_account()` - line ~205)
   - Default placeholder: `/account/register`
   - Look for: Registration/signup API call

2. **Pro Trial** (`activate_pro_trial()` - line ~250)
   - Default placeholder: `/account/upgrade/trial`
   - Look for: Upgrade/trial API call

3. **Create Site** (`create_site_from_template()` - line ~270)
   - Default placeholder: `/api/sites/create`
   - Look for: Site creation API call

4. **Add Form** (`add_form_to_site()` - line ~310)
   - Default placeholder: `/api/sites/{id}/elements/add`
   - Look for: Element/form addition API call

5. **Publish Site** (`publish_site()` - line ~350)
   - Default placeholder: `/api/sites/{id}/publish`
   - Look for: Publish API call

6. **Submit Form** (`send_message_through_form()` - line ~390)
   - Default placeholder: `{site_url}/submit`
   - Look for: Form submission endpoint (may be on published site)

### Step 6: Test

After updating endpoints:

```bash
python carrd_automation.py
```

Check the logs - you should see successful responses instead of 404 errors.

## Alternative: Use DRY_RUN_MODE

If you want to test the script flow without making actual API calls:

1. Open `carrd_automation.py`
2. Find line ~48: `DRY_RUN_MODE = False`
3. Change to: `DRY_RUN_MODE = True`
4. Run the script - it will log what it would do without making API calls

## Common Issues

### CORS Errors
If you get CORS errors, you may need to add proper headers:
```python
headers = {
    'Origin': 'https://carrd.co',
    'Referer': 'https://carrd.co/',
    # Add any other headers you see in the browser
}
```

### Authentication Errors
Some endpoints may require authentication tokens:
- Check if Carrd sends a CSRF token
- Check cookies for session tokens
- Update the headers accordingly

### Different Payload Structure
If your payload doesn't match what Carrd expects:
- Copy the exact JSON/form data from DevTools
- Update the `payload` dictionary to match

## Need Help?

If you're stuck:
1. Share the Network tab screenshot showing the request
2. Share the exact error message from the script
3. Ask in the issue tracker

## Important Note

Carrd may update their API at any time, so endpoints may change. Always verify using the latest version of their website.
