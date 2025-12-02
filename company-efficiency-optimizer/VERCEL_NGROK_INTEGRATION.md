# Vercel + Ngrok Integration Guide

This document explains how AstraMech is integrated with both Vercel and ngrok for flexible deployment options.

## Project Overview

- **Project ID**: `prj_PML13yysmZWv7xaUkwy0Vh67zKCY`
- **Project Name**: `astramech`
- **Organization**: `arielsanrojs-projects`
- **Vercel Dashboard**: https://vercel.com/arielsanrojs-projects/astramech

## Deployment Architecture

### Local Development + Ngrok
```
Flask App (localhost:5002)
    ↓
Ngrok Tunnel
    ↓
https://astramech.ngrok.app (Public URL)
```

### Vercel Production
```
Git Push → Vercel Build → Serverless Functions → Public URL
```

## Configuration

### 1. Vercel Configuration (`vercel.json`)

The project is configured with:
- **Python Runtime**: Via `@vercel/python`
- **Entry Point**: `api/index.py`
- **Memory**: 1024 MB
- **Max Duration**: 60 seconds
- **Ngrok URL**: Set as environment variable

### 2. Environment Variables

Environment variables are stored in Vercel and can be set via:
- Vercel Dashboard
- Vercel CLI
- The provided `vercel_env_setup.sh` script

#### Required Variables:
- `SECRET_KEY` - Flask secret key
- `FLASK_ENV` - Set to "production"
- `NGROK_URL` - https://astramech.ngrok.app

#### Optional Variables:
- `OLLAMA_API_KEY` - For Ollama integration
- `OLLAMA_BASE_URL` - Ollama endpoint
- `PINECONE_API_KEY` - For vector database
- `MAX_FILE_SIZE` - Maximum upload size
- `ALLOWED_EXTENSIONS` - Allowed file types

## Deployment Options

### Option 1: Deploy to Vercel (Production)

#### Quick Deploy:
```bash
cd /Users/arielsanroj/Astramech/company-efficiency-optimizer
./deploy_to_vercel.sh
```

#### Manual Deploy:
```bash
# Setup environment variables first
./vercel_env_setup.sh

# Deploy to production
vercel --prod
```

### Option 2: Local Development with Ngrok

#### Start Everything:
```bash
# Start Flask + Ngrok together
./start_with_ngrok.sh

# Or separately:
python3 run.py                    # Terminal 1
./start_ngrok_background.sh       # Terminal 2
```

### Option 3: Hybrid Approach

Use ngrok for development/testing and Vercel for production:

```bash
# Development
./start_with_ngrok.sh
# Test at: https://astramech.ngrok.app

# When ready for production
./deploy_to_vercel.sh
# Live at: https://astramech.vercel.app (or custom domain)
```

## Setup Instructions

### Initial Setup

1. **Link Vercel Project** (Already done ✅)
   ```bash
   vercel link --yes --project prj_PML13yysmZWv7xaUkwy0Vh67zKCY
   ```

2. **Configure Environment Variables**
   ```bash
   ./vercel_env_setup.sh
   ```

3. **Configure Ngrok**
   ```bash
   ngrok config add-authtoken 2mtkS18m9XOwl8cFgBxpWHyXgio_4wLygqUmXu7Fqz43DhN2w
   ```

### First Deployment

```bash
# Check status
./check_status.sh

# Deploy to Vercel
./deploy_to_vercel.sh
```

## Access URLs

### Development (Ngrok)
- **Public URL**: https://astramech.ngrok.app
- **Local URL**: http://localhost:5002
- **Inspector**: http://localhost:4040

### Production (Vercel)
- **Production URL**: Will be shown after deployment
- **Dashboard**: https://vercel.com/arielsanrojs-projects/astramech

## Environment-Specific Configuration

### Development (Ngrok)
- Real-time updates (no rebuild needed)
- Full debugging capabilities
- Access to local files and databases
- Request/response inspection via ngrok

### Production (Vercel)
- Serverless functions
- Auto-scaling
- CDN edge caching
- No local file storage (use /tmp or external storage)
- Production-grade security

## Switching Between Environments

### Use Ngrok When:
- Developing new features
- Testing webhook integrations
- Debugging issues locally
- Sharing work-in-progress with team
- Need access to local resources

### Use Vercel When:
- Deploying to production
- Need high availability
- Want auto-scaling
- Require CDN benefits
- Want zero-config deployment

## Webhook Configuration

For external services that need webhooks:

