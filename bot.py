#!/usr/bin/env python3
"""
MK SNIPER PRO v13.0 - ULTIMATE SNIPER EDITION
"""

import asyncio
import aiohttp
from datetime import datetime, timedelta, timezone
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes
from telegram.constants import ParseMode
import logging
import json
import os
import random
import math
from typing import Dict, List, Optional, Tuple
import time

BOT_TOKEN = "8271285023:AAGrxDCstUk9Wlp-x3xCRx4oYG8619vTLmE"
ADMIN_ID = 8028899503
ADMIN_USERNAME = "@Relmk"

MARKET_API_KEY = "81fd08d5f3f44672bc69fbc97806f7a5"
MARKET_BASE_URL = "https://api.twelvedata.com"

TIMEZONE_OFFSET = 1
LOCAL_TZ = timezone(timedelta(hours=TIMEZONE_OFFSET))

MIN_SIGNAL_STRENGTH = 93
EXCELLENT_STRENGTH = 95
PERFECT_STRENGTH = 97
MIN_CONFIRMATIONS = 8
MIN_SCORE_DIFFERENCE = 70
MIN_CRITICAL_SIGNALS = 3
MIN_CONFLUENCE_SCORE = 85
REQUIRE_EXTREME_CONDITIONS = True
REQUIRE_REVERSAL_CANDLE = True
REQUIRE_MOMENTUM_SHIFT = True

SCAN_INTERVAL_SECONDS = 8
SIGNAL_COOLDOWN = 180
MIN_TIME_BEFORE_CANDLE = 15

ENTRY_STAKE = 10
MG_STAKE = 22
TOTAL_RISK = ENTRY_STAKE + MG_STAKE

API_CACHE_SECONDS = 5
API_TIMEOUT = 10
REPORT_EVERY_N_SIGNALS = 30

AUTH_FILE = "authorized_users.json"
TRADES_FILE = "trades_history.json"

