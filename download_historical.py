# download_historical.py
# ─────────────────────────────────────────────
# Incrementally updates daily OHLC data for:
#
#   - Nifty 50
#   - Bank Nifty
#   - Nifty Midcap 50
#   - India VIX
#
# For each instrument:
#
#   1. Read existing CSV
#   2. Find latest saved date
#   3. Fetch only missing data
#   4. Create backup before modifying the CSV
#   5. Append new data
#   6. Remove duplicates
#   7. Save updated CSV
# ─────────────────────────────────────────────

import os
import time
import shutil
import pandas as pd

from datetime import datetime, timedelta
from connection import get_connection


# ─────────────────────────────────────────────
# FOLDERS
# ─────────────────────────────────────────────

DATA_FOLDER = "data"
BACKUP_FOLDER = os.path.join(DATA_FOLDER, "backup")

os.makedirs(DATA_FOLDER, exist_ok=True)

if os.path.exists(BACKUP_FOLDER) and not os.path.isdir(BACKUP_FOLDER):
    raise RuntimeError(
        f"'{BACKUP_FOLDER}' exists but is a file. "
        "Delete or rename it and create a folder instead."
    )

os.makedirs(BACKUP_FOLDER, exist_ok=True)


# ─────────────────────────────────────────────
# INSTRUMENTS
# ─────────────────────────────────────────────

INSTRUMENTS = [
    {
        "name": "Nifty 50",
        "symbol": "Nifty 50",
        "token": "99926000",
        "exchange": "NSE",
        "file": "data/nifty50_daily.csv",
    },
    {
        "name": "Bank Nifty",
        "symbol": "Nifty Bank",
        "token": "99926009",
        "exchange": "NSE",
        "file": "data/banknifty_daily.csv",
    },
    {
        "name": "Nifty Midcap 50",
        "symbol": "NIFTY MIDCAP 50",
        "token": "99926014",
        "exchange": "NSE",
        "file": "data/nifty_midcap50_daily.csv",
    },
    {
        "name": "India VIX",
        "symbol": "India VIX",
        "token": "99926017",
        "exchange": "NSE",
        "file": "data/nifty_vix.csv",
    },
]


# ─────────────────────────────────────────────
# SETTINGS
# ─────────────────────────────────────────────

INITIAL_FROM_DATE = datetime(2021, 1, 1)

CHUNK_DAYS = 365

RATE_LIMIT_DELAY = 0.5


# ─────────────────────────────────────────────
# FETCH ONE CHUNK
# ─────────────────────────────────────────────

def fetch_daily_chunk(
    api,
    instrument,
    from_dt,
    to_dt
):

    params = {
        "exchange": instrument["exchange"],
        "symboltoken": instrument["token"],
        "interval": "ONE_DAY",
        "fromdate": from_dt.strftime("%Y-%m-%d 09:15"),
        "todate": to_dt.strftime("%Y-%m-%d 15:30"),
    }

    try:

        response = api.getCandleData(params)

        if not response or response.get("status") is not True:

            message = (
                response.get("message", "Unknown API error")
                if response
                else "No response from API"
            )

            print(f"    API error: {message}")

            return pd.DataFrame()

        raw_data = response.get("data", [])

        if not raw_data:
            return pd.DataFrame()

        df = pd.DataFrame(
            raw_data,
            columns=[
                "datetime",
                "open",
                "high",
                "low",
                "close",
                "volume",
            ],
        )

        df["datetime"] = pd.to_datetime(
            df["datetime"]
        ).dt.tz_localize(None)

        for column in [
            "open",
            "high",
            "low",
            "close",
            "volume",
        ]:

            df[column] = pd.to_numeric(
                df[column],
                errors="coerce",
            )

        df.dropna(inplace=True)

        df.drop_duplicates(
            subset=["datetime"],
            inplace=True,
        )

        df.sort_values(
            "datetime",
            inplace=True,
        )

        df.reset_index(
            drop=True,
            inplace=True,
        )

        return df

    except Exception as error:

        print(f"    Exception: {error}")

        return pd.DataFrame()


# ─────────────────────────────────────────────
# FETCH DATE RANGE
# ─────────────────────────────────────────────

def fetch_data(
    api,
    instrument,
    from_date,
    to_date,
):

    all_chunks = []

    current_from = from_date

    while current_from <= to_date:

        current_to = min(
            current_from + timedelta(days=CHUNK_DAYS),
            to_date,
        )

        print(
            f"  Fetching "
            f"{current_from.strftime('%Y-%m-%d')} "
            f"→ "
            f"{current_to.strftime('%Y-%m-%d')}"
        )

        chunk = fetch_daily_chunk(
            api,
            instrument,
            current_from,
            current_to,
        )

        if chunk.empty:

            print("    No candles received.")

        else:

            all_chunks.append(chunk)

            print(
                f"    Received {len(chunk)} candles ✅"
            )

        current_from = current_to + timedelta(days=1)

        time.sleep(RATE_LIMIT_DELAY)

    if not all_chunks:
        return pd.DataFrame()

    df = pd.concat(
        all_chunks,
        ignore_index=True,
    )

    df.drop_duplicates(
        subset=["datetime"],
        keep="last",
        inplace=True,
    )

    df.sort_values(
        "datetime",
        inplace=True,
    )

    df.reset_index(
        drop=True,
        inplace=True,
    )

    return df


# ─────────────────────────────────────────────
# CREATE BACKUP
# ─────────────────────────────────────────────

