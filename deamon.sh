#!/bin/bash
# DealwalaIndia 24/7 Daemon - auto-restarts on crash
while true; do
  /usr/bin/python3 /root/dealwalaindia/post_deals.py >> /root/dealwalaindia/cron.log 2>&1
  sleep 900
done
