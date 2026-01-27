# Deployment Guide - Railway + GitHub

This guide covers deploying the CSGB CRM to Railway using GitHub integration.

## Prerequisites

- GitHub account with the `csgb-crm` repository
- Railway account (sign up at [railway.app](https://railway.app))
- Twilio account (for SMS features)

## Step-by-Step Deployment

### 1. Prepare Your Repository

Ensure your code is pushed to GitHub:
```bash
git add .
git commit -m "Initial commit"
git push origin main
```

### 2. Create Railway Project

1. Go to [Railway Dashboard](https://railway.app/dashboard)
2. Click **"New Project"**
3. Select **"Deploy from GitHub repo"**
4. Authorize Railway to access your GitHub account
5. Select the `csgb-crm` repository
6. Railway will automatically detect the project and start deployment

### 3. Add Database Services

#### PostgreSQL

1. In your Railway project, click **"+ New"**
2. Select **"Database"** → **"Add PostgreSQL"**
3. Railway will automatically create a PostgreSQL instance
4. The `DATABASE_URL` environment variable will be automatically set in the PostgreSQL service

**IMPORTANT**: After adding PostgreSQL, you need to link it to your web service:
1. Go to your **web service** (the one running FastAPI)
2. Click on **"Variables"** tab
3. Click **"+ New Variable"** or **"Add Reference"**
4. Select **"Reference Variable from Another Service"**
5. Choose your **PostgreSQL** service
6. Select **`DATABASE_URL`** from the list
7. Save

Alternatively, Railway may auto-share variables if services are in the same project. Check your web service's Variables tab to confirm `DATABASE_URL` is present and points to the PostgreSQL service (not localhost).

#### Redis

1. Click **"+ New"** again
2. Select **"Database"** → **"Add Redis"**
3. Railway will create a Redis instance
4. The `REDIS_URL` environment variable will be automatically set

### 4. Configure Environment Variables

Go to your project → **Variables** tab and add:

```bash
# Twilio (required for SMS features)
TWILIO_ACCOUNT_SID=your_account_sid
TWILIO_AUTH_TOKEN=your_auth_token
TWILIO_PHONE_NUMBER=+1234567890
TWILIO_WEBHOOK_VALIDATE=true

# App Settings
ENVIRONMENT=production
DEBUG=false
```

**Note**: `DATABASE_URL` and `REDIS_URL` are automatically set by Railway when you add the services.

### 5. Run Database Migrations

#### Option A: Using Railway CLI

```bash
# Install Railway CLI
npm install -g @railway/cli

# Login
railway login

# Link to your project
railway link

# Run migrations
railway run alembic upgrade head
```

#### Option B: Using Railway Dashboard

1. Go to your project → **Deployments**
2. Click on the latest deployment
3. Open the **Shell** tab
4. Run: `alembic upgrade head`

### 6. Configure Services

Railway will automatically detect the `Procfile` and create services:

- **Web Service**: FastAPI server (auto-configured)
- **Worker Service**: RQ worker (needs to be enabled)

#### Enable Worker Service

1. In Railway dashboard, you should see two services (or create a second one)
2. For the worker service:
   - Go to **Settings** → **Start Command**
   - Set to: `python -m app.worker`
   - Or Railway will use the `worker` process from Procfile

### 7. Configure Twilio Webhook

1. Get your Railway deployment URL (e.g., `https://your-app.railway.app`)
2. Go to Twilio Console → Phone Numbers → Manage → Active Numbers
3. Select your Twilio phone number
4. Under "Messaging", set the webhook URL to:
   ```
   https://your-app.railway.app/comms/webhooks/twilio/sms
   ```
5. Set HTTP method to **POST**
6. Save

### 8. Verify Deployment

1. Check web service health:
   ```bash
   curl https://your-app.railway.app/health
   ```

2. Check API docs:
   ```
   https://your-app.railway.app/docs
   ```

3. Test lead intake:
   ```bash
   curl -X POST "https://your-app.railway.app/leads/webhook/website?external_id=test123" \
     -H "Content-Type: application/json" \
     -d '{"name": "Test User", "email": "test@example.com", "phone": "+441234567890"}'
   ```

## Monitoring

### View Logs

- **Web Service**: Railway Dashboard → Your Service → **Deployments** → Click deployment → **Logs**
- **Worker Service**: Same process for worker service

### Check Worker Status

The RQ worker processes background jobs. Check logs to ensure it's running:

```bash
railway logs --service worker
```

## Troubleshooting

### Database Connection Issues

- Verify `DATABASE_URL` is set correctly
- Check PostgreSQL service is running
- Ensure migrations have run: `railway run alembic upgrade head`

### Redis Connection Issues

- Verify `REDIS_URL` is set correctly
- Check Redis service is running
- Worker requires Redis to be accessible

### Worker Not Processing Jobs

- Ensure worker service is enabled and running
- Check Redis connection
- Verify `REDIS_URL` environment variable

### Twilio Webhook Not Working

- Verify webhook URL is correct in Twilio console
- Check `TWILIO_WEBHOOK_VALIDATE` setting
- Review webhook logs in Railway

## Environment Variables Reference

| Variable | Required | Description |
|----------|----------|-------------|
| `DATABASE_URL` | Yes | Auto-set by Railway PostgreSQL service |
| `REDIS_URL` | Yes | Auto-set by Railway Redis service |
| `TWILIO_ACCOUNT_SID` | Yes* | Twilio account SID (*required for SMS) |
| `TWILIO_AUTH_TOKEN` | Yes* | Twilio auth token (*required for SMS) |
| `TWILIO_PHONE_NUMBER` | Yes* | Your Twilio phone number (*required for SMS) |
| `TWILIO_WEBHOOK_VALIDATE` | No | Validate Twilio webhook signatures (default: true) |
| `ENVIRONMENT` | No | Environment name (default: development) |
| `DEBUG` | No | Debug mode (default: true) |

## Continuous Deployment

Railway automatically deploys on every push to your main branch. To disable:

1. Go to project **Settings**
2. Under **"Source"**, configure branch deployments
3. Or use Railway CLI: `railway unlink` to disconnect

## Scaling

- **Web Service**: Railway auto-scales based on traffic
- **Worker Service**: Add multiple worker instances if needed
- **Database**: Railway PostgreSQL scales automatically
- **Redis**: Railway Redis scales automatically

## Cost Optimization

- Use Railway's free tier for development
- Monitor usage in Railway dashboard
- Consider pausing services when not in use (development only)
