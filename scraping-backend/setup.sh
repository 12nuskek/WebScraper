#!/bin/bash

# Setup script for Django scraping backend

echo "🚀 Setting up Django Scraping Backend..."

# Create virtual environment if it doesn't exist
if [ ! -d "../venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv ../venv
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source ../venv/bin/activate

# Install dependencies
echo "📥 Installing dependencies..."
pip install -r requirements.txt

# Create database directory if it doesn't exist
mkdir -p ../database

# Run migrations
echo "🗄️ Running database migrations..."
python manage.py makemigrations
python manage.py migrate

# Create superuser (optional)
echo "👤 You can create a superuser account:"
echo "python manage.py createsuperuser"

echo ""
echo "✅ Setup complete!"
echo ""
echo "🚀 To start the development server:"
echo "cd scraping-backend"
echo "source ../venv/bin/activate"
echo "python manage.py runserver"
echo ""
echo "📚 API Documentation will be available at:"
echo "- Swagger UI: http://127.0.0.1:8000/docs/"
echo "- ReDoc: http://127.0.0.1:8000/redoc/"
echo ""
echo "🔗 Available endpoints:"
echo "- POST /auth/register/"
echo "- POST /auth/login/"
echo "- POST /auth/logout/"
echo "- GET/PUT /profiles/me/"