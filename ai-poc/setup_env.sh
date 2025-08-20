#!/usr/bin/env bash
set -e
python3.11 -m venv report_poc_sample
source report_poc_sample/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
echo "VENV READY. Activated with: source report_poc_sample/bin/activate"
