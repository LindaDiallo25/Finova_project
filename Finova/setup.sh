#!/bin/bash

# Finova Setup Script

echo "🚀 Finova Setup"
echo "===================="

# Check Docker
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker first."
    exit 1
fi

echo "✓ Docker found"

# Copy .env if not exists
if [ ! -f .env ]; then
    echo "📋 Creating .env from .env.example..."
    cp .env.example .env
    echo "⚠️  Please update .env with your GEMINI_API_KEY"
    echo "Edit .env and add your Gemini API key from https://ai.google.dev"
    read -p "Press enter when done..."
fi

# Build and run
echo "🔨 Building Docker images..."
docker-compose build

echo "🚀 Starting Finova..."
docker-compose up

echo "✓ Finova is running!"
echo ""
echo "📍 Accès:"
echo "   Frontend: http://localhost:3000"
echo "   Backend:  http://localhost:8000"
echo "   API Docs: http://localhost:8000/docs"
