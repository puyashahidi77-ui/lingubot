LINGUYA BALE BOT — SETUP
========================

1. INSTALL
----------
pip install python-bale-bot

2. GET YOUR ADMIN CHAT ID
--------------------------
- Open Bale, message @lingubot the word: myid
- Or send any message, then check logs for your user ID
- Paste it in bot.py line:  ADMIN_CHAT_ID = "12345678"

3. RUN LOCALLY (TEST)
----------------------
cd /Users/puyasi/lingubot
python bot.py

4. RUN ON SERVER (PRODUCTION)
------------------------------
Upload bot.py + requirements.txt to your Tavanahost (or any VPS).
Then run with nohup so it stays alive:

  pip install python-bale-bot
  nohup python bot.py &

Or use screen:
  screen -S lingubot
  python bot.py
  Ctrl+A then D to detach

5. BALE PAYMENT PROVIDER
--------------------------
Bale has its own built-in wallet payment.
provider_token is left empty — Bale handles it natively.
You may need to activate payments for your bot via @BotFather on Bale.

6. FLOW
-------
User clicks "پرداخت با بله" on website
→ Opens Bale app → @lingubot
→ Bot sends payment invoice for that course
→ User pays via Bale Wallet
→ Bot confirms + notifies you (admin)