### Development:
```
Webhook URL: https://astramech.ngrok.app/api/webhook
```

### Production:
```
Webhook URL: https://your-vercel-url.vercel.app/api/webhook
```

## Managing Environment Variables

### View Current Variables:
```bash
vercel env ls
```

### Add New Variable:
```bash
vercel env add VARIABLE_NAME production
```

### Remove Variable:
```bash
vercel env rm VARIABLE_NAME production
```

### Pull Variables to Local:
```bash
vercel env pull .env.local
```

## Deployment Workflow

### Recommended Workflow:

1. **Local Development**
   ```bash
   python3 run.py
   # Test at: http://localhost:5002
   ```

2. **Test with Ngrok**
   ```bash
   ./start_ngrok_background.sh
   # Share: https://astramech.ngrok.app
   ```

3. **Commit Changes**
   ```bash
   git add .
   git commit -m "Your changes"
   git push
   ```

4. **Deploy to Vercel**
   ```bash
   vercel --prod
   ```

## Monitoring and Debugging

### Ngrok Debugging:
- Inspector: http://localhost:4040
- Logs: `tail -f ngrok.log`
- Status: `./check_status.sh`

### Vercel Debugging:
- Dashboard: https://vercel.com/arielsanrojs-projects/astramech
- Function Logs: Dashboard → Functions → View Logs
- Real-time logs: `vercel logs`

### Common Issues:

#### 1. Ngrok Domain Not Working
```bash
pkill -f ngrok
./start_ngrok_background.sh
```

#### 2. Vercel Build Fails
- Check `requirements.txt` has all dependencies
- Verify Python version compatibility
- Check build logs in Vercel dashboard

#### 3. Environment Variables Not Loading
```bash
# Re-run setup
./vercel_env_setup.sh

# Or add manually via dashboard
```

## Custom Domain Setup (Vercel)

1. Go to: https://vercel.com/arielsanrojs-projects/astramech/settings/domains
2. Add your custom domain
3. Update DNS records as instructed
4. SSL certificate will be auto-provisioned

## Security Considerations

### Ngrok (Development):
- ⚠️ Publicly accessible - don't expose sensitive data
- Use for development/testing only
- Authtoken stored in config (gitignored)
- Monitor ngrok inspector for unexpected traffic

### Vercel (Production):
- ✅ HTTPS by default
- ✅ Environment variables encrypted
- ✅ Automatic security updates
- ✅ DDoS protection included

## Cost Considerations

### Ngrok:
- Free tier: Limited connections, random URLs
- Pro tier ($8/mo): Reserved domains, more connections
- Current setup uses **Pro** domain: astramech.ngrok.app

### Vercel:
- Hobby (Free): 100GB bandwidth, 100 build minutes
- Pro ($20/mo): 1TB bandwidth, 6000 build minutes
- Check usage: https://vercel.com/arielsanrojs-projects/astramech/settings/usage

## Support & Resources

### Vercel:
- Docs: https://vercel.com/docs
- Status: https://www.vercel-status.com
- Support: https://vercel.com/support

### Ngrok:
- Docs: https://ngrok.com/docs
- Status: https://status.ngrok.com
- Support: https://ngrok.com/support

### AstraMech Project:
- Dashboard: https://vercel.com/arielsanrojs-projects/astramech
- Logs: `vercel logs --follow`
- Functions: Dashboard → Functions tab

## Quick Reference Commands

```bash
# Status checks
./check_status.sh                          # Check all services
vercel ls                                  # List Vercel deployments

# Ngrok
./start_ngrok_background.sh                # Start ngrok
pkill -f ngrok                             # Stop ngrok
tail -f ngrok.log                          # View logs

# Vercel
./deploy_to_vercel.sh                      # Interactive deploy
vercel --prod                              # Deploy to production
vercel logs --follow                       # Follow logs
vercel env ls                              # List environment variables

# Combined
./start_with_ngrok.sh                      # Start Flask + Ngrok
```

## Next Steps

1. ✅ Project linked to Vercel
2. ✅ Ngrok configured and running
3. ⏳ Set environment variables: `./vercel_env_setup.sh`
4. ⏳ Deploy to production: `./deploy_to_vercel.sh`
5. ⏳ Configure custom domain (optional)
6. ⏳ Set up monitoring and alerts

---

**Last Updated**: 2025-11-28  
**Status**: Configured and ready to deploy  
**Project**: astramech (prj_PML13yysmZWv7xaUkwy0Vh67zKCY)
