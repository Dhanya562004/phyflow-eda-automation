#!/usr/bin/env bash
# PHYFlow Bash Regression Suite Execution Script
set -e

echo "=================================================================="
echo " PHYFlow EDA Automation — POSIX Shell Regression Runner"
echo "=================================================================="

# Environment Check
echo "[1/3] Validating Python environment and PHYFlow installation..."
if ! command -v python3 &> /dev/null; then
    echo "[ERROR] python3 could not be found. Please install Python 3.11+."
    exit 1
fi

# Tool Check
echo "[2/3] Checking tool availability via PHYFlow CLI..."
python3 -m phyflow cli check-tools || true

# Execute Regression Matrix
echo "[3/3] Executing parallel regression suite across designs and corners..."
python3 -m phyflow cli regression --config configs/regression.yaml --workers 4

echo "=================================================================="
echo " PHYFlow Regression Suite Finished Successfully"
echo "=================================================================="
