# Backend configuration

## Secrets and auth keys

Create a local env file before running API or Modal jobs:

```bash
cp backend/.env.example backend/.env
```

Set at least:

- `GEMINI_API_KEY`

Optional:

- `GEMINI_MODEL_ID`
- `CORS_ALLOWED_ORIGINS` (comma-separated frontend origins)

`backend/.env` is gitignored.
