# Flight Price Tracker

Track flight prices and get notified when prices drop. Currently configured for:
- **Route:** Toronto (YYZ) → Vancouver (YVR)
- **Dates:** July 29 - August 5, 2025
- **Includes:** Carry-on bag pricing

## Setup

1. **Get a SerpApi key** (free tier available):
   - Sign up at https://serpapi.com
   - Get 100 free searches/month

2. **Configure environment**:
   ```bash
   cp .env.example .env
   # Edit .env and add your SERPAPI_KEY
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

### Check prices once
```bash
python tracker.py
```

### Run continuously (checks every 6 hours)
```bash
python tracker.py --continuous
```

### View price history
```bash
python tracker.py --history
```

## Configuration

Edit `config.py` to change:
- Origin/destination airports
- Travel dates
- Number of bags
- Check interval
- Price alert thresholds
- Target price

## Email Notifications (Optional)

To receive email alerts when prices drop:

1. Edit `.env` and set:
   ```
   EMAIL_ENABLED=true
   SMTP_EMAIL=your_email@gmail.com
   SMTP_PASSWORD=your_app_password
   NOTIFY_EMAIL=where_to_send@example.com
   ```

2. For Gmail, create an App Password:
   - Go to Google Account → Security → 2-Step Verification → App passwords
   - Generate a password for "Mail"

## Tips for Finding Lower Fares

1. **Check prices at different times** - Prices often change throughout the day
2. **Be flexible with dates** - Modify `config.py` to check alternative dates
3. **Set a price target** - Get alerted when prices hit your budget
4. **Book quickly** - Low prices don't last long!
