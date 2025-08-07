# Step-by-Step Hosting Guide

## Option 1: VPS Hosting (Recommended)

### Step 1: Get a VPS Server
1. Sign up for a VPS provider:
   - **DigitalOcean** (easiest): $5/month droplet
   - **Linode**: $5/month nanode
   - **AWS EC2**: t2.micro (free tier)
   - **Vultr**: $2.50/month

2. Create Ubuntu 22.04 server with at least 1GB RAM

### Step 2: Connect to Your Server
```bash
ssh root@your_server_ip
```

### Step 3: Install Docker
```bash
# Update system
apt update && apt upgrade -y

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh

# Install Docker Compose
curl -L "https://github.com/docker/compose/releases/download/v2.20.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
chmod +x /usr/local/bin/docker-compose

# Start Docker
systemctl start docker
systemctl enable docker
```

### Step 4: Upload Your Project
```bash
# Install git
apt install git -y

# Clone or upload your project
git clone <your-repo-url>
# OR upload via SCP/SFTP
```

### Step 5: Configure Environment
```bash
cd subscription-manager-tg-bot-main
cp .env.example .env
nano .env
```

Update `.env` with:
```
POSTGRES_PASSWORD=secure_password_123
SECRET_KEY=your_long_random_secret_key
TELEGRAM_BOT_TOKEN=your_bot_token
FLASK_ENV=production
```

### Step 6: Deploy
```bash
# Build and start
docker-compose up -d --build

# Check status
docker-compose ps
docker-compose logs
```

### Step 7: Configure Domain (Optional)
1. Point your domain to server IP
2. Install nginx:
```bash
apt install nginx -y
```

3. Configure nginx:
```bash
nano /etc/nginx/sites-available/tg-bot
```

Add:
```nginx
server {
    listen 80;
    server_name yourdomain.com;
    
    location / {
        proxy_pass http://localhost:3000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
    
    location /api {
        proxy_pass http://localhost:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

```bash
ln -s /etc/nginx/sites-available/tg-bot /etc/nginx/sites-enabled/
nginx -t
systemctl restart nginx
```

## Option 2: Railway (Easiest)

### Step 1: Prepare for Railway
1. Create account at railway.app
2. Install Railway CLI:
```bash
npm install -g @railway/cli
```

### Step 2: Deploy
```bash
cd subscription-manager-tg-bot-main
railway login
railway init
railway up
```

### Step 3: Add Environment Variables
In Railway dashboard, add:
- `TELEGRAM_BOT_TOKEN`
- `SECRET_KEY`
- `POSTGRES_PASSWORD`

## Option 3: Heroku

### Step 1: Install Heroku CLI
Download from heroku.com/cli

### Step 2: Deploy
```bash
cd subscription-manager-tg-bot-main
heroku login
heroku create your-app-name
heroku addons:create heroku-postgresql:mini
heroku config:set TELEGRAM_BOT_TOKEN=your_token
heroku config:set SECRET_KEY=your_secret
git push heroku main
```

## Quick Start (Local Testing)
```bash
cd subscription-manager-tg-bot-main
docker-compose up --build
```
Access at: http://localhost:3000

## Troubleshooting
- Check logs: `docker-compose logs`
- Restart services: `docker-compose restart`
- View running containers: `docker-compose ps`