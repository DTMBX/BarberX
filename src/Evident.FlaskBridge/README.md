# Evident Flask Bridge

This directory contains the integration layer between the existing Python Flask
app and the new .NET infrastructure.

## Current Flask App

- Location: `C:\web-dev\github-repos\Evident.info\app.py`
- Run with: `python app.py` or `flask run`

## Integration Strategy

1. Keep existing Flask app for BWC analysis features
2. Use .NET Web API for new scalable features (bookings, payments, user
   management)
3. Share data via REST APIs or shared database

## Running Both Apps

- Flask (Python): Port 5000
- .NET API: Port 5001

See: `/docs/api/INTEGRATION.md` for API contracts
