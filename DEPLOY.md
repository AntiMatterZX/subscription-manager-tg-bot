# GitHub Fork & Deploy Guide

## Step 1: Fork to GitHub
```bash
cd c:\RANGAONE\subscription-manager-tg-bot-main

# Initialize git (if not already)
git init
git add .
git commit -m "Initial commit"

# Add your GitHub repo
git remote add origin https://github.com/YOUR_USERNAME/subscription-manager-tg-bot.git
git branch -M main
git push -u origin main
```

## Step 2: One-Click Deploy Options

### Railway (Recommended)
1. Go to railway.app
2. Click "Deploy from GitHub repo"
3. Select your forked repo
4. Add environment variables:
   - `TELEGRAM_BOT_TOKEN`
   - `SECRET_KEY`
   - `POSTGRES_PASSWORD`

### Render
1. Go to render.com
2. Connect GitHub repo
3. Choose "Docker" deployment
4. Set environment variables

### Heroku
```bash
# Install Heroku CLI
# Then:
heroku create your-app-name
heroku stack:set container
git push heroku main
```

## Step 3: Auto-Deploy Setup
GitHub Actions is configured to auto-deploy on push to main branch.

Add these secrets in GitHub repo settings:
- `HOST`: Your server IP
- `USERNAME`: root
- `SSH_KEY`: Your private SSH key