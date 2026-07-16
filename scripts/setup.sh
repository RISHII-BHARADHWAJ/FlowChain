#!/bin/bash
# FlowChain - Local Setup Script (without Docker)
set -e

echo "🚀 Setting up FlowChain Platform..."

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install --upgrade pip
pip install -r requirements.txt

# Copy env file
if [ ! -f .env ]; then
  cp .env.example .env
  echo "📝 Created .env file - please update with your settings"
fi

# Create log directory
mkdir -p logs media staticfiles

# Run migrations
python manage.py migrate

# Create superuser
echo "Creating superuser..."
python manage.py shell << 'PYEOF'
from accounts.models import User
if not User.objects.filter(email='admin@cyberbuddy.com').exists():
    User.objects.create_superuser(
        email='admin@cyberbuddy.com',
        password='Admin@1234',
        first_name='Super',
        last_name='Admin',
    )
    print("✅ Superuser created: admin@cyberbuddy.com / Admin@1234")
else:
    print("ℹ️  Superuser already exists")
PYEOF

# Collect static files
python manage.py collectstatic --noinput

echo ""
echo "✅ Setup complete!"
echo ""
echo "To start the development server:"
echo "  source venv/bin/activate"
echo "  python manage.py runserver"
echo ""
echo "Access: http://localhost:8000"
echo "Admin: http://localhost:8000/admin"
echo "API Docs: http://localhost:8000/api/docs/"
echo ""
echo "Login: admin@cyberbuddy.com / Admin@1234"