def create_backup(
    file_path,
    last_datetime,
):

    filename = os.path.basename(file_path)

    name, extension = os.path.splitext(filename)

    date_suffix = last_datetime.strftime(
        "%d%b%Y"
    ).lower()

    backup_filename = (
        f"{name}_{date_suffix}{extension}"
    )

    backup_path = os.path.join(
        BACKUP_FOLDER,
        backup_filename,
    )

    shutil.copy2(
        file_path,
        backup_path,
    )

    print(
        f"  Backup created: {backup_path}"
    )

    return backup_path


# ─────────────────────────────────────────────
# READ EXISTING DATA
# ─────────────────────────────────────────────

def read_existing_data(file_path):

    if not os.path.exists(file_path):

        print("  Existing file: Not found")

        return pd.DataFrame()

    existing_df = pd.read_csv(file_path)

    if existing_df.empty:

        print("  Existing file: Empty")

        return pd.DataFrame()

    existing_df["datetime"] = pd.to_datetime(
        existing_df["datetime"]
    ).dt.tz_localize(None)

    existing_df.drop_duplicates(
        subset=["datetime"],
        keep="last",
        inplace=True,
    )

    existing_df.sort_values(
        "datetime",
        inplace=True,
    )

    existing_df.reset_index(
        drop=True,
        inplace=True,
    )

    return existing_df


# ─────────────────────────────────────────────
# UPDATE ONE INSTRUMENT
# ─────────────────────────────────────────────

def update_instrument(
    api,
    instrument,
):

    print()
    print("=" * 60)
    print(f"UPDATING: {instrument['name']}")
    print("=" * 60)

    file_path = instrument["file"]

    existing_df = read_existing_data(file_path)

    # ── Existing file ─────────────────────────

    if not existing_df.empty:

        last_datetime = existing_df["datetime"].max()

        print(
            "  Latest saved date: "
            f"{last_datetime.strftime('%Y-%m-%d')}"
        )

        from_date = (
            last_datetime + timedelta(days=1)
        )

    # ── New file ──────────────────────────────

    else:

        last_datetime = None

        from_date = INITIAL_FROM_DATE

        print(
            "  Starting from: "
            f"{from_date.strftime('%Y-%m-%d')}"
        )

    to_date = datetime.now()

    # ── Already ahead ─────────────────────────

    if from_date.date() > to_date.date():

        print("  Already up to date ✅")

        return {
            "instrument": instrument["name"],
            "status": "Already up to date",
            "added": 0,
            "latest": (
                last_datetime.strftime("%Y-%m-%d")
                if last_datetime
                else "—"
            ),
        }

    print(
        "  Update range: "
        f"{from_date.strftime('%Y-%m-%d')} "
        "→ "
        f"{to_date.strftime('%Y-%m-%d')}"
    )

    # ── Fetch new data ────────────────────────

    new_df = fetch_data(
        api,
        instrument,
        from_date,
        to_date,
    )

    # ── No new data ───────────────────────────

    if new_df.empty:

        print("  No new data received.")

        return {
            "instrument": instrument["name"],
            "status": "No new data",
            "added": 0,
            "latest": (
                last_datetime.strftime("%Y-%m-%d")
                if last_datetime
                else "—"
            ),
        }

    # ── Backup only when modification happens ─

    if (
        not existing_df.empty
        and last_datetime is not None
    ):

        create_backup(
            file_path,
            last_datetime,
        )

    # ── Combine data ──────────────────────────

    updated_df = pd.concat(
        [
            existing_df,
            new_df,
        ],
        ignore_index=True,
    )

    updated_df["datetime"] = pd.to_datetime(
        updated_df["datetime"]
    ).dt.tz_localize(None)

    updated_df.drop_duplicates(
        subset=["datetime"],
        keep="last",
        inplace=True,
    )

    updated_df.sort_values(
        "datetime",
        inplace=True,
    )

    updated_df.reset_index(
        drop=True,
        inplace=True,
    )

    # ── Save ──────────────────────────────────

    updated_df.to_csv(
        file_path,
        index=False,
    )

    latest_date = updated_df[
        "datetime"
    ].iloc[-1].strftime("%Y-%m-%d")

    print()
    print(
        f"  New candles added: {len(new_df)}"
    )

    print(
        f"  Total rows: {len(updated_df)}"
    )

    print(
        f"  Latest available date: {latest_date}"
    )

    print(
        f"  Saved: {file_path} ✅"
    )

    return {
        "instrument": instrument["name"],
        "status": "Updated",
        "added": len(new_df),
        "latest": latest_date,
    }


# ─────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────

def main():

    started_at = datetime.now()

    print()
    print("=" * 60)
    print("NIFTY HISTORICAL DATA UPDATER")
    print("=" * 60)

    print(
        "Started: "
        f"{started_at.strftime('%d %b %Y %H:%M:%S')}"
    )

    print()

    print("Connecting to Angel One...")

    api = get_connection()

    print("Angel One connected ✅")

    summary = []

    for instrument in INSTRUMENTS:

        result = update_instrument(
            api,
            instrument,
        )

        summary.append(result)

        time.sleep(RATE_LIMIT_DELAY)

    finished_at = datetime.now()

    print()
    print("=" * 60)
    print("UPDATE SUMMARY")
    print("=" * 60)

    for item in summary:

        print(
            f"{item['instrument']:<20} | "
            f"{item['status']:<20} | "
            f"Added: {item['added']:<5} | "
            f"Latest: {item['latest']}"
        )

    print()

    print(
        "Finished: "
        f"{finished_at.strftime('%d %b %Y %H:%M:%S')}"
    )

    print("Historical data update completed ✅")


if __name__ == "__main__":
    main()
