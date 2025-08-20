py -3.11 -m venv report_poc_sample
. .\report_poc_sample\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
Write-Output "VENV READY. Activate next time with: .\report_poc_sample\Scripts\Activate.ps1"
