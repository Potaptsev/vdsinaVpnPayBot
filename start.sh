#!/bin/bash
pip uninstall -y telegram || true
pip install -r requirements.txt
python3 subscription_bot.py
