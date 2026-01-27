# CSGB CRM - Modular Monolith MVP

A FastAPI-based CRM system for lead management, customer tracking, and automated communication.

**Deployment**: Ready for Railway + GitHub. See [DEPLOYMENT.md](./DEPLOYMENT.md) for detailed deployment instructions.

## Features

- **Lead Intake**: Webhook and manual entry with idempotency
- **Early Merge**: Automatic customer matching by phone/email
- **Lead Inbox**: View leads with status NEW or NEEDS_INFO
- **Lead Detail**: View lead with associated customer and timeline
- **Timeline**: ContactEvent logs all system events and SMS communications
- **Qualification**: Move leads to QUALIFIED and create Opportunity stubs
- **Automation**: Redis + RQ for SMS follow-ups on missing information
- **Twilio Integration**: Outbound and inbound SMS with signature validation

## Tech Stack

- FastAPI
- SQLAlchemy 2.0 + Alembic
- PostgreSQL
- Redis + RQ
- Twilio Python SDK
- Pydantic v2 + pydantic-settings

## Setup

### Prerequisites

- Python 3.11+
- Node.js 18+ (for frontend)
- PostgreSQL
- Redis

### Installation

1. Clone the repository:
```bash
cd csgb-crm
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Create `.env` file from `.env.example`:
```bash
cp .env.example .env
```

5. Update `.env` with your configuration:
   - Database URL
   - Redis URL
   - Twilio credentials (if using SMS features)

6. Build the frontend:
```bash
cd frontend
npm install
npm run build
cd ..
```

7. Run database migrations:
```bash
alembic upgrade head
```

### Running Locally

1. Start PostgreSQL and Redis (using Docker Compose if available):
```bash
docker-compose up -d
```

Or start them separately:
- PostgreSQL on `localhost:5432`
- Redis on `localhost:6379`

2. Start the FastAPI server:
```bash
uvicorn app.main:app --reload
```

3. Start the RQ worker (in a separate terminal):
```bash
python -m app.worker
```

   Or using rq directly:
```bash
rq worker default --url $REDIS_URL
```

The application will be available at:
- **Frontend UI**: `http://localhost:8000`
- **API**: `http://localhost:8000/api/`
- **API Documentation**: `http://localhost:8000/docs`

## API Endpoints

### Lead Management

#### Webhook Lead Intake
```bash
curl -X POST "http://localhost:8000/leads/webhook/website?external_id=12345" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "John Doe",
    "email": "john@example.com",
    "phone": "+441234567890",
    "postcode": "SW1A 1AA",
    "product_interest": "Solar panels",
    "timeframe": "Within 3 months"
  }'
```

#### Create Lead Manually
```bash
curl -X POST "http://localhost:8000/leads/" \
  -H "Content-Type: application/json" \
  -d '{
    "source": "manual",
    "name": "Jane Smith",
    "email": "jane@example.com",
    "phone": "+441234567891",
    "raw_payload": {
      "postcode": "SW1A 1AB",
      "product_interest": "Heat pumps",
      "timeframe": "Within 6 months"
    }
  }'
```

#### Get Lead Inbox
```bash
curl "http://localhost:8000/leads/inbox?limit=50&offset=0"
```

#### Get Lead Detail
```bash
curl "http://localhost:8000/leads/{lead_id}"
```

#### Request Info (Triggers Automation)
```bash
curl -X POST "http://localhost:8000/leads/{lead_id}/request-info"
```

#### Qualify Lead
```bash
curl -X POST "http://localhost:8000/leads/{lead_id}/qualify"
```

### Communications

#### Send SMS
```bash
curl -X POST "http://localhost:8000/comms/sms/send" \
  -H "Content-Type: application/json" \
  -d '{
    "lead_id": "lead-uuid-here",
    "message": "Hello, this is a test message"
  }'
```

#### Twilio SMS Webhook (Inbound)
Configure Twilio webhook URL to: `https://your-domain.com/comms/webhooks/twilio/sms`

