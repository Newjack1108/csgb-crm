# CSGB CRM Frontend

React frontend for the CSGB CRM application.

## Development

```bash
# Install dependencies
npm install

# Start development server
npm run dev
```

The dev server will proxy API requests to `http://localhost:8000`.

## Building for Production

```bash
npm run build
```

This will build the frontend and output to `../app/static/` which FastAPI will serve.

## Features

- **Lead Inbox**: View all leads with status NEW or NEEDS_INFO
- **Lead Detail**: View lead information, customer details, and timeline
- **Create Lead**: Manual lead entry form
- **Qualify Lead**: Move leads to qualified status
- **Request Info**: Trigger automation to request missing information
- **Send SMS**: Send SMS messages to leads

## API Integration

The frontend uses `/api` prefix for all API calls. FastAPI serves the API at `/api/*` routes.
