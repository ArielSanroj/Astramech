# Vercel Deployment Guide

This guide explains how to deploy the AstraMech Flask application to Vercel.

## Prerequisites

1. Vercel account (sign up at https://vercel.com)
2. Vercel CLI installed: `npm i -g vercel`
3. Git repository (GitHub, GitLab, or Bitbucket)

## Quick Deploy

### Option 1: Deploy via Vercel Dashboard

1. Go to https://vercel.com/new
2. Import your Git repository
3. Configure project:
   - **Framework Preset**: Other
   - **Root Directory**: `company-efficiency-optimizer`
   - **Build Command**: (leave empty)
   - **Output Directory**: (leave empty)
4. Add environment variables (see below)
5. Click "Deploy"

### Option 2: Deploy via CLI

```bash
cd company-efficiency-optimizer
vercel
```

Follow the prompts, then:
```bash
vercel --prod
```

## Environment Variables

Set these in Vercel Dashboard → Project → Settings → Environment Variables:

### Required

- `SECRET_KEY`: Flask secret key (generate with: `python -c "import secrets; print(secrets.token_hex(32))"`)
- `FLASK_ENV`: Set to `production`

### Optional (but recommended)

- `OLLAMA_BASE_URL`: Your Ollama API endpoint (if using external service)
- `PINECONE_API_KEY`: Pinecone API key (if using Pinecone)
- `PINECONE_ENVIRONMENT`: Pinecone environment
- `MAX_FILE_SIZE`: Maximum upload size in bytes (default: 16777216 = 16MB)
- `ALLOWED_EXTENSIONS`: Comma-separated list (default: `pdf,xlsx,xls,csv`)

### Security (Production)

- `SESSION_COOKIE_SECURE`: `true` (for HTTPS)
- `SESSION_COOKIE_HTTPONLY`: `true`
- `SESSION_COOKIE_SAMESITE`: `Strict`

## Project Structure

```
company-efficiency-optimizer/
├── api/
│   └── index.py          # Vercel serverless handler
├── app/                   # Flask application
├── templates/             # HTML templates
├── vercel.json           # Vercel configuration
├── requirements.txt      # Python dependencies
└── .vercelignore        # Files to exclude
```

## Important Notes

### Sessions

- Vercel uses **cookie-based sessions** (not filesystem)
- Sessions are stored in encrypted cookies
- No persistent file storage available

### File Uploads

- Uploads are stored in `/tmp` (temporary, cleared after function execution)
- For persistent storage, use:
  - AWS S3
  - Google Cloud Storage
  - Cloudinary
  - Vercel Blob Storage

### Limitations

- **Function timeout**: 60 seconds (configurable in `vercel.json`)
- **Memory**: 1024 MB (configurable)
- **No persistent filesystem**: Use external storage for uploads
- **Cold starts**: First request may be slower

## Troubleshooting

### Build Errors

1. Check `requirements.txt` for all dependencies
2. Ensure Python version is compatible (Vercel uses Python 3.9+)
3. Check build logs in Vercel Dashboard

### Runtime Errors

1. Check function logs in Vercel Dashboard
2. Verify environment variables are set correctly
3. Ensure all file paths use `/tmp` for temporary files

### Session Issues

- Sessions use cookies (not filesystem)
- Ensure `SECRET_KEY` is set
- Check cookie settings in production config

## Custom Domain

1. Go to Project → Settings → Domains
2. Add your custom domain
3. Update DNS records as instructed
4. SSL is automatically provisioned

## Monitoring

- View logs: Vercel Dashboard → Project → Functions
- Monitor performance: Vercel Dashboard → Analytics
- Set up alerts: Vercel Dashboard → Settings → Notifications

## Support

- Vercel Docs: https://vercel.com/docs
- Python Runtime: https://vercel.com/docs/concepts/functions/serverless-functions/runtimes/python
- Flask on Vercel: https://vercel.com/guides/deploying-flask-with-vercel


