# Quick Start Guide - Finance Management Application

## 🚀 Get Started in 5 Minutes

### Prerequisites
- Python 3.8+
- Redis (local or cloud)
- Tesseract OCR

---

## Step 1: Install Dependencies

```bash
cd budget_tracker
pip install -r requirements.txt
```

---

## Step 2: Install System Dependencies

### Tesseract OCR

**Windows:**
1. Download from: https://github.com/UB-Mannheim/tesseract/wiki
2. Install and add to PATH

**Linux:**
```bash
sudo apt-get update
sudo apt-get install tesseract-ocr
```

**Mac:**
```bash
brew install tesseract
```

### Redis

**Windows:**
- Download from: https://github.com/microsoftarchive/redis/releases
- Or use Docker: `docker run -d -p 6379:6379 redis`

**Linux:**
```bash
sudo apt-get install redis-server
sudo systemctl start redis
```

**Mac:**
```bash
brew install redis
brew services start redis
```

---

## Step 3: Environment Setup

Create `.env` file in `budget_tracker/` directory:

```env
SECRET_KEY=your-secret-key-here-change-this
DEBUG=True
REDIS_URL=redis://localhost:6379/0

# Email (optional for testing)
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
```

---

## Step 4: Database Setup

```bash
# Run migrations
python manage.py makemigrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Load initial currency data
python setup_initial_data.py
```

---

## Step 5: Start Services

### Terminal 1: Django Server
```bash
python manage.py runserver
```

### Terminal 2: Celery Worker
```bash
celery -A budget_tracker worker -l info
```

### Terminal 3: Celery Beat (Scheduled Tasks)
```bash
celery -A budget_tracker beat -l info
```

---

## Step 6: Test the API

### Get JWT Token
```bash
curl -X POST http://localhost:8000/api/token/ \
  -H "Content-Type: application/json" \
  -d '{"username": "your_username", "password": "your_password"}'
```

### List Currencies
```bash
curl http://localhost:8000/api/currencies/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

### Create Recurring Transaction
```bash
curl -X POST http://localhost:8000/api/recurring-transactions/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "amount": 1500.00,
    "category": 1,
    "description": "Monthly Salary",
    "frequency": "monthly",
    "start_date": "2024-01-01",
    "next_occurrence": "2024-01-01"
  }'
```

---

## 🎯 Access Points

- **API**: http://localhost:8000/api/
- **Admin Panel**: http://localhost:8000/admin/
- **Frontend** (if running): http://localhost:4200/

---

## 📚 Key Endpoints

### Authentication
- `POST /api/signup/` - Register new user
- `POST /api/login/` - Login (token auth)
- `POST /api/token/` - Get JWT token
- `POST /api/token/refresh/` - Refresh JWT

### Features
- `/api/recurring-transactions/` - Recurring transactions
- `/api/bill-reminders/` - Bill reminders
- `/api/shared-accounts/` - Shared accounts
- `/api/financial-goals/` - Financial goals
- `/api/investments/` - Investment portfolio
- `/api/currencies/` - Currency list
- `/api/ocr/receipt/` - OCR receipt processing
- `/api/export/transactions/` - Export data
- `/api/2fa/` - Two-factor authentication

---

## 🔍 Verify Installation

### Check Redis Connection
```bash
redis-cli ping
# Should return: PONG
```

### Check Celery Worker
Look for this in Celery worker terminal:
```
[tasks]
  . budget.tasks.process_recurring_transactions
  . budget.tasks.send_bill_reminders
  . budget.tasks.update_investment_prices
  . budget.tasks.cleanup_old_data
```

### Check Database
```bash
python manage.py shell
```
```python
from budget.models import Currency
print(Currency.objects.count())  # Should be 10
```

---

## 🐛 Troubleshooting

### Redis Connection Error
```bash
# Check if Redis is running
redis-cli ping

# If not, start Redis
# Windows: redis-server.exe
# Linux/Mac: redis-server
```

### Tesseract Not Found
```bash
# Check installation
tesseract --version

# Add to PATH if needed (Windows)
# Control Panel > System > Advanced > Environment Variables
# Add: C:\Program Files\Tesseract-OCR
```

### Celery Not Starting
```bash
# Make sure Redis is running first
# Check for errors in terminal output
# Verify REDIS_URL in settings
```

### Migration Errors
```bash
# Delete migrations (except __init__.py)
# Delete db.sqlite3
# Run migrations again
python manage.py makemigrations
python manage.py migrate
```

---

## 📖 Next Steps

1. **Read Full Documentation**: Check `IMPLEMENTATION_GUIDE.md`
2. **Explore API**: Use Postman or curl to test endpoints
3. **Admin Panel**: Create test data via Django admin
4. **Frontend**: Start Angular development
5. **Testing**: Write tests for your use cases

---

## 💡 Pro Tips

1. **Use Postman**: Import API endpoints for easier testing
2. **Check Logs**: Monitor Django and Celery logs for errors
3. **Redis GUI**: Use RedisInsight for visual Redis management
4. **Database GUI**: Use DB Browser for SQLite during development
5. **Environment**: Use python-dotenv for environment variables

---

## 📞 Need Help?

- Check `FEATURES_SUMMARY.md` for feature overview
- Read `IMPLEMENTATION_GUIDE.md` for detailed docs
- Review Django logs: `python manage.py runserver`
- Check Celery logs in worker terminal
- Verify Redis: `redis-cli monitor`

---

## ✅ Checklist

- [ ] Python 3.8+ installed
- [ ] Dependencies installed (`pip install -r requirements.txt`)
- [ ] Tesseract OCR installed
- [ ] Redis running
- [ ] Migrations completed
- [ ] Superuser created
- [ ] Initial data loaded
- [ ] Django server running
- [ ] Celery worker running
- [ ] Celery beat running
- [ ] API responding to requests

---

**You're all set! Start building amazing financial features! 🎉**
