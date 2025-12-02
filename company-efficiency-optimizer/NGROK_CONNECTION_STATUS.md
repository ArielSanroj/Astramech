# Ngrok Connection Status ✅

## Connection Details

- **Public URL**: https://astramech.ngrok.app
- **Local URL**: http://localhost:5002
- **Inspector Dashboard**: http://localhost:4040
- **Status**: ✅ **CONNECTED**

## Configuration Summary

| Item | Status | Details |
|------|--------|---------|
| Ngrok Domain | ✅ Connected | astramech.ngrok.app |
| Authtoken | ✅ Configured | Hidden for security |
| Local Port | ✅ Running | 5002 |
| Flask App | ✅ Running | Multiple processes detected |
| Tunnel Protocol | ✅ HTTPS | Secure connection |

## Available Scripts

### Start/Stop Scripts

```bash
# Check status of all services
./check_status.sh

# Start ngrok in background (Flask already running)
./start_ngrok_background.sh

# Start ngrok in foreground (interactive mode)
./start_ngrok.sh

# Start both Flask and ngrok together
./start_with_ngrok.sh

# Stop ngrok
pkill -f ngrok
```

### View Logs

```bash
# View ngrok logs
tail -f ngrok.log

# View Flask logs (if started with start_with_ngrok.sh)
tail -f flask.log
```

## Testing Your Connection

### 1. Basic Connection Test

```bash
# Test from command line
curl https://astramech.ngrok.app/

# Should return your Flask app's homepage HTML
```

### 2. Check Available Endpoints

Your Astramech application is now accessible at these URLs:

- **Homepage**: https://astramech.ngrok.app/
- **Questionnaire**: https://astramech.ngrok.app/questionnaire
- **Upload**: https://astramech.ngrok.app/upload
- **Results**: https://astramech.ngrok.app/results
- **SuperVincent Agent**: https://astramech.ngrok.app/agents/supervincent
- **SuperVincent Status**: https://astramech.ngrok.app/agents/supervincent/status
- **Clio Alpha Agent**: https://astramech.ngrok.app/agents/clioalpha
- **Clio Status**: https://astramech.ngrok.app/agents/clioalpha/status
- **API Endpoints**: https://astramech.ngrok.app/api/*

### 3. Inspector Dashboard

Visit http://localhost:4040 to:
- See all incoming requests in real-time
- Inspect request/response headers and bodies
- Replay requests for testing
- Debug webhook integrations

## Security Considerations

⚠️ **Important Security Notes:**

1. **Authtoken Protection**: Your ngrok authtoken is stored in:
   - `ngrok_config.yml` (added to .gitignore)
   - `~/.ngrok2/ngrok.yml` (system config)

2. **Public Access**: Your application is now **publicly accessible** at https://astramech.ngrok.app
   - Anyone with the URL can access it
   - Consider adding authentication for production use
   - Monitor the inspector dashboard for unexpected traffic

3. **Sensitive Data**: Ensure no sensitive data is logged or exposed in:
   - Error messages
   - Debug output
   - Flask session data

## Troubleshooting

### Tunnel Shows Different Domain

If the tunnel shows a different domain (like mommyshops.ngrok.app):

```bash
# Stop all ngrok processes
pkill -f ngrok

# Start with correct domain
./start_ngrok_background.sh
```

### Port 5002 Already in Use

```bash
# Find processes using port 5002
lsof -ti:5002

# Stop specific process
kill <PID>

# Or stop all
lsof -ti:5002 | xargs kill
```

### Cannot Access Public URL

1. Check Flask is running: `lsof -ti:5002`
2. Check ngrok is running: `lsof -ti:4040`
3. Verify domain in inspector: http://localhost:4040
4. Check ngrok logs: `cat ngrok.log`

### Authtoken Error

```bash
# Reconfigure authtoken
ngrok config add-authtoken 2mtkS18m9XOwl8cFgBxpWHyXgio_4wLygqUmXu7Fqz43DhN2w
```

## Integration Examples

### Webhook URL for External Services

If you need to receive webhooks from external services, use:

```
https://astramech.ngrok.app/api/webhook
```

### API Calls from External Systems

```bash
# Example: Get SuperVincent status
curl https://astramech.ngrok.app/agents/supervincent/status

# Example: POST to Clio analyze
curl -X POST https://astramech.ngrok.app/agents/clioalpha/analyze \
  -H "Content-Type: application/json" \
  -d '{"members": {...}}'
```

### Mobile/Remote Testing

Access your local development from:
- Other devices on different networks
- Mobile phones
- Tablets
- Remote team members

Just share the URL: https://astramech.ngrok.app

## Next Steps

1. **Test your application**: Visit https://astramech.ngrok.app in a browser
2. **Monitor traffic**: Keep http://localhost:4040 open in another tab
3. **Set up webhooks**: Use the public URL for any webhook integrations
4. **Share with team**: Send the URL to team members for testing

## Stopping Services

### Stop Everything

```bash
# Stop ngrok
pkill -f ngrok

# Stop Flask
lsof -ti:5002 | xargs kill

# Or just restart your terminal session
```

### Keep Running

To keep services running even after closing terminal:

```bash
# Ngrok is already running in background via nohup
# Flask can be started similarly:
nohup python3 run.py > flask.log 2>&1 &
```

## Production Notes

⚠️ **This is a development setup**

For production deployment, consider:

1. **Vercel** (already configured in your project)
2. **Heroku** with proper domain
3. **AWS/GCP/Azure** with load balancer
4. **Digital Ocean** App Platform
5. **Ngrok Pro** for reserved domains and better limits

## Support

- **Ngrok Docs**: https://ngrok.com/docs
- **Ngrok Status**: https://status.ngrok.com
- **Flask Logs**: Check `flask.log` or console output
- **Application Logs**: Check `logs/` directory

---

**Last Updated**: 2025-11-28  
**Connection Status**: ✅ Active  
**Public URL**: https://astramech.ngrok.app
