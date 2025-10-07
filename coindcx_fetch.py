import hmac
import hashlib
import base64
import json
import time
import requests
import pandas as pd
from PyQt5 import QtCore, QtGui, QtWidgets
import threading

# Enter your API Key and Secret here. If you don't have one, you can generate it from the website.
key = "f460e64e1facf9600f2030f5ea86982129217d11ccf43548"
secret = "f3f88d00e66aa186b3c40d34587ae003aa2ab9c57537861fb0af5a19be79ef5d"

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

def ltp(IDNAME):
    
    url = f"https://api.coindcx.com/exchange/v1/derivatives/futures/data/trades?pair={IDNAME}"
    #sample_url = "https://api.coindcx.com/exchange/v1/derivatives/futures/data/trades?pair=B-MKR_USDT"
    response = requests.get(url)
    data = response.json()
    df = data[0]['price']
    return df

class GlassWidget(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()

        # Frameless, always on top, no taskbar icon
        self.setWindowFlags(
            QtCore.Qt.FramelessWindowHint |
            QtCore.Qt.Tool |
            QtCore.Qt.WindowStaysOnTopHint |
            QtCore.Qt.X11BypassWindowManagerHint
        )
        self.setAttribute(QtCore.Qt.WA_TranslucentBackground)

        # --- Style ---
        self.resize(260, 200)
        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)

        self.bg = QtWidgets.QFrame()
        self.bg.setStyleSheet("""
            QFrame {
                background-color: rgba(25, 25, 25, 180);
                border-radius: 16px;
                border: 1px solid rgba(100, 255, 100, 40);
            }
        """)
        bg_layout = QtWidgets.QVBoxLayout(self.bg)
        self.label = QtWidgets.QLabel("Loading...", self)
        self.label.setStyleSheet("color: #00ff88; font: 14px Consolas;")
        bg_layout.addWidget(self.label)
        layout.addWidget(self.bg)

        # --- Make widget draggable ---
        self.offset = None
        self.bg.mousePressEvent = self.start_move
        self.bg.mouseMoveEvent = self.moving

        # --- Start background thread to update data ---
        threading.Thread(target=self.update_loop, daemon=True).start()

    def start_move(self, event):
        if event.button() == QtCore.Qt.LeftButton:
            self.offset = event.pos()

    def moving(self, event):
        if self.offset is not None and event.buttons() == QtCore.Qt.LeftButton:
            self.move(self.pos() + event.pos() - self.offset)

while True:
    rt = getpos()  # your list of dictionaries
    lines = []

    for entry in rt:
        if entry['active_pos'] != 0:  # only include if active_pos is not 0
            pair_value = entry['pair']
            result = ltp(pair_value)
            avgprice = entry['avg_price']
            actvpos = entry['active_pos']
            l_u_m = entry['locked_user_margin']
            



            pnlusdt = (result - avgprice) * actvpos
            pnl_inr = pnlusdt * usdt_inr  # convert USDT profit/loss to INR
            ROE = (pnlusdt / l_u_m) * 100  if l_u_m != 0 else 0 # calculate ROE
            color = "00FF00" if ROE > 0 else "FF0000"  # green if >0 else red
            lines.append(f"Name: {pair_value}, PNL: {pnlusdt:.4f} USDT | {pnl_inr:.2f} INR | ROE: {ROE:.2f}%")
    text = "\n".join(lines) if lines else "No active positions"
    self.update_text(text)
    time.sleep(5)



