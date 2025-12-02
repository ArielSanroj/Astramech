# Ngrok Setup for Astramech

This guide explains how to connect your Astramech application to the ngrok endpoint `astramech.ngrok.app`.

## Prerequisites

1. **Install ngrok** if not already installed:
   ```bash
   # macOS (using Homebrew)
   brew install ngrok
   
   # Or download directly from https://ngrok.com/download
   ```

2. **Verify ngrok installation**:
   ```bash
   ngrok version
   ```

## Quick Start

### Option 1: Start Everything Together (Recommended)

This starts both the Flask app and ngrok tunnel:

```bash
chmod +x start_with_ngrok.sh
./start_with_ngrok.sh
```

### Option 2: Start Separately

If you want to run the Flask app and ngrok separately:

1. **Start the Flask application**:
   ```bash
   python3 run.py
   ```

2. **In another terminal, start ngrok**:
   ```bash
   chmod +x start_ngrok.sh
   ./start_ngrok.sh
   ```

### Option 3: Use ngrok config file

Use the configuration file directly:

```bash
# Configure authtoken first
ngrok config add-authtoken 2mtkS18m9XOwl8cFgBxpWHyXgio_4wLygqUmXu7Fqz43DhN2w

# Start using config file
ngrok start --config=ngrok_config.yml astramech
```

## Configuration Details

- **Custom Domain**: astramech.ngrok.app
- **Local Port**: 5002
- **Protocol**: HTTP
- **Authtoken**: Configured in `ngrok_config.yml`

## Accessing Your Application

Once ngrok is running:

1. **Public URL**: https://astramech.ngrok.app
2. **Local URL**: http://localhost:5002
3. **Ngrok Inspector**: http://localhost:4040

The ngrok inspector allows you to:
- See all HTTP requests/responses
- Replay requests
- Debug webhook integrations

## Troubleshooting

### Port Already in Use

If port 5002 is already in use:

```bash
# Find the process
lsof -ti:5002

# Kill it
lsof -ti:5002 | xargs kill -9
```

### Ngrok Authentication Error

If you see authentication errors:

```bash
# Reconfigure the authtoken
ngrok config add-authtoken 2mtkS18m9XOwl8cFgBxpWHyXgio_4wLygqUmXu7Fqz43DhN2w
```

### Flask App Not Starting

Check the logs:

```bash
# If using start_with_ngrok.sh
cat flask.log

# Or run Flask directly to see errors
python3 run.py
```

### Domain Not Working

Ensure you have:
1. Valid ngrok authtoken
2. Custom domain properly configured in your ngrok account
3. The domain `astramech.ngrok.app` is assigned to your account

## Security Notes

⚠️ **Important**: The authtoken in this setup provides access to your ngrok account.

- Never commit `ngrok_config.yml` to public repositories
- Consider adding it to `.gitignore`
- Rotate the token if it's exposed

## Stopping the Services

### If using start_with_ngrok.sh

Press `Ctrl+C` to stop both ngrok and Flask.

### If running separately

Stop each service with `Ctrl+C` in their respective terminals.

### Force stop Flask

```bash
lsof -ti:5002 | xargs kill -9
```

## Integration with External Services

Your Astramech application is now accessible at `https://astramech.ngrok.app` and can receive:

- Webhook callbacks from external services
- API requests from other systems
- Form submissions from external forms

Example webhook URL structure:
```
https://astramech.ngrok.app/api/webhook
https://astramech.ngrok.app/agents/supervincent/status
https://astramech.ngrok.app/agents/clioalpha/analyze
```

## Environment Variables

If you need to use ngrok URL in your application:

```python
# In your Flask app
NGROK_URL = os.getenv('NGROK_URL', 'https://astramech.ngrok.app')
```

Set it in your environment:

```bash
export NGROK_URL=https://astramech.ngrok.app
python3 run.py
```

## Production Deployment

For production, consider:

1. **Ngrok paid plan** for custom domains without random subdomains
2. **Reserved domains** for consistent URLs
3. **Edge configuration** for advanced routing
4. **OAuth protection** for sensitive endpoints

Or migrate to a proper hosting solution like:
- Vercel (already configured in your project)
- Heroku
- AWS/GCP/Azure
- Digital Ocean

## Support

For ngrok-specific issues:
- Documentation: https://ngrok.com/docs
- Status page: https://status.ngrok.com

For Astramech application issues:
- Check application logs
- Review Flask error messages
- Test locally first without ngrok
