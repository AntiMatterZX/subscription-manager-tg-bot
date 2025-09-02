#!/bin/bash

# VPS Deployment Script for bot.rangaone.finance

echo "🚀 Starting VPS deployment..."

# Check if .env.production exists
if [ ! -f .env.production ]; then
    echo "❌ .env.production file not found. Please create it with your production environment variables."
    exit 1
fi

# Copy environment file
cp .env.production .env

# Create SSL directory if it doesn't exist
mkdir -p nginx/ssl

# Check if SSL certificates exist
if [ ! -f nginx/ssl/cert.pem ] || [ ! -f nginx/ssl/key.pem ]; then
    echo "⚠️  SSL certificates not found in nginx/ssl/"
    echo "Please add your SSL certificates:"
    echo "  - nginx/ssl/cert.pem"
    echo "  - nginx/ssl/key.pem"
    echo ""
    echo "For Let's Encrypt certificates, you can use:"
    echo "  sudo certbot certonly --standalone -d bot.rangaone.finance"
    echo "  Then copy the files to nginx/ssl/"
    echo ""
    read -p "Continue without SSL? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Stop existing containers
echo "🛑 Stopping existing containers..."
docker-compose -f docker-compose.vps.yml down

# Build and start containers
echo "🔨 Building and starting containers..."
docker-compose -f docker-compose.vps.yml up --build -d

# Wait for services to be ready
echo "⏳ Waiting for services to be ready..."
sleep 30

# Check if services are running
echo "🔍 Checking service status..."
docker-compose -f docker-compose.vps.yml ps

echo "✅ Deployment complete!"
echo ""
echo "Your application should be available at:"
echo "  - https://bot.rangaone.finance (with SSL)"
echo "  - http://bot.rangaone.finance (redirects to HTTPS)"
echo "  - API docs: https://bot.rangaone.finance/api-docs/"
echo ""
echo "To view logs:"
echo "  docker-compose -f docker-compose.vps.yml logs -f"