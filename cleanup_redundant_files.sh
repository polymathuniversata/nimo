#!/bin/bash
# Script to remove redundant files identified in the audit

echo "Removing redundant git log files..."
rm -f "h --set-upstream origin final --force-with-lease"
rm -f "h origin final"
rm -f "s RETURN"
rm -f "tatus"

echo "Removing redundant backend files..."
cd backend
rm -f simple_app.py debug_app.py simple_demo.py

echo "Removing legacy Ethereum tooling..."
cd ../contracts
rm -f foundry.lock foundry.toml hardhat.config.js
rm -rf lib/forge-std
rm -rf lib/openzeppelin-contracts

echo "Cleanup completed!"
