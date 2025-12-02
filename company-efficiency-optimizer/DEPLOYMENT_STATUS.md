# AstraMech Deployment Status

## ✅ Connected and Configured

### Project Information
- **Project ID**: `prj_PML13yysmZWv7xaUkwy0Vh67zKCY`
- **Project Name**: `astramech`
- **Organization**: `arielsanrojs-projects`
- **Status**: Linked and ready to deploy

### Current Setup

#### 1. Vercel Configuration ✅
- [x] Project linked successfully
- [x] `vercel.json` configured with ngrok URL
- [x] CORS headers enabled for API endpoints
- [x] Python runtime configured
- [x] Serverless functions set up (60s timeout, 1024MB memory)
- [ ] Environment variables to be set (run `./vercel_env_setup.sh`)
- [ ] Production deployment pending

#### 2. Ngrok Configuration ✅
- [x] Authtoken configured
- [x] Domain: `astramech.ngrok.app`
- [x] Tunnel active and running
- [x] Connected to Flask app on port 5002
- [x] Inspector available at http://localhost:4040

### URLs

#### Development (Active)
- **Ngrok Public**: https://astramech.ngrok.app
- **Local Flask**: http://localhost:5002
- **Ngrok Inspector**: http://localhost:4040

#### Production (Pending First Deploy)
- **Vercel Dashboard**: https://vercel.com/arielsanrojs-projects/astramech
- **Production URL**: Will be assigned after first deployment

### Quick Actions

#### Check Status
```bash
cd /Users/arielsanroj/Astramech/company-efficiency-optimizer
./check_status.sh
```

#### Deploy to Vercel
```bash
# Option 1: Interactive deployment
./deploy_to_vercel.sh

# Option 2: Direct deployment
vercel --prod
```

#### Manage Ngrok
```bash
# Start ngrok (if not running)
./start_ngrok_background.sh

# Stop ngrok
pkill -f ngrok

# View logs
tail -f ngrok.log
```

#### Set Up Environment Variables
```bash
# Configure all environment variables for Vercel
./vercel_env_setup.sh
```

### Available Scripts

| Script | Purpose |
|--------|---------|
| `check_status.sh` | Check status of Flask and ngrok |
| `start_ngrok.sh` | Start ngrok (interactive) |
| `start_ngrok_background.sh` | Start ngrok in background |
| `start_with_ngrok.sh` | Start Flask + ngrok together |
| `vercel_env_setup.sh` | Configure Vercel environment variables |
| `deploy_to_vercel.sh` | Interactive Vercel deployment |

### File Structure

```
company-efficiency-optimizer/
├── .vercel/
│   └── project.json          ✅ Project linked
├── api/
│   └── index.py              ✅ Vercel entry point
├── app/                      ✅ Flask application
├── templates/                ✅ HTML templates
├── vercel.json              ✅ Updated with ngrok URL
├── ngrok_config.yml         ✅ Ngrok configuration
├── requirements.txt         ✅ Python dependencies
├── .vercelignore           ✅ Deployment exclusions
├── .gitignore              ✅ Updated for ngrok files
└── *.sh                    ✅ Deployment scripts
```

### Environment Variables Required

The following environment variables need to be set in Vercel (use `./vercel_env_setup.sh`):

#### Essential
- `SECRET_KEY` - Flask session security
- `FLASK_ENV` - Set to "production"
- `NGROK_URL` - https://astramech.ngrok.app

#### API Keys
- `OLLAMA_API_KEY` - For Ollama integration
- `PINECONE_API_KEY` - For vector database
- `OLLAMA_BASE_URL` - Ollama endpoint
- `OLLAMA_MODEL` - Model name

#### Optional
- `MAX_FILE_SIZE` - Maximum upload size (default: 16777216)
- `ALLOWED_EXTENSIONS` - File types (default: pdf,xlsx,xls,csv)
- `LOG_LEVEL` - Logging level (default: INFO)
- `PROJECT_NAME` - Project name (default: AstraMech)

### Next Steps

1. **Set Environment Variables** (5 minutes)
   ```bash
   ./vercel_env_setup.sh
   ```

2. **Test Ngrok Connection** (1 minute)
   ```bash
   ./check_status.sh
   curl https://astramech.ngrok.app
   ```

3. **Deploy to Vercel** (5 minutes)
   ```bash
   ./deploy_to_vercel.sh
   ```

4. **Verify Deployment** (2 minutes)
   - Visit Vercel URL (shown after deployment)
   - Check Vercel dashboard for logs
   - Test all endpoints

5. **Optional: Custom Domain**
   - Configure in Vercel dashboard
   - Update DNS records
   - SSL auto-provisioned

### Monitoring

#### Ngrok (Development)
- **Inspector**: http://localhost:4040
- **Logs**: `tail -f ngrok.log`
- **Status**: `./check_status.sh`

#### Vercel (Production)
- **Dashboard**: https://vercel.com/arielsanrojs-projects/astramech
- **Logs**: `vercel logs --follow`
- **Functions**: Dashboard → Functions tab
- **Analytics**: Dashboard → Analytics tab

### Troubleshooting

#### Ngrok Issues
```bash
# Restart ngrok
pkill -f ngrok
./start_ngrok_background.sh

# Check logs
cat ngrok.log

# Verify tunnel
curl http://localhost:4040/api/tunnels | python3 -m json.tool
```

#### Vercel Issues
```bash
# Check deployment status
vercel ls

# View logs
vercel logs

# Re-link project if needed
vercel link --yes --project prj_PML13yysmZWv7xaUkwy0Vh67zKCY
```

#### Flask Issues
```bash
# Check if running
lsof -ti:5002

# Restart
lsof -ti:5002 | xargs kill
python3 run.py
```

### Deployment History

| Date | Action | Status |
|------|--------|--------|
| 2025-11-28 | Project linked to Vercel | ✅ Complete |
| 2025-11-28 | Ngrok configured | ✅ Active |
| 2025-11-28 | `vercel.json` updated | ✅ Complete |
| 2025-11-28 | Deployment scripts created | ✅ Complete |
| Pending | Environment variables setup | ⏳ Ready |
| Pending | First production deployment | ⏳ Ready |

### Support Resources

- **Vercel Docs**: https://vercel.com/docs
- **Ngrok Docs**: https://ngrok.com/docs
- **Project Dashboard**: https://vercel.com/arielsanrojs-projects/astramech
- **Deployment Guide**: See `VERCEL_NGROK_INTEGRATION.md`
- **Ngrok Setup**: See `NGROK_SETUP.md`

### Security Notes

- ✅ Ngrok authtoken added to `.gitignore`
- ✅ `ngrok_config.yml` excluded from git
- ✅ Environment variables secured in Vercel
- ✅ CORS headers configured
- ⚠️ Remember to rotate tokens if exposed

### Performance

#### Current Configuration
- **Memory**: 1024 MB
- **Timeout**: 60 seconds
- **Region**: Auto (US-East by default)
- **Runtime**: Python 3.9+

#### Optimization Options
- Increase memory if needed (up to 3008 MB)
- Extend timeout if processing takes longer
- Configure specific edge regions
- Enable edge caching for static assets

---

**Status**: ✅ Configured and ready to deploy  
**Last Updated**: 2025-11-28  
**Action Required**: Run `./vercel_env_setup.sh` then `./deploy_to_vercel.sh`
