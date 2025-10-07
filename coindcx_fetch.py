import hmac
import hashlib
import base64
import json
import time, sys
import requests
from PyQt6 import QtCore, QtGui, QtWidgets
from PyQt6.QtCore import Qt, QTimer, QCoreApplication, QThread

import threading

# Enter your API Key and Secret here. If you don't have one, you can generate it from the website.
key = "XXXX"
secret = "XXXX"

# python3
secret_bytes = bytes(secret, encoding='utf-8')

# Generating a timestamp
timeStamp = int(round(time.time() * 1000))
def getpos():
    
    body = {
            "timestamp":timeStamp , # EPOCH timestamp in seconds
            "page": "1", #no. of pages needed
            "size": "10",
            "margin_currency_short_name": ["INR"]
            }


    json_body = json.dumps(body, separators = (',', ':'))

    signature = hmac.new(secret_bytes, json_body.encode(), hashlib.sha256).hexdigest()

    url = "https://api.coindcx.com/exchange/v1/derivatives/futures/positions"

    headers = {
        'Content-Type': 'application/json',
        'X-AUTH-APIKEY': key,
        'X-AUTH-SIGNATURE': signature
    }

    response = requests.post(url, data = json_body, headers = headers)
    data = response.json()
    return data

ticker = requests.get("https://api.coindcx.com/exchange/ticker").json()
usdt_inr = next(float(i["last_price"]) for i in ticker if i["market"] == "USDTINR")

def write_data_csv(lines, file_path='data.txt'):
    """Write all rows to data.txt in CSV format expected by the Rainmeter skin.
    Each element of lines should already be a comma-separated string like:
    PAIR,PNL_USDT,PNL_INR,ROE
    """
    try:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write("\n".join(lines))
    except Exception as e:
        # Best-effort logging only; do not crash fetch loop
        print(f"Failed to write {file_path}: {e}")

def ltp(IDNAME):
    
    url = f"https://api.coindcx.com/exchange/v1/derivatives/futures/data/trades?pair={IDNAME}"
    #sample_url = "https://api.coindcx.com/exchange/v1/derivatives/futures/data/trades?pair=B-MKR_USDT"
    response = requests.get(url)
    data = response.json()
    df = data[0]['price']
    return df

while True:
    rt = getpos()
    rows = []

    for entry in rt:
        if entry['active_pos'] != 0:
            pair_value = entry['pair']
            last_price = ltp(pair_value)
            avgprice = entry['avg_price']
            actvpos = entry['active_pos']
            l_u_m = entry['locked_user_margin']

            pnlusdt = (last_price - avgprice) * actvpos
            pnl_inr = pnlusdt * usdt_inr
            roe = (pnlusdt / l_u_m) * 100 if l_u_m != 0 else 0.0

            row = f"{pair_value},{pnlusdt:.2f},{int(round(pnl_inr))},{roe:.2f}"
            rows.append(row)

    if rows:
        write_data_csv(rows, 'data.txt')
    else:
        # Clear file when no active positions
        write_data_csv([], 'data.txt')

    time.sleep(3)





