"""Download cohort.db from the course repo into data/.

Run from the repo root:
    python scripts/get_data.py
"""
import urllib.request
from pathlib import Path

URL = ("https://github.com/gwcbi/applied-computing-HDS/raw/main/"
       "data/raw/lab4-cbioportal-luad/cohort.db")
DEST = Path("data/cohort.db")

if DEST.exists():
    print(f"{DEST} already exists, skipping download")
else:
    DEST.parent.mkdir(exist_ok=True)
    print(f"downloading {URL}")
    urllib.request.urlretrieve(URL, DEST)
    print(f"saved {DEST} ({DEST.stat().st_size / 1e6:.1f} MB)")