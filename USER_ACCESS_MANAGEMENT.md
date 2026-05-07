# Dashboard User Access Management Guide

## How Dashboard Authorization Works

The dashboard uses **IBM App ID** for authentication and authorization:

1. **Authentication**: Users log in via IBM App ID (SSO with IBM w3id)
2. **Authorization**: Users must have at least one **role** assigned in App ID to access the dashboard
3. **Access Check**: Code checks `_user_has_a_role()` - if user has no roles, they see "Unauthorized!"

## Managing User Access via IBM Cloud Console

### Step 1: Access IBM App ID Service

1. Go to IBM Cloud Console: https://cloud.ibm.com
2. Navigate to **Resource List**
3. Find and click on your App ID instance (likely named something like `python-appid-service`)

### Step 2: View Current Users

1. In App ID dashboard, click **Users** in the left sidebar
2. You'll see a list of all users who have logged in
3. Each user shows:
   - Email address
   - Identity provider (Cloud Directory, IBM w3id, etc.)
   - Roles assigned
   - Last login date

### Step 3: Add a New User (Grant Access)

#### Option A: User Already Logged In (Recommended)
If the user has already tried to access the dashboard:

1. Go to **Users** section in App ID
2. Find the user by email address
3. Click on the user
4. Click **Assign roles**
5. Select a role (or create a new one)
6. Click **Save**
7. User can now access the dashboard (may need to log out and back in)

#### Option B: Pre-authorize User (Before First Login)
If you want to grant access before they try to log in:

1. Go to **Users** section
2. Click **Add user** (if using Cloud Directory)
3. For IBM w3id users, they must log in first, then you assign roles

### Step 4: Create Roles (If Needed)

The dashboard just checks if user has **any role**, so you can create simple roles:

1. Go to **Roles** section in App ID
2. Click **Create role**
3. Name it something like:
   - `dashboard-viewer`
   - `dashboard-user`
   - `external-client`
   - `ibm-employee`
4. Add description (optional)
5. Click **Save**

### Step 5: Remove User Access

To revoke access:

1. Go to **Users** section
2. Find the user
3. Click on the user
4. Remove all roles
5. User will see "Unauthorized!" on next login

## Managing Users via IBM Cloud CLI

### List All Users
```bash
# Get your App ID tenant ID
ibmcloud resource service-instance python-appid-service --output json | grep "guid"

# Set tenant ID
export TENANT_ID="your-tenant-id-here"

# Get IAM token
ibmcloud iam oauth-tokens

# List users (requires management API)
curl -X GET \
  "https://us-south.appid.cloud.ibm.com/management/v4/$TENANT_ID/users" \
  -H "Authorization: Bearer YOUR_IAM_TOKEN"
```

### Assign Role to User
```bash
# Get user ID from the list above
export USER_ID="user-id-here"
export ROLE_ID="role-id-here"

curl -X PUT \
  "https://us-south.appid.cloud.ibm.com/management/v4/$TENANT_ID/users/$USER_ID/roles" \
  -H "Authorization: Bearer YOUR_IAM_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "roles": {
      "ids": ["'$ROLE_ID'"]
    }
  }'
```

## Common Scenarios

### Scenario 1: External Client Needs Access

**Example:** Capital One employee needs to view their data

1. Ask them to try logging in to the dashboard URL
2. They'll see "Unauthorized!" after login
3. Go to App ID Users section
4. Find their email (e.g., `john.doe@capitalone.com`)
5. Assign them the `dashboard-viewer` role
6. Notify them to refresh the page or log out/in

### Scenario 2: New IBM Employee Needs Access

**Example:** New team member joins

1. They log in with IBM w3id
2. See "Unauthorized!"
3. You assign them a role in App ID
4. They refresh and can access dashboard

### Scenario 3: Bulk User Addition

If you need to add many users at once:

1. Create a CSV file with email addresses
2. Use App ID bulk import feature (Cloud Directory only)
3. Or use the Management API in a script

### Scenario 4: Temporary Access

**Example:** Contractor needs 30-day access

1. Assign role when needed
2. Set calendar reminder for 30 days
3. Remove role after 30 days
4. Or use App ID's access policies (if available in your plan)

## Checking Who Has Access

### Via IBM Cloud Console
1. Go to App ID → Users
2. Filter by "Has roles"
3. Export list if needed

### Via Dashboard Logs
Check the weekly log exports in `C:\DashboardLogs`:

```powershell
# See all users who logged in this week
Get-Content "C:\DashboardLogs\logins-*.txt" | Select-String "logged in"

# Get unique users
Get-Content "C:\DashboardLogs\logins-*.txt" | 
    Select-String "User (.*?) logged in" | 
    ForEach-Object { $_.Matches.Groups[1].Value } | 
    Sort-Object -Unique
```

## Troubleshooting

### User Sees "Unauthorized!" After Login

**Cause:** User has no roles assigned in App ID

**Solution:**
1. Verify user appears in App ID Users list
2. Assign at least one role to the user
3. User may need to log out and back in

### User Can't Log In At All

**Cause:** Authentication issue, not authorization

**Possible Issues:**
- User not in IBM w3id system
- App ID not configured for their identity provider
- Network/firewall issues

**Solution:**
- Check App ID identity providers configuration
- Verify user can access other IBM Cloud services
- Check App ID logs for authentication errors

### How to See All Roles

```bash
# Via CLI
ibmcloud resource service-instance python-appid-service

# Via Console
App ID → Roles section
```

## Best Practices

### 1. Use Descriptive Role Names
- ✅ `external-client-viewer`
- ✅ `ibm-employee-full-access`
- ❌ `role1`
- ❌ `test`

### 2. Document Role Assignments
Keep a spreadsheet or document tracking:
- User email
- Role assigned
- Date granted
- Reason for access
- Expiration date (if temporary)

### 3. Regular Access Reviews
- Monthly: Review who has access
- Quarterly: Remove inactive users
- Use the weekly log exports to identify inactive users

### 4. Principle of Least Privilege
- Only grant access to users who need it
- Remove access when no longer needed
- Consider creating different roles for different access levels (future enhancement)

## Quick Reference

### Grant Access (Console)
1. IBM Cloud → App ID → Users
2. Find user → Assign roles
3. Select role → Save

### Revoke Access (Console)
1. IBM Cloud → App ID → Users
2. Find user → Remove all roles

### Check Access (Logs)
```powershell
Get-Content "C:\DashboardLogs\weekly-summary-*.txt" | Select-String "UNIQUE USERS"
```

### Emergency Access Removal
If you need to immediately revoke access:
1. Go to App ID Users
2. Find user
3. Click "Delete user" (removes completely)
   OR
4. Remove all roles (keeps user record, blocks access)

## Future Enhancements

Consider implementing:
- **Multiple role levels**: viewer, editor, admin
- **Client-specific roles**: Only see their own data
- **Time-based access**: Automatic expiration
- **Approval workflow**: Request access via form
- **Audit trail**: Track who granted/revoked access

## Support

If you need help with user access:
1. Check App ID documentation: https://cloud.ibm.com/docs/appid
2. Review App ID logs in IBM Cloud
3. Check dashboard logs in `C:\DashboardLogs`
4. Contact IBM Cloud Support for App ID issues