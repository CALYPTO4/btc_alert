import yfinance as yf
import pandas as pd
from ta.trend import EMAIndicator, MACD, ADXIndicator
from ta.momentum import RSIIndicator, StochasticOscillator
from ta.volatility import BollingerBands
import smtplib
from email.mime.text import MIMEText
from datetime import datetime

# 🔐 ข้อมูลอีเมล
EMAIL_ADDRESS = "calypsoex4@gmail.com"
EMAIL_PASSWORD = "pkfj augk gcjp ghzj"
TO_EMAIL = "calipsoex4@gmail.com"

# 📊 ดึงข้อมูล BTCUSDT จาก Yahoo (TF 5 นาที, ย้อนหลัง 1 วัน)
df = yf.download("BTC-USD", interval="5m", period="1d")

# 🔧 คำนวณอินดิเคเตอร์
df['EMA20'] = EMAIndicator(df['Close'], window=20).ema_indicator()
df['EMA50'] = EMAIndicator(df['Close'], window=50).ema_indicator()

macd = MACD(df['Close'])
df['MACD'] = macd.macd()
df['MACD_signal'] = macd.macd_signal()

df['RSI'] = RSIIndicator(df['Close'], window=14).rsi()
df['ADX'] = ADXIndicator(df['High'], df['Low'], df['Close'], window=14).adx()

stoch = StochasticOscillator(df['High'], df['Low'], df['Close'], window=14, smooth_window=3)
df['Stoch_k'] = stoch.stoch()
df['Stoch_d'] = stoch.stoch_signal()

bb = BollingerBands(df['Close'], window=20, window_dev=2)
df['bb_upper'] = bb.bollinger_hband()
df['bb_lower'] = bb.bollinger_lband()

# 🧠 เงื่อนไขวิเคราะห์
last = df.iloc[-1]
signal = None

if (
    last['MACD'] > last['MACD_signal'] and
    last['RSI'] > 52 and
    last['EMA20'] > last['EMA50'] and
    last['Stoch_k'] < 30 and last['Stoch_k'] > last['Stoch_d'] and
    last['ADX'] > 20
):
    signal = "BUY"

elif (
    last['MACD'] < last['MACD_signal'] and
    last['RSI'] < 48 and
    last['EMA20'] < last['EMA50'] and
    last['Stoch_k'] > 70 and last['Stoch_k'] < last['Stoch_d'] and
    last['ADX'] > 20
):
    signal = "SELL"

# ✉️ ส่งอีเมลแจ้งเตือน
def send_email(subject, body):
    msg = MIMEText(body)
    msg['Subject'] = subject
    msg['From'] = EMAIL_ADDRESS
    msg['To'] = TO_EMAIL
    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
        smtp.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
        smtp.send_message(msg)

# ✅ ถ้ามีสัญญาณ → ส่งอีเมล
if signal:
    now = datetime.now().strftime('%Y-%m-%d %H:%M')
    price = last['Close']
    body = f"""
📊 BTCUSDT {signal} SIGNAL DETECTED (TF: 5M)

⏰ Time: {now}
Price: {price:.2f}

MACD: {last['MACD']:.2f} > Signal: {last['MACD_signal']:.2f}
RSI: {last['RSI']:.2f}
EMA20: {last['EMA20']:.2f}, EMA50: {last['EMA50']:.2f}
Stochastic K: {last['Stoch_k']:.2f}, D: {last['Stoch_d']:.2f}
ADX: {last['ADX']:.2f}
BB: Upper {last['bb_upper']:.2f}, Lower {last['bb_lower']:.2f}
"""
    send_email(f"⚡ BTCUSDT {signal} SIGNAL", body)