The webhook accepts form-encoded data from Twilio and:
- Validates signature (if `TWILIO_WEBHOOK_VALIDATE=true`)
- Normalizes phone number to E.164
- Finds or creates customer
- Creates lead if needed
- Attempts to extract postcode from message body
- Logs contact event

## Database Schema

### Tables

1. **customers**: Customer records with phone/email matching
2. **leads**: Lead records with status tracking
3. **contact_events**: Timeline of all communications and system events
4. **opportunities**: Sales opportunities linked to customers
5. **idempotency_keys**: Webhook deduplication

## Automation

The system uses Redis + RQ for background job processing:

- **Qualification Chase**: Automatically sends SMS when lead status is set to NEEDS_INFO
- **Follow-up**: Sends follow-up SMS 4 hours after initial request

Jobs are processed by the RQ worker (`python -m app.worker`).

## Deployment to Railway

### Option 1: Railway GitHub Integration (Recommended)

1. **Connect GitHub Repository**:
   - Go to [Railway](https://railway.app)
   - Click "New Project" → "Deploy from GitHub repo"
   - Select your `csgb-crm` repository
   - Railway will automatically detect the project

2. **Add Services**:
   - Add a **PostgreSQL** service (Railway will auto-generate `DATABASE_URL`)
   - Add a **Redis** service (Railway will auto-generate `REDIS_URL`)

3. **Configure Environment Variables**:
   - Go to your project settings → Variables
   - Add variables from `.env.example`:
     - `TWILIO_ACCOUNT_SID`
     - `TWILIO_AUTH_TOKEN`
     - `TWILIO_PHONE_NUMBER`
     - `TWILIO_WEBHOOK_VALIDATE=true`
     - `ENVIRONMENT=production`
     - `DEBUG=false`

4. **Run Migrations**:
   - Railway will automatically run `alembic upgrade head` on first deploy
   - Or use Railway CLI: `railway run alembic upgrade head`

5. **Deploy**:
   - Railway will automatically deploy on every push to `main`/`master`
   - The `Procfile` defines two processes:
     - `web`: FastAPI server (auto-started)
     - `worker`: RQ worker (must be enabled separately)

6. **Enable Worker Process**:
   - In Railway dashboard, go to your service
   - Add a new service from the same repo
   - Set the start command to: `python -m app.worker`
   - Or use the Procfile worker process

### Option 2: Railway CLI

1. Install Railway CLI: `npm install -g @railway/cli`
2. Login: `railway login`
3. Initialize: `railway init`
4. Link to project: `railway link`
5. Add PostgreSQL and Redis services via dashboard
6. Set environment variables: `railway variables set KEY=value`
7. Deploy: `railway up`

### Railway Configuration

The `Procfile` defines:
- `web`: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
- `worker`: `python -m app.worker`

**Important**: Make sure to enable both the web and worker processes in Railway. The worker process is required for background job processing (SMS automation).

## Development

### Running Migrations

Create a new migration:
```bash
alembic revision --autogenerate -m "Description"
```

Apply migrations:
```bash
alembic upgrade head
```

Rollback:
```bash
alembic downgrade -1
```

### Project Structure

```
csgb-crm/
  app/
    main.py                 # FastAPI app
    worker.py               # RQ worker
    static/                 # Frontend build output (generated)
    core/
      config.py            # Settings
      db.py                # Database session
      idempotency.py       # Webhook deduplication
      utils.py             # Phone normalization, etc.
    modules/
      customers/           # Customer management
      leads/               # Lead management
      comms/               # Communications (SMS)
      automation/          # Background jobs
      opportunities/       # Sales opportunities
  frontend/                 # React frontend
    src/                   # Source files
    package.json           # Node dependencies
  alembic/                 # Database migrations
  requirements.txt
  Procfile                 # Railway deployment
  .env.example
```

## Notes

- Phone numbers are normalized to E.164 format
- UK postcode extraction from SMS uses regex patterns
- Webhook idempotency uses external_id or payload hash
- Lead status: NEW → NEEDS_INFO → QUALIFIED
- Missing fields: name, phone_or_email, postcode, product_interest, timeframe
