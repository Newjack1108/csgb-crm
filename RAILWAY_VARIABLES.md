# Railway Environment Variables Guide

This document lists all environment variables needed for the CSGB CRM on Railway.

## Required Variables

### Database & Redis (Auto-Set by Railway)

These are **automatically created** when you add the services, but you need to **link them** to your web service:

| Variable | Source | How to Set |
|----------|--------|------------|
| `DATABASE_URL` | PostgreSQL Service | 1. Add PostgreSQL service<br>2. In web service → Variables → Add Reference → Select PostgreSQL service → Select `DATABASE_URL` |
| `REDIS_URL` | Redis Service | 1. Add Redis service<br>2. In web service → Variables → Add Reference → Select Redis service → Select `REDIS_URL` |

### Twilio (Required for SMS Features)

| Variable | Required | Example Value | Description |
|----------|----------|---------------|-------------|
| `TWILIO_ACCOUNT_SID` | Yes* | `ACxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx` | Your Twilio Account SID (from Twilio Console) |
| `TWILIO_AUTH_TOKEN` | Yes* | `your_auth_token_here` | Your Twilio Auth Token (from Twilio Console) |
| `TWILIO_PHONE_NUMBER` | Yes* | `+1234567890` | Your Twilio phone number in E.164 format |
| `TWILIO_WEBHOOK_VALIDATE` | No | `true` or `false` | Validate Twilio webhook signatures (default: `true`) |

*Required only if you're using SMS features. The app will start without them, but SMS functionality won't work.

### Application Settings (Optional)

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `ENVIRONMENT` | No | `development` | Environment name (set to `production` for production) |
| `DEBUG` | No | `true` | Debug mode (set to `false` for production) |
| `PORT` | No | `8000` | Port for the web server (Railway sets this automatically) |

## How to Set Variables in Railway

### Method 1: Project-Level Variables (Recommended)

1. Go to your Railway project dashboard
2. Click on **"Variables"** tab (at the project level, not service level)
3. Click **"+ New Variable"**
4. Add each variable:
   - **Name**: e.g., `TWILIO_ACCOUNT_SID`
   - **Value**: Your actual value
   - **Scope**: Select "All Services" or specific service
5. Click **"Add"**

### Method 2: Service-Level Variables

1. Go to your **web service** (the FastAPI one)
2. Click on **"Variables"** tab
3. Click **"+ New Variable"**
4. Add variables as above

### Method 3: Reference from Another Service (For DATABASE_URL and REDIS_URL)

1. Go to your **web service**
2. Click on **"Variables"** tab
3. Click **"+ New Variable"** or **"Add Reference"**
4. Select **"Reference Variable from Another Service"**
5. Choose the service (PostgreSQL or Redis)
6. Select the variable (`DATABASE_URL` or `REDIS_URL`)
7. Save

## Worker Service Variables

The **worker service** (RQ worker for background jobs) needs the same variables as the web service:

### Required for Worker:
- [ ] `DATABASE_URL` (from PostgreSQL service) - **Required** - Worker needs database access to process jobs
- [ ] `REDIS_URL` (from Redis service) - **Required** - Worker connects to Redis to get jobs from queue

### Required for Worker SMS Jobs (if using SMS automation):
- [ ] `TWILIO_ACCOUNT_SID` - **Required** - Worker sends SMS via Twilio
- [ ] `TWILIO_AUTH_TOKEN` - **Required** - Worker sends SMS via Twilio
- [ ] `TWILIO_PHONE_NUMBER` - **Required** - Worker sends SMS via Twilio
- [ ] `TWILIO_WEBHOOK_VALIDATE` - Optional (default: `true`)

### Optional for Worker:
- [ ] `ENVIRONMENT=production`
- [ ] `DEBUG=false`

**Note**: The worker service should have the same variables as the web service. You can:
1. Set variables at **project level** with scope "All Services" (recommended)
2. Or copy the same variables to the worker service

## Complete Variable Checklist

### For Basic Setup (Without SMS):
**Web Service:**
- [ ] `DATABASE_URL` (from PostgreSQL service)
- [ ] `REDIS_URL` (from Redis service)
- [ ] `ENVIRONMENT=production`
- [ ] `DEBUG=false`

**Worker Service:**
- [ ] `DATABASE_URL` (from PostgreSQL service)
- [ ] `REDIS_URL` (from Redis service)
- [ ] `ENVIRONMENT=production`
- [ ] `DEBUG=false`

### For Full Setup (With SMS):
**Web Service:**
- [ ] `DATABASE_URL` (from PostgreSQL service)
- [ ] `REDIS_URL` (from Redis service)
- [ ] `TWILIO_ACCOUNT_SID`
- [ ] `TWILIO_AUTH_TOKEN`
- [ ] `TWILIO_PHONE_NUMBER`
- [ ] `TWILIO_WEBHOOK_VALIDATE=true`
- [ ] `ENVIRONMENT=production`
- [ ] `DEBUG=false`

**Worker Service:**
- [ ] `DATABASE_URL` (from PostgreSQL service)
- [ ] `REDIS_URL` (from Redis service)
- [ ] `TWILIO_ACCOUNT_SID`
- [ ] `TWILIO_AUTH_TOKEN`
- [ ] `TWILIO_PHONE_NUMBER`
- [ ] `TWILIO_WEBHOOK_VALIDATE=true`
- [ ] `ENVIRONMENT=production`
- [ ] `DEBUG=false`

## Where to Find Twilio Credentials

1. Go to [Twilio Console](https://console.twilio.com/)
2. Your **Account SID** and **Auth Token** are on the dashboard homepage
3. For **Phone Number**:
   - Go to Phone Numbers → Manage → Active Numbers
   - Select your number
   - Copy the number in E.164 format (e.g., `+1234567890`)

## Verification

After setting variables, verify they're loaded:

1. Check Railway logs - the startup script will show:
   ```
   Database URL: ***@your-db-host:5432/your-db-name
   ```

2. If you see `localhost` in the database URL, the `DATABASE_URL` reference isn't set correctly.

3. Test the API:
   ```bash
   curl https://your-app.railway.app/health
   ```

## Troubleshooting

### Variables Not Appearing
- Make sure you're setting them at the correct level (project vs service)
- Check that service references are properly linked
- Redeploy after adding variables

### DATABASE_URL Still Shows localhost
- Verify you've added a **reference** to the PostgreSQL service's `DATABASE_URL`
- Don't create a new variable with the same name - use "Reference Variable from Another Service"
- Check that both services are in the same project

### SMS Not Working
- Verify all three Twilio variables are set
- Check that `TWILIO_PHONE_NUMBER` is in E.164 format (starts with `+`)
- Verify credentials in Twilio Console