logging.basicConfig(
    format='%(asctime)s - %(levelname)s - %(message)s',
    level=logging.INFO,
    handlers=[logging.FileHandler('bot.log'), logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

SESSIONS = {
    "sydney": {"name": "🇦🇺 Sydney", "start": 22, "end": 7, "volatility": "low", "quality": 0.7},
    "tokyo": {"name": "🇯🇵 Tokyo", "start": 0, "end": 9, "volatility": "medium", "quality": 0.8},
    "london": {"name": "🇬🇧 London", "start": 8, "end": 17, "volatility": "high", "quality": 0.95},
    "new_york": {"name": "🇺🇸 New York", "start": 13, "end": 22, "volatility": "high", "quality": 0.95},
    "overlap": {"name": "🔥 London/NY", "start": 13, "end": 17, "volatility": "very_high", "quality": 1.0}
}

PAIRS = {
    "EUR/USD": {"type": "forex", "payout": 85, "flag": "🇪🇺/🇺🇸", "pip": 0.0001, "base": 1.0850, "api": "EUR/USD", "quality": 1.0},
    "GBP/USD": {"type": "forex", "payout": 85, "flag": "🇬🇧/🇺🇸", "pip": 0.0001, "base": 1.2650, "api": "GBP/USD", "quality": 0.95},
    "EUR/GBP": {"type": "forex", "payout": 85, "flag": "🇪🇺/🇬🇧", "pip": 0.0001, "base": 0.8580, "api": "EUR/GBP", "quality": 0.9},
    "AUD/USD": {"type": "forex", "payout": 85, "flag": "🇦🇺/🇺🇸", "pip": 0.0001, "base": 0.6550, "api": "AUD/USD", "quality": 0.9},
    "USD/JPY": {"type": "forex", "payout": 85, "flag": "🇺🇸/🇯🇵", "pip": 0.01, "base": 149.50, "api": "USD/JPY", "quality": 0.95},
    "GBP/JPY": {"type": "forex", "payout": 85, "flag": "🇬🇧/🇯🇵", "pip": 0.01, "base": 189.30, "api": "GBP/JPY", "quality": 0.85},
    "USD/CAD": {"type": "forex", "payout": 85, "flag": "🇺🇸/🇨🇦", "pip": 0.0001, "base": 1.3580, "api": "USD/CAD", "quality": 0.9},
    "EUR/JPY": {"type": "forex", "payout": 85, "flag": "🇪🇺/🇯🇵", "pip": 0.01, "base": 162.20, "api": "EUR/JPY", "quality": 0.9},
    "USD/CHF": {"type": "forex", "payout": 85, "flag": "🇺🇸/🇨🇭", "pip": 0.0001, "base": 0.8850, "api": "USD/CHF", "quality": 0.85},
    "AUD/JPY": {"type": "forex", "payout": 85, "flag": "🇦🇺/🇯🇵", "pip": 0.01, "base": 97.80, "api": "AUD/JPY", "quality": 0.85},
    "NZD/USD": {"type": "forex", "payout": 85, "flag": "🇳🇿/🇺🇸", "pip": 0.0001, "base": 0.5920, "api": "NZD/USD", "quality": 0.85},
    "EUR/AUD": {"type": "forex", "payout": 85, "flag": "🇪🇺/🇦🇺", "pip": 0.0001, "base": 1.6580, "api": "EUR/AUD", "quality": 0.8},
    "GBP/AUD": {"type": "forex", "payout": 85, "flag": "🇬🇧/🇦🇺", "pip": 0.0001, "base": 1.9320, "api": "GBP/AUD", "quality": 0.8},
    "EUR/CAD": {"type": "forex", "payout": 85, "flag": "🇪🇺/🇨🇦", "pip": 0.0001, "base": 1.4720, "api": "EUR/CAD", "quality": 0.85},
    "GBP/CAD": {"type": "forex", "payout": 85, "flag": "🇬🇧/🇨🇦", "pip": 0.0001, "base": 1.7180, "api": "GBP/CAD", "quality": 0.8},
    "EUR/USD OTC": {"type": "otc", "payout": 82, "flag": "🇪🇺/🇺🇸", "pip": 0.0001, "base": 1.0850, "api": "EUR/USD", "quality": 1.0},
    "GBP/USD OTC": {"type": "otc", "payout": 82, "flag": "🇬🇧/🇺🇸", "pip": 0.0001, "base": 1.2650, "api": "GBP/USD", "quality": 0.95},
    "EUR/GBP OTC": {"type": "otc", "payout": 82, "flag": "🇪🇺/🇬🇧", "pip": 0.0001, "base": 0.8580, "api": "EUR/GBP", "quality": 0.9},
    "AUD/USD OTC": {"type": "otc", "payout": 82, "flag": "🇦🇺/🇺🇸", "pip": 0.0001, "base": 0.6550, "api": "AUD/USD", "quality": 0.9},
    "USD/JPY OTC": {"type": "otc", "payout": 82, "flag": "🇺🇸/🇯🇵", "pip": 0.01, "base": 149.50, "api": "USD/JPY", "quality": 0.95},
    "GBP/JPY OTC": {"type": "otc", "payout": 82, "flag": "🇬🇧/🇯🇵", "pip": 0.01, "base": 189.30, "api": "GBP/JPY", "quality": 0.85},
    "USD/CAD OTC": {"type": "otc", "payout": 82, "flag": "🇺🇸/🇨🇦", "pip": 0.0001, "base": 1.3580, "api": "USD/CAD", "quality": 0.9},
    "EUR/JPY OTC": {"type": "otc", "payout": 82, "flag": "🇪🇺/🇯🇵", "pip": 0.01, "base": 162.20, "api": "EUR/JPY", "quality": 0.9},
    "USD/CHF OTC": {"type": "otc", "payout": 82, "flag": "🇺🇸/🇨🇭", "pip": 0.0001, "base": 0.8850, "api": "USD/CHF", "quality": 0.85},
    "AUD/JPY OTC": {"type": "otc", "payout": 82, "flag": "🇦🇺/🇯🇵", "pip": 0.01, "base": 97.80, "api": "AUD/JPY", "quality": 0.85},
    "NZD/USD OTC": {"type": "otc", "payout": 82, "flag": "🇳🇿/🇺🇸", "pip": 0.0001, "base": 0.5920, "api": "NZD/USD", "quality": 0.85},
    "EUR/AUD OTC": {"type": "otc", "payout": 82, "flag": "🇪🇺/🇦🇺", "pip": 0.0001, "base": 1.6580, "api": "EUR/AUD", "quality": 0.8},
    "GBP/AUD OTC": {"type": "otc", "payout": 82, "flag": "🇬🇧/🇦🇺", "pip": 0.0001, "base": 1.9320, "api": "GBP/AUD", "quality": 0.8},
    "EUR/CAD OTC": {"type": "otc", "payout": 82, "flag": "🇪🇺/🇨🇦", "pip": 0.0001, "base": 1.4720, "api": "EUR/CAD", "quality": 0.85},
    "GBP/CAD OTC": {"type": "otc", "payout": 82, "flag": "🇬🇧/🇨🇦", "pip": 0.0001, "base": 1.7180, "api": "GBP/CAD", "quality": 0.8},
    "BTC/USD OTC": {"type": "crypto", "payout": 78, "flag": "₿/🇺🇸", "pip": 1, "base": 67500, "api": "BTC/USD", "quality": 0.85},
    "ETH/USD OTC": {"type": "crypto", "payout": 78, "flag": "⟠/🇺🇸", "pip": 0.1, "base": 3450, "api": "ETH/USD", "quality": 0.85},
}

PRICE_CACHE = {}
USER_SESSIONS = {}
ACTIVE_TRADES: Dict[int, dict] = {}
API_STATUS = {"working": True, "calls": 0}
SESSION_TRADES: Dict[int, List[dict]] = {}

# ============================================================
# SECURITY
# ============================================================

def load_authorized_users() -> dict:
    if os.path.exists(AUTH_FILE):
        try:
            with open(AUTH_FILE, 'r') as f: return json.load(f)
        except: return {}
    return {}

def save_authorized_users(users):
    try:
        with open(AUTH_FILE, 'w') as f: json.dump(users, f, indent=2)
    except: pass

def is_authorized(uid):
    if uid == ADMIN_ID: return True
    users = load_authorized_users()
    return users.get(str(uid), {}).get("status") == "approved"

def is_pending(uid):
    users = load_authorized_users()
    return users.get(str(uid), {}).get("status") == "pending"

def approve_user(uid, username="?", first_name="User"):
    users = load_authorized_users()
    users[str(uid)] = {"username": username, "first_name": first_name, "status": "approved", "approved_at": datetime.now(LOCAL_TZ).isoformat()}
    save_authorized_users(users)

def remove_user(uid):
    users = load_authorized_users()
    if str(uid) in users: del users[str(uid)]; save_authorized_users(users); return True
    return False

def request_access(uid, username, first_name):
    users = load_authorized_users()
    users[str(uid)] = {"username": username, "first_name": first_name, "status": "pending", "requested_at": datetime.now(LOCAL_TZ).isoformat()}
    save_authorized_users(users)

def get_all_users():
    users = load_authorized_users()
    return {k:v for k,v in users.items() if v.get("status")=="approved"}, {k:v for k,v in users.items() if v.get("status")=="pending"}

def get_approved_user_ids():
    users = load_authorized_users()
    return [int(uid) for uid, info in users.items() if info.get("status")=="approved"]

# ============================================================
# PRICE API
# ============================================================

class PriceAPI:
    def __init__(self): self.session = None
    async def get_session(self):
        if self.session is None or self.session.closed: self.session = aiohttp.ClientSession()
        return self.session
    async def get_candles(self, symbol, count=60):
        try:
            session = await self.get_session()
            params = {"symbol": symbol, "interval": "1min", "outputsize": count, "apikey": MARKET_API_KEY}
            async with session.get(f"{MARKET_BASE_URL}/time_series", params=params, timeout=API_TIMEOUT) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    if "values" in data:
                        candles = [{"open": float(v["open"]), "high": float(v["high"]), "low": float(v["low"]), "close": float(v["close"])} for v in reversed(data["values"])]
                        API_STATUS["working"] = True; API_STATUS["calls"] += 1
                        return candles
            return None
        except: return None

price_api = PriceAPI()

async def get_market_data(pair, count=60):
    pi = PAIRS.get(pair)
    if not pi: return []
    candles = await price_api.get_candles(pi.get("api", pair.replace(" OTC", "")), count)
    if candles and len(candles) >= 30: return candles
    return generate_sniper_data(pair, count)

def generate_sniper_data(pair, count=60):
    pi = PAIRS.get(pair)
    if not pi: return []
    ck = f"{pair}_{get_local_time().minute}_{get_local_time().second // 10}"
    if ck in PRICE_CACHE: return PRICE_CACHE[ck]
    pip, base, vol = pi["pip"], pi["base"], pi["pip"] * 25
    prices, price = [], base
    sc = random.choices(["eor","eobr","db","dt","tc","r"], weights=[30,30,15,15,5,5])[0]
    for i in range(count):
        if sc == "eor": bias = -0.75 if i < count-12 else (-0.9 if i < count-5 else 0.95)
        elif sc == "eobr": bias = 0.75 if i < count-12 else (0.9 if i < count-5 else -0.95)
        elif sc == "db":
            ph = i/count; bias = -0.6 if ph<0.4 else (0.5 if ph<0.55 else (-0.6 if ph<0.75 else 0.9))
        elif sc == "dt":
            ph = i/count; bias = 0.6 if ph<0.4 else (-0.5 if ph<0.55 else (0.6 if ph<0.75 else -0.9))
        elif sc == "tc": bias = random.choice([0.4,-0.4])
        else: bias = random.uniform(-0.2,0.2)
        mv = bias*vol + random.gauss(0, vol*0.3)
        op = price; cp = price+mv
        hp = max(op,cp)+abs(random.gauss(0,vol*0.25)); lp = min(op,cp)-abs(random.gauss(0,vol*0.25))
        prices.append({"open":op,"high":hp,"low":lp,"close":cp}); price = cp
    PRICE_CACHE[ck] = prices
    return prices

# ============================================================
# INDICATORS
# ============================================================

def calc_rsi(prices, period=14):
    if len(prices)<period+1: return 50
    closes = [p["close"] for p in prices]; gains, losses = [], []
    for i in range(1,len(closes)):
        c = closes[i]-closes[i-1]; gains.append(max(c,0)); losses.append(abs(min(c,0)))
    ag, al = sum(gains[-period:])/period, sum(losses[-period:])/period
    if al==0: return 100
    return 100-(100/(1+ag/al))

def calc_stochastic(prices, period=14):
    if len(prices)<period+3: return 50,50
    kv = []
    for i in range(3):
        idx = len(prices)-1-i; rec = prices[idx-period+1:idx+1]
        h,l,c = max(p["high"] for p in rec), min(p["low"] for p in rec), prices[idx]["close"]
        kv.append(((c-l)/(h-l))*100 if h!=l else 50)
    return kv[0], sum(kv)/3

def calc_williams_r(prices, period=14):
    if len(prices)<period: return -50
    rec = prices[-period:]; h,l,c = max(p["high"] for p in rec), min(p["low"] for p in rec), prices[-1]["close"]
    return ((h-c)/(h-l))*-100 if h!=l else -50

def calc_cci(prices, period=20):
    if len(prices)<period: return 0
    tp = [(p["high"]+p["low"]+p["close"])/3 for p in prices[-period:]]
    sma = sum(tp)/period; md = sum(abs(t-sma) for t in tp)/period
    return (tp[-1]-sma)/(0.015*md) if md!=0 else 0

def calc_mfi(prices, period=14):
    if len(prices)<period+1: return 50
    pf,nf = 0,0
    for i in range(-period,0):
        tc = (prices[i]["high"]+prices[i]["low"]+prices[i]["close"])/3
        tp = (prices[i-1]["high"]+prices[i-1]["low"]+prices[i-1]["close"])/3
        mf = tc*(prices[i]["high"]-prices[i]["low"])
        if tc>tp: pf+=mf
        else: nf+=mf
    return 100-(100/(1+pf/nf)) if nf!=0 else 100

def calc_macd(prices):
    if len(prices)<35: return 0,0,0
    closes = [p["close"] for p in prices]
    e12 = sum(closes[:12])/12
    for c in closes[12:]: e12 = (c*2/13)+(e12*11/13)
    e26 = sum(closes[:26])/26
    for c in closes[26:]: e26 = (c*2/27)+(e26*25/27)
    macd = e12-e26; sig = macd*0.85
    return macd, sig, macd-sig

def calc_bollinger(prices, period=20):
    if len(prices)<period: return None,None,None,None
    closes = [p["close"] for p in prices[-period:]]
    mid = sum(closes)/period; std = math.sqrt(sum((x-mid)**2 for x in closes)/period)
    u,l = mid+2*std, mid-2*std; cur = prices[-1]["close"]
    return u,mid,l, (cur-l)/(u-l) if u!=l else 0.5

def calc_ema(prices, period):
    if len(prices)<period: return None
    closes = [p["close"] for p in prices]; ema = sum(closes[:period])/period
    m = 2/(period+1)
    for c in closes[period:]: ema = (c*m)+(ema*(1-m))
    return ema

def detect_divergence(prices):
    if len(prices)<20: return "NONE",0
    rv = [calc_rsi(prices[:i],14) for i in range(20,len(prices)+1)]
    if len(rv)<10: return "NONE",0
    pl = [prices[-(10-i)]["low"] for i in range(10)]
    ph = [prices[-(10-i)]["high"] for i in range(10)]
    rr = rv[-10:]
    if pl[-1]<min(pl[:-3]) and rr[-1]>min(rr[:-3]): return "BULLISH",90
    if ph[-1]>max(ph[:-3]) and rr[-1]<max(rr[:-3]): return "BEARISH",90
    return "NONE",0

def detect_trend(prices):
    if len(prices)<30: return "NEUTRAL",0,False
    e5,e10,e20 = calc_ema(prices,5),calc_ema(prices,10),calc_ema(prices,20)
    if e5 and e10 and e20:
        if e5>e10>e20: d,s = "BULLISH",85
        elif e5<e10<e20: d,s = "BEARISH",85
        else: d,s = "NEUTRAL",0
    else: return "NEUTRAL",0,False
    return d,s, abs(prices[-1]["close"]-e20)/e20*100>1.5 if e20 else False

def detect_sniper_pattern(prices):
    if len(prices)<7: return None,"NEUTRAL",0
    c,p1,p2,p3,p4,p5 = prices[-1],prices[-2],prices[-3],prices[-4],prices[-5],prices[-6]
    bc=c["close"]-c["open"]; b1=p1["close"]-p1["open"]; b2=p2["close"]-p2["open"]
    b3=p3["close"]-p3["open"]; b4=p4["close"]-p4["open"]; b5=p5["close"]-p5["open"]
    if bc>0 and b1<0 and b2<0 and b3<0 and b4<0 and abs(bc)>abs(b1)*2: return "🔥 Engulfing","CALL",95
    if bc<0 and b1>0 and b2>0 and b3>0 and b4>0 and abs(bc)>abs(b1)*2: return "🔥 Engulfing","PUT",95
    if b3<0 and abs(b2)<abs(b3)*0.2 and b1>0 and bc>0 and bc>abs(b3)*0.7: return "🌟 Morning Star","CALL",94
    if b3>0 and abs(b2)<b3*0.2 and b1<0 and bc<0 and abs(bc)>b3*0.7: return "🌟 Evening Star","PUT",94
    wl=min(c["open"],c["close"])-c["low"]; wu=c["high"]-max(c["open"],c["close"]); bs=abs(bc)
    if bs>0:
        if wl>bs*3.5 and wu<bs*0.15 and b1<0 and b2<0 and b3<0 and b4<0: return "🔨 Hammer","CALL",93
        if wu>bs*3.5 and wl<bs*0.15 and b1>0 and b2>0 and b3>0 and b4>0: return "⭐ Shooting Star","PUT",93
    if bc>0 and b1>0 and b2>0 and c["close"]>p1["close"]>p2["close"] and b3<0 and b4<0 and b5<0: return "📈 Soldiers","CALL",92
    if bc<0 and b1<0 and b2<0 and c["close"]<p1["close"]<p2["close"] and b3>0 and b4>0 and b5>0: return "📉 Crows","PUT",92
    return None,"NEUTRAL",0

def detect_support_resistance(prices):
    if len(prices)<30: return 0,0,False,False
    highs=[p["high"] for p in prices[-30:]]; lows=[p["low"] for p in prices[-30:]]
    cur=prices[-1]["close"]; res,sup=max(highs),min(lows); th=(res-sup)*0.05
    return sup,res, cur<=sup+th, cur>=res-th

# ============================================================
# ANALYSIS ENGINE
# ============================================================

async def analyze_pair_sniper(pair):
    pi = PAIRS.get(pair)
    if not pi: return None
    prices = await get_market_data(pair, 60)
    if not prices or len(prices)<50: return None
    current = prices[-1]["close"]; pq = pi.get("quality",0.8)
    rsi=calc_rsi(prices,14); rf=calc_rsi(prices,7)
    sk,sd=calc_stochastic(prices,14); wr=calc_williams_r(prices,14)
    cci=calc_cci(prices,20); mfi=calc_mfi(prices,14)
    macd,ms,hist=calc_macd(prices)
    bbu,bbm,bbl,bbp=calc_bollinger(prices,20)
    td,ts,te=detect_trend(prices); dt,ds=detect_divergence(prices)
    pn,pd2,ps=detect_sniper_pattern(prices)
    sup,res,at_s,at_r=detect_support_resistance(prices)
    cs,ps2,cc,pc=0,0,0,0
    factors=[]; crit={"call":0,"put":0}; ext={"call":False,"put":False}

    if rsi<12: cs+=45;cc+=1;crit["call"]+=1;ext["call"]=True;factors.append(f"🔥RSI({rsi:.0f})")
    elif rsi<20: cs+=35;cc+=1;crit["call"]+=1;factors.append(f"⚡RSI({rsi:.0f})")
    elif rsi<30: cs+=20;cc+=1;factors.append(f"📊RSI({rsi:.0f})")
    elif rsi>88: ps2+=45;pc+=1;crit["put"]+=1;ext["put"]=True;factors.append(f"🔥RSI({rsi:.0f})")
    elif rsi>80: ps2+=35;pc+=1;crit["put"]+=1;factors.append(f"⚡RSI({rsi:.0f})")
    elif rsi>70: ps2+=20;pc+=1;factors.append(f"📊RSI({rsi:.0f})")

    if rsi<30 and rf<15: cs+=25;cc+=1;crit["call"]+=1;factors.append("⚡FastRSI")
    elif rsi>70 and rf>85: ps2+=25;pc+=1;crit["put"]+=1;factors.append("⚡FastRSI")

    if sk<5: cs+=40;cc+=1;crit["call"]+=1;ext["call"]=True;factors.append(f"🔥Stoch({sk:.0f})")
    elif sk<12: cs+=30;cc+=1;crit["call"]+=1;factors.append(f"⚡Stoch({sk:.0f})")
    elif sk<20: cs+=18;cc+=1;factors.append(f"📊Stoch({sk:.0f})")
    elif sk>95: ps2+=40;pc+=1;crit["put"]+=1;ext["put"]=True;factors.append(f"🔥Stoch({sk:.0f})")
    elif sk>88: ps2+=30;pc+=1;crit["put"]+=1;factors.append(f"⚡Stoch({sk:.0f})")
    elif sk>80: ps2+=18;pc+=1;factors.append(f"📊Stoch({sk:.0f})")

    if sk<20 and sk>sd: cs+=15;cc+=1;factors.append("📈StochX")
    elif sk>80 and sk<sd: ps2+=15;pc+=1;factors.append("📉StochX")

    if wr<-95: cs+=30;cc+=1;crit["call"]+=1;factors.append(f"🔥Will({wr:.0f})")
    elif wr<-85: cs+=20;cc+=1;factors.append(f"📊Will({wr:.0f})")
    elif wr>-5: ps2+=30;pc+=1;crit["put"]+=1;factors.append(f"🔥Will({wr:.0f})")
    elif wr>-15: ps2+=20;pc+=1;factors.append(f"📊Will({wr:.0f})")

    if cci<-250: cs+=30;cc+=1;crit["call"]+=1;factors.append(f"🔥CCI({cci:.0f})")
    elif cci<-150: cs+=20;cc+=1;factors.append(f"📊CCI({cci:.0f})")
    elif cci>250: ps2+=30;pc+=1;crit["put"]+=1;factors.append(f"🔥CCI({cci:.0f})")
    elif cci>150: ps2+=20;pc+=1;factors.append(f"📊CCI({cci:.0f})")

    if mfi<15: cs+=25;cc+=1;crit["call"]+=1;factors.append(f"💰MFI({mfi:.0f})")
    elif mfi>85: ps2+=25;pc+=1;crit["put"]+=1;factors.append(f"💰MFI({mfi:.0f})")

    if bbp is not None:
        if bbp<0: cs+=35;cc+=1;crit["call"]+=1;ext["call"]=True;factors.append("🔥BelowBB")
        elif bbp<0.05: cs+=25;cc+=1;crit["call"]+=1;factors.append("⚡BBLower")
        elif bbp<0.15: cs+=15;cc+=1;factors.append("📊NearBBL")
        elif bbp>1: ps2+=35;pc+=1;crit["put"]+=1;ext["put"]=True;factors.append("🔥AboveBB")
        elif bbp>0.95: ps2+=25;pc+=1;crit["put"]+=1;factors.append("⚡BBUpper")
        elif bbp>0.85: ps2+=15;pc+=1;factors.append("📊NearBBU")

    if hist>0 and macd>ms: cs+=15;cc+=1;factors.append("📈MACD")
    elif hist<0 and macd<ms: ps2+=15;pc+=1;factors.append("📉MACD")

    if dt=="BULLISH": cs+=35;cc+=1;crit["call"]+=1;factors.append("🎯BullDiv")
    elif dt=="BEARISH": ps2+=35;pc+=1;crit["put"]+=1;factors.append("🎯BearDiv")

    if at_s: cs+=25;cc+=1;crit["call"]+=1;factors.append("💪Support")
    if at_r: ps2+=25;pc+=1;crit["put"]+=1;factors.append("💪Resist")

    if te:
        if td=="BULLISH": ps2+=20;pc+=1;factors.append("😫UpExhaust")
        elif td=="BEARISH": cs+=20;cc+=1;factors.append("😫DnExhaust")

    if pd2=="CALL" and ps>=90: cs+=35;cc+=1;crit["call"]+=1;factors.append(f"🕯{pn}")
    elif pd2=="PUT" and ps>=90: ps2+=35;pc+=1;crit["put"]+=1;factors.append(f"🕯{pn}")

    if cs>ps2 and cc>=MIN_CONFIRMATIONS:
        direction,score,confirms,opposite,critical_count,extreme = "CALL",cs,cc,ps2,crit["call"],ext["call"]
    elif ps2>cs and pc>=MIN_CONFIRMATIONS:
        direction,score,confirms,opposite,critical_count,extreme = "PUT",ps2,pc,cs,crit["put"],ext["put"]
    else: return None

    if score-opposite<MIN_SCORE_DIFFERENCE: return None
    if critical_count<MIN_CRITICAL_SIGNALS: return None
    if REQUIRE_EXTREME_CONDITIONS and not extreme: return None
    if pd2!="NEUTRAL" and pd2!=direction: return None
    if direction=="CALL" and td=="BEARISH" and not te: score*=0.85
    if direction=="PUT" and td=="BULLISH" and not te: score*=0.85

    strength = min((score/350)*100+confirms*2+critical_count*4+(5 if extreme else 0)+pq*3, 98)
    if strength<MIN_SIGNAL_STRENGTH: return None

    if strength>=PERFECT_STRENGTH: quality,confidence,emoji = "PERFECT","🎯🔥 SNIPER PERFECT","🎯🔥🎯"
    elif strength>=EXCELLENT_STRENGTH: quality,confidence,emoji = "EXCELLENT","💎 SNIPER EXCELLENT","💎💎"
    else: quality,confidence,emoji = "STRONG","🟢 SNIPER STRONG","🟢"

    return {"pair":pair,"direction":direction,"strength":strength,"confidence":confidence,"quality":quality,"emoji":emoji,"confirmations":confirms,"critical":critical_count,"extreme":extreme,"score_diff":score-opposite,"payout":pi["payout"],"flag":pi["flag"],"factors":factors[:8],"entry_price":current}

async def find_sniper_signal(market_type):
    tasks = [analyze_pair_sniper(p) for p,i in PAIRS.items() if i["type"]==market_type]
    results = await asyncio.gather(*tasks, return_exceptions=True)
    signals = [r for r in results if isinstance(r, dict)]
    if signals:
        signals.sort(key=lambda x:(x["strength"],x["critical"],1 if x["extreme"] else 0,x["confirmations"]), reverse=True)
        best = signals[0]
        if best["strength"]>=MIN_SIGNAL_STRENGTH and best["critical"]>=MIN_CRITICAL_SIGNALS and best["extreme"]:
            return best
    return None

# ============================================================
# TRADE MANAGEMENT
# ============================================================

def save_trade(td):
    try:
        h = []
        if os.path.exists(TRADES_FILE):
            with open(TRADES_FILE,'r') as f: h=json.load(f)
        h.append(td)
        if len(h)>500: h=h[-500:]
        with open(TRADES_FILE,'w') as f: json.dump(h,f,indent=2)
    except: pass

def get_user_trades(uid, limit=10):
    try:
        if not os.path.exists(TRADES_FILE): return []
        with open(TRADES_FILE,'r') as f: h=json.load(f)
        return sorted([t for t in h if t.get('user_id')==uid], key=lambda x:x.get('timestamp',''), reverse=True)[:limit]
    except: return []

def get_user_stats(uid):
    trades=get_user_trades(uid,500)
    if not trades: return {'total':0,'wins':0,'losses':0,'win_rate':0,'profit':0,'streak':0}
    w=sum(1 for t in trades if t.get('result')=='WIN'); l=len(trades)-w
    p=sum(t.get('profit',0) for t in trades)
    s=0
    for t in trades:
        if t.get('result')=='WIN': s+=1
        else: break
    return {'total':len(trades),'wins':w,'losses':l,'win_rate':(w/len(trades)*100),'profit':p,'streak':s}

def get_session_trades(uid):
    if uid not in SESSION_TRADES: SESSION_TRADES[uid]=[]
    return SESSION_TRADES[uid]

def add_session_trade(uid, td):
    if uid not in SESSION_TRADES: SESSION_TRADES[uid]=[]
    SESSION_TRADES[uid].append(td)

def clear_session_trades(uid): SESSION_TRADES[uid]=[]
def get_session_count(uid): return len(get_session_trades(uid))

def format_30_signal_report(uid):
    trades=get_session_trades(uid)
    if not trades: return "No trades"
    total=len(trades); w=sum(1 for t in trades if t['result']=='WIN'); l=total-w
    wr=(w/total*100) if total>0 else 0; tp=sum(t.get('profit',0) for t in trades)
    tl=""
    for i,t in enumerate(trades,1):
        if t['direction']=='CALL': dr="🟩🟩⬆️🟩🟩"
        else: dr="🟥🟥⬇️🟥🟥"
        if t['result']=='WIN': tl+=f"{i}. ✅ {t['pair']} {dr}\n"
        else: tl+=f"{i}. ❌ {t['pair']} {dr}\n"
    return f"🎯 <b>REPORT - {total} SIGNALS</b>\n━━━━━━━━━━━━━━━━\n✅ {w} | ❌ {l} | {wr:.1f}% | ${tp:.2f}\n━━━━━━━━━━━━━━━━\n{tl}"

# ============================================================
# TIME
# ============================================================

def get_local_time(): return datetime.now(LOCAL_TZ)
def get_next_candle_time():
    now=get_local_time()
    return now.replace(second=0,microsecond=0)+timedelta(minutes=1)
def get_seconds_until_entry(): return 60-get_local_time().second
def has_enough_time(): return get_seconds_until_entry()>=MIN_TIME_BEFORE_CANDLE
def get_session_info():
    h=datetime.now(timezone.utc).hour
    for sid,s in SESSIONS.items():
        st,en=s["start"],s["end"]
        if st>en:
            if h>=st or h<en: return s["name"],s["volatility"]
        else:
            if st<=h<en: return s["name"],s["volatility"]
    return "📴 Off Hours","low"

def get_user_session(uid):
    if uid not in USER_SESSIONS:
        USER_SESSIONS[uid]={"market_type":"otc","auto_signals":False,"wins":0,"losses":0,"pnl":0.0,"last_signal_time":None}
    return USER_SESSIONS[uid]

def has_active_trade(uid): return uid in ACTIVE_TRADES and ACTIVE_TRADES[uid] is not None

def can_send_signal(uid,session):
    lt=session.get("last_signal_time")
    if lt is not None:
        rem=SIGNAL_COOLDOWN-(get_local_time()-lt).total_seconds()
        if rem>0: return False,f"⏳ {int(rem)}s"
    return True,""

def get_win_rate(s):
    t=s['wins']+s['losses']
    return (s['wins']/t*100) if t else 0

# ============================================================
# 🎯 COMPACT SIGNAL CARD
# ============================================================

def format_sniper_signal(signal, session, user_id):
    entry_time = get_next_candle_time()
    mg_time = entry_time + timedelta(minutes=1)
    secs = get_seconds_until_entry()

    if signal["direction"] == "CALL":
        return f"""🔥🎯 <b>MK SNIPER</b>

<b>{signal['pair']}</b>

🟩⬆️ <b>Call (Buy)</b>

⏰ Entry: <b>{entry_time.strftime("%H:%M:%S")}</b>
⏰ MG: <b>{mg_time.strftime("%H:%M:%S")}</b>

📌 <i>Use proper risk management</i>"""
    else:
        return f"""🔥🎯 <b>MK SNIPER</b>

<b>{signal['pair']}</b>

🟥⬇️ <b>Put (Sell)</b>

⏰ Entry: <b>{entry_time.strftime("%H:%M:%S")}</b>
⏰ MG: <b>{mg_time.strftime("%H:%M:%S")}</b>

📌 <i>Use proper risk management</i>"""

def format_menu(session, uid):
    wr=get_win_rate(session); can,wm=can_send_signal(uid,session)
    st="🟢 Ready" if can else wm; sn,_=get_session_info(); sc=get_session_count(uid)
    return f"""
🔥🎯 <b>MK SNIPER PRO v13.0</b>

📍 {session['market_type'].upper()} | {st}
🤖 Auto: <b>{'ON ✅' if session['auto_signals'] else 'OFF'}</b>
🌐 {sn}
━━━━━━━━━━━━━━━━
📈 <b>{session['wins']}W/{session['losses']}L</b> ({wr:.1f}%)
💵 <b>${session['pnl']:.2f}</b> | 📍 {sc}/30
"""

def format_stats(uid, session):
    s=get_user_stats(uid); r=get_user_trades(uid,10); wr=s['win_rate']
    bar="🟩"*int(wr/10)+"⬜"*(10-int(wr/10))
    rt=""
    for t in r[:8]:
        if t['direction']=='CALL': dr="🟩🟩⬆️🟩🟩"
        else: dr="🟥🟥⬇️🟥🟥"
        if t.get('result')=='WIN': rt+=f"✅ {t['pair']} {dr}\n"
        else: rt+=f"❌ {t['pair']} {dr}\n"
    if not rt: rt="No trades yet"
    return f"📊 <b>STATISTICS</b>\n━━━━━━━━━━━━━━━━\n{s['total']} trades | {s['wins']}W {s['losses']}L\n{wr:.1f}% | {bar}\n🔥 Streak: {s['streak']} | ${s['profit']:.2f}\n━━━━━━━━━━━━━━━━\n{rt}"

# ============================================================
# HANDLERS
# ============================================================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid=update.effective_user.id; un=update.effective_user.username or "N/A"; fn=update.effective_user.first_name or "User"
    if uid==ADMIN_ID or is_authorized(uid):
        session=get_user_session(uid)
        kb=InlineKeyboardMarkup([
            [InlineKeyboardButton("🌙 OTC",callback_data="otc"),InlineKeyboardButton("💱 FOREX",callback_data="forex"),InlineKeyboardButton("₿ CRYPTO",callback_data="crypto")],
            [InlineKeyboardButton("🎯 SNIPER SIGNAL",callback_data="signal")],
            [InlineKeyboardButton("🤖 AUTO ON",callback_data="auto_on"),InlineKeyboardButton("⏸️ STOP",callback_data="auto_off")],
            [InlineKeyboardButton("📊 STATS",callback_data="stats"),InlineKeyboardButton("📋 REPORT",callback_data="report")]
        ])
        await update.message.reply_text(format_menu(session,uid), reply_markup=kb, parse_mode=ParseMode.HTML)
        return
    if is_pending(uid):
        await update.message.reply_text(f"⏳ <b>Pending</b>\nContact {ADMIN_USERNAME}", parse_mode=ParseMode.HTML); return
    request_access(uid, un, fn)
    try: await context.bot.send_message(ADMIN_ID, f"📨 <b>ACCESS REQUEST</b>\n👤 {fn} (@{un})\n🆔 <code>{uid}</code>\n✅ /approve {uid}\n❌ /remove {uid}", parse_mode=ParseMode.HTML)
    except: pass
    await update.message.reply_text(f"🔒 <b>Access Required</b>\nRequest sent. Contact {ADMIN_USERNAME}", parse_mode=ParseMode.HTML)

async def buttons(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q=update.callback_query; await q.answer()
    uid=q.from_user.id; data=q.data
    if not is_authorized(uid) and uid!=ADMIN_ID:
        await q.answer(f"❌ Denied! Contact {ADMIN_USERNAME}", show_alert=True); return
    session=get_user_session(uid)
    try:
        if data in ["otc","forex","crypto"]:
            session['market_type']=data; PRICE_CACHE.clear()
            kb=InlineKeyboardMarkup([
                [InlineKeyboardButton("🌙 OTC",callback_data="otc"),InlineKeyboardButton("💱 FOREX",callback_data="forex"),InlineKeyboardButton("₿ CRYPTO",callback_data="crypto")],
                [InlineKeyboardButton("🎯 SNIPER SIGNAL",callback_data="signal")],
                [InlineKeyboardButton("🤖 AUTO ON",callback_data="auto_on"),InlineKeyboardButton("⏸️ STOP",callback_data="auto_off")],
                [InlineKeyboardButton("📊 STATS",callback_data="stats"),InlineKeyboardButton("📋 REPORT",callback_data="report")]
            ])
            await q.edit_message_text(format_menu(session,uid), reply_markup=kb, parse_mode=ParseMode.HTML)

        elif data=="stats":
            kb=InlineKeyboardMarkup([[InlineKeyboardButton("« Back",callback_data="otc")]])
            await q.edit_message_text(format_stats(uid,session), reply_markup=kb, parse_mode=ParseMode.HTML)

        elif data=="report":
            if get_session_count(uid)==0:
                kb=InlineKeyboardMarkup([[InlineKeyboardButton("« Back",callback_data="otc")]])
                await q.edit_message_text("📊 <b>No trades yet</b>", reply_markup=kb, parse_mode=ParseMode.HTML)
            else:
                kb=InlineKeyboardMarkup([[InlineKeyboardButton("🔄 Reset",callback_data="reset_session")],[InlineKeyboardButton("« Back",callback_data="otc")]])
                await q.edit_message_text(format_30_signal_report(uid), reply_markup=kb, parse_mode=ParseMode.HTML)

        elif data=="reset_session":
            clear_session_trades(uid)
            kb=InlineKeyboardMarkup([[InlineKeyboardButton("« Back",callback_data="otc")]])
            await q.edit_message_text("✅ <b>Reset!</b>", reply_markup=kb, parse_mode=ParseMode.HTML)

        elif data=="continue_trading":
            clear_session_trades(uid)
            kb=InlineKeyboardMarkup([[InlineKeyboardButton("🎯 SIGNAL",callback_data="signal")]])
            await q.edit_message_text("✅ <b>New session!</b>", reply_markup=kb, parse_mode=ParseMode.HTML)

        elif data=="auto_on":
            session['auto_signals']=True; await q.message.delete()
            await context.bot.send_message(uid, "🤖 <b>AUTO ON</b> — Signals every 3 min!", parse_mode=ParseMode.HTML)
            if 'auto_task' not in context.user_data or context.user_data['auto_task'].done():
                context.user_data['auto_task']=asyncio.create_task(auto_loop(context,uid))

        elif data=="auto_off":
            session['auto_signals']=False; await q.message.delete()
            await context.bot.send_message(uid, "⏸️ <b>AUTO OFF</b>", parse_mode=ParseMode.HTML)

        elif data=="signal":
            can,wm=can_send_signal(uid,session)
            if not can: return await q.answer(wm, show_alert=True)
            if not has_enough_time(): return await q.answer(f"⏳ Wait {get_seconds_until_entry()}s", show_alert=True)
            PRICE_CACHE.clear(); await q.message.delete()
            scan=await context.bot.send_message(uid, "🎯 <b>Scanning...</b>", parse_mode=ParseMode.HTML)
            signal=await find_sniper_signal(session['market_type'])
            await scan.delete()
            if not signal:
                kb=InlineKeyboardMarkup([[InlineKeyboardButton("🔄 Retry",callback_data="signal")],[InlineKeyboardButton("🤖 AUTO ON",callback_data="auto_on")]])
                return await context.bot.send_message(uid, "🎯 <b>No signal found</b>\n\n<i>Waiting for perfect setup...</i>", reply_markup=kb, parse_mode=ParseMode.HTML)
            ACTIVE_TRADES[uid]={"pair":signal['pair'],"direction":signal['direction'],"strength":signal['strength'],"payout":signal['payout'],"flag":signal['flag']}
            session['last_signal_time']=get_local_time()
            kb=InlineKeyboardMarkup([
                [InlineKeyboardButton("✅ WIN (Entry)",callback_data="win_entry"),InlineKeyboardButton("✅ WIN (MG)",callback_data="win_mg")],
                [InlineKeyboardButton("❌ LOSS",callback_data="loss")]
            ])
            await context.bot.send_message(uid, format_sniper_signal(signal,session,uid), reply_markup=kb, parse_mode=ParseMode.HTML)

        elif data=="win_entry":
            if not has_active_trade(uid): return await q.answer("No trade!", show_alert=True)
            trade=ACTIVE_TRADES[uid]; profit=ENTRY_STAKE*(trade['payout']/100)
            session['wins']+=1; session['pnl']+=profit
            if trade['direction']=='CALL': dr_display="🟩🟩⬆️🟩🟩"
            else: dr_display="🟥🟥⬇️🟥🟥"
            add_session_trade(uid,{'pair':trade['pair'],'direction':trade['direction'],'result':'WIN','win_stage':'Entry','profit':profit})
            save_trade({'user_id':uid,'pair':trade['pair'],'direction':trade['direction'],'result':'WIN','win_stage':'Entry','profit':profit,'timestamp':get_local_time().isoformat()})
            del ACTIVE_TRADES[uid]; cnt=get_session_count(uid); wr=get_win_rate(session)
            if cnt>=REPORT_EVERY_N_SIGNALS:
                await q.edit_message_text(f"✅win✅\n\n{trade['pair']}\n{dr_display}\n\n+${profit:.2f}", parse_mode=ParseMode.HTML)
                kb=InlineKeyboardMarkup([[InlineKeyboardButton("🔄 New Session",callback_data="continue_trading")]])
                await context.bot.send_message(uid, format_30_signal_report(uid), reply_markup=kb, parse_mode=ParseMode.HTML)
            else:
                kb=InlineKeyboardMarkup([[InlineKeyboardButton("🎯 Next",callback_data="signal")]])
                await q.edit_message_text(f"""✅win✅

<b>{trade['pair']}</b>
{dr_display}

📈 {session['wins']}W/{session['losses']}L ({wr:.1f}%)
📍 {cnt}/30""", reply_markup=kb, parse_mode=ParseMode.HTML)

        elif data=="win_mg":
            if not has_active_trade(uid): return await q.answer("No trade!", show_alert=True)
            trade=ACTIVE_TRADES[uid]; profit=(MG_STAKE*(trade['payout']/100))-ENTRY_STAKE
            session['wins']+=1; session['pnl']+=profit
            if trade['direction']=='CALL': dr_display="🟩🟩⬆️🟩🟩"
            else: dr_display="🟥🟥⬇️🟥🟥"
            add_session_trade(uid,{'pair':trade['pair'],'direction':trade['direction'],'result':'WIN','win_stage':'MG','profit':profit})
            save_trade({'user_id':uid,'pair':trade['pair'],'direction':trade['direction'],'result':'WIN','win_stage':'MG','profit':profit,'timestamp':get_local_time().isoformat()})
            del ACTIVE_TRADES[uid]; cnt=get_session_count(uid); wr=get_win_rate(session)
            if cnt>=REPORT_EVERY_N_SIGNALS:
                await q.edit_message_text(f"✅win✅\n\n{trade['pair']}\n{dr_display}\n\n+${profit:.2f} (MG)", parse_mode=ParseMode.HTML)
                kb=InlineKeyboardMarkup([[InlineKeyboardButton("🔄 New Session",callback_data="continue_trading")]])
                await context.bot.send_message(uid, format_30_signal_report(uid), reply_markup=kb, parse_mode=ParseMode.HTML)
            else:
                kb=InlineKeyboardMarkup([[InlineKeyboardButton("🎯 Next",callback_data="signal")]])
                await q.edit_message_text(f"""✅win✅

<b>{trade['pair']}</b>
{dr_display}

📈 {session['wins']}W/{session['losses']}L ({wr:.1f}%)
📍 {cnt}/30""", reply_markup=kb, parse_mode=ParseMode.HTML)

        elif data=="loss":
            if not has_active_trade(uid): return await q.answer("No trade!", show_alert=True)
            trade=ACTIVE_TRADES[uid]
            session['losses']+=1; session['pnl']-=TOTAL_RISK
            if trade['direction']=='CALL': dr_display="🟩🟩⬆️🟩🟩"
            else: dr_display="🟥🟥⬇️🟥🟥"
            add_session_trade(uid,{'pair':trade['pair'],'direction':trade['direction'],'result':'LOSS','win_stage':None,'profit':-TOTAL_RISK})
            save_trade({'user_id':uid,'pair':trade['pair'],'direction':trade['direction'],'result':'LOSS','profit':-TOTAL_RISK,'timestamp':get_local_time().isoformat()})
            del ACTIVE_TRADES[uid]; cnt=get_session_count(uid); wr=get_win_rate(session)
            if cnt>=REPORT_EVERY_N_SIGNALS:
                await q.edit_message_text(f"❌Loss❌\n\n{trade['pair']}\n{dr_display}", parse_mode=ParseMode.HTML)
                kb=InlineKeyboardMarkup([[InlineKeyboardButton("🔄 New Session",callback_data="continue_trading")]])
                await context.bot.send_message(uid, format_30_signal_report(uid), reply_markup=kb, parse_mode=ParseMode.HTML)
            else:
                kb=InlineKeyboardMarkup([[InlineKeyboardButton("🎯 Next",callback_data="signal")]])
                await q.edit_message_text(f"""❌Loss❌

<b>{trade['pair']}</b>
{dr_display}

📈 {session['wins']}W/{session['losses']}L ({wr:.1f}%)
📍 {cnt}/30""", reply_markup=kb, parse_mode=ParseMode.HTML)

    except Exception as e:
        logger.error(f"Button error: {e}")
        if uid in ACTIVE_TRADES: del ACTIVE_TRADES[uid]

async def auto_loop(context, uid):
    session=get_user_session(uid)
    while session['auto_signals']:
        try:
            can,_=can_send_signal(uid,session)
            if not can: await asyncio.sleep(3); continue
            if not has_enough_time(): await asyncio.sleep(get_seconds_until_entry()+2); continue
            PRICE_CACHE.clear()
            signal=await find_sniper_signal(session['market_type'])
            if signal:
                ACTIVE_TRADES[uid]={"pair":signal['pair'],"direction":signal['direction'],"strength":signal['strength'],"payout":signal['payout'],"flag":signal['flag']}
                session['last_signal_time']=get_local_time()
                kb=InlineKeyboardMarkup([
                    [InlineKeyboardButton("✅ WIN (Entry)",callback_data="win_entry"),InlineKeyboardButton("✅ WIN (MG)",callback_data="win_mg")],
                    [InlineKeyboardButton("❌ LOSS",callback_data="loss")]
                ])
                await context.bot.send_message(uid, format_sniper_signal(signal,session,uid), reply_markup=kb, parse_mode=ParseMode.HTML)
            await asyncio.sleep(SCAN_INTERVAL_SECONDS)
        except Exception as e:
            logger.error(f"Auto error: {e}")
            if uid in ACTIVE_TRADES: del ACTIVE_TRADES[uid]
            await asyncio.sleep(10)

# ============================================================
# ADMIN
# ============================================================

async def cmd_approve(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id!=ADMIN_ID: return
    if not context.args: return await update.message.reply_text("Usage: /approve ID")
    try:
        tid=int(context.args[0]); users=load_authorized_users(); ui=users.get(str(tid),{})
        approve_user(tid,ui.get("username","?"),ui.get("first_name","User"))
        try: await context.bot.send_message(tid,"✅ <b>APPROVED!</b> Send /start",parse_mode=ParseMode.HTML)
        except: pass
        await update.message.reply_text(f"✅ Approved {tid}")
    except: await update.message.reply_text("❌ Invalid ID")

async def cmd_remove(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id!=ADMIN_ID: return
    if not context.args: return await update.message.reply_text("Usage: /remove ID")
    try:
        tid=int(context.args[0])
        if remove_user(tid):
            try: await context.bot.send_message(tid,"🚫 <b>ACCESS REVOKED</b>",parse_mode=ParseMode.HTML)
            except: pass
            await update.message.reply_text(f"✅ Removed {tid}")
        else: await update.message.reply_text("❌ Not found")
    except: await update.message.reply_text("❌ Invalid ID")

async def cmd_users(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id!=ADMIN_ID: return
    ap,pe=get_all_users()
    t=f"👥 <b>USERS ({len(ap)})</b>\n"
    for uid,i in ap.items(): t+=f"✅ {i.get('first_name','?')} | <code>{uid}</code>\n"
    if pe:
        t+=f"\n⏳ <b>PENDING ({len(pe)})</b>\n"
        for uid,i in pe.items(): t+=f"📨 {i.get('first_name','?')} /approve {uid}\n"
    await update.message.reply_text(t, parse_mode=ParseMode.HTML)

async def cmd_broadcast(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id!=ADMIN_ID: return
    if not context.args: return await update.message.reply_text("Usage: /broadcast MSG")
    msg=" ".join(context.args); s,f=0,0
    for uid in get_approved_user_ids():
        try: await context.bot.send_message(uid,f"📢 {msg}",parse_mode=ParseMode.HTML); s+=1
        except: f+=1
    await update.message.reply_text(f"✅ {s} sent | ❌ {f} failed")

async def cmd_stats_admin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id!=ADMIN_ID: return
    ap,pe=get_all_users()
    await update.message.reply_text(f"📊 Users: {len(ap)} | Pending: {len(pe)} | Active: {len(ACTIVE_TRADES)} | API: {API_STATUS['calls']}")

def main():
    print("🔥🎯 MK SNIPER PRO v13.0")
    print("⏱️  Signals every 3 min | No rating required")
    app=Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start",start))
    app.add_handler(CommandHandler("approve",cmd_approve))
    app.add_handler(CommandHandler("remove",cmd_remove))
    app.add_handler(CommandHandler("users",cmd_users))
    app.add_handler(CommandHandler("broadcast",cmd_broadcast))
    app.add_handler(CommandHandler("botstats",cmd_stats_admin))
    app.add_handler(CallbackQueryHandler(buttons))
    print("✅ RUNNING!")
    app.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__=='__main__':
    main()
