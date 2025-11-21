# Deployment Checklist for Vercel

## Pre-Deployment Checklist

- [ ] All environment variables configured in Vercel Dashboard
- [ ] `SECRET_KEY` generated and set
- [ ] `FLASK_ENV` set to `production`
- [ ] External services configured (Ollama, Pinecone if used)
- [ ] File upload storage configured (S3, Cloudinary, etc. if needed)
- [ ] Database configured (if using external database)

## Quick Deploy Steps

1. **Install Vercel CLI** (if not already installed):
   ```bash
   npm i -g vercel
   ```

2. **Login to Vercel**:
   ```bash
   vercel login
   ```

3. **Deploy**:
   ```bash
   cd company-efficiency-optimizer
   vercel
   ```

4. **Deploy to Production**:
   ```bash
   vercel --prod
   ```

## Environment Variables Required

Set these in Vercel Dashboard → Project → Settings → Environment Variables:

### Critical
- `SECRET_KEY` - Flask secret key (generate: `python -c "import secrets; print(secrets.token_hex(32))"`)
- `FLASK_ENV` - Set to `production`

### Optional but Recommended
- `OLLAMA_BASE_URL` - Your Ollama endpoint
- `PINECONE_API_KEY` - If using Pinecone
- `PINECONE_ENVIRONMENT` - Pinecone environment
- `MAX_FILE_SIZE` - Max upload size (default: 16777216 = 16MB)

## Post-Deployment

1. Test all routes
2. Verify file uploads work (using /tmp)
3. Check session management
4. Monitor logs in Vercel Dashboard
5. Set up custom domain (optional)

## Troubleshooting

- **Build fails**: Check `requirements.txt` for all dependencies
- **Runtime errors**: Check function logs in Vercel Dashboard
- **Session issues**: Verify `SECRET_KEY` is set
- **File upload issues**: Ensure using `/tmp` directory

## Important Notes

- Sessions use cookies (not filesystem) in production
- File uploads stored in `/tmp` (temporary, cleared after execution)
- For persistent storage, use external services (S3, Cloudinary, etc.)
- Function timeout: 60 seconds (configurable in `vercel.json`)


