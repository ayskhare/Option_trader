# download_historical.py
# ─────────────────────────────────────────────
# Incrementally updates daily OHLC data for:
#   - Nifty 50
#   - Bank Nifty
#   - Nifty Midcap 50
#   - India VIX
#
# For each instrument:
#   1. Reads existing CSV
#   2. Finds the latest saved date
#   3. Creates a dated backup in data/backup/
#   4. Fetches only missing data
#   5. Appends new data
#   6. Removes duplicates
#   7. Saves back to the original CSV
# ─────────────────────────────────────────────

import os
import time
import shutil
import pandas as pd

from datetime import datetime, timedelta
from connection import get_connection


# ── Folders ───────────────────────────────────

DATA_FOLDER = "data"
BACKUP_FOLDER = os.path.join(DATA_FOLDER, "backup")

os.makedirs(DATA_FOLDER, exist_ok=True)


print("BACKUP_FOLDER:", BACKUP_FOLDER)
print("Exists:", os.path.exists(BACKUP_FOLDER))
print("Is directory:", os.path.isdir(BACKUP_FOLDER))
print("Is file:", os.path.isfile(BACKUP_FOLDER))
os.makedirs(BACKUP_FOLDER, exist_ok=True)


# ── Instruments ───────────────────────────────

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


# ── Fetch settings ────────────────────────────

# Used only if an original CSV does not exist
INITIAL_FROM_DATE = datetime(2021, 1, 1)

TO_DATE = datetime.now()

# AngelOne daily candle limit
CHUNK_DAYS = 365


def fetch_daily_chunk(
    api,
    instrument: dict,
    from_dt: datetime,
    to_dt: datetime
) -> pd.DataFrame:
    """Fetch one chunk of daily OHLC data."""

    params = {
        "exchange": instrument["exchange"],
        "symboltoken": instrument["token"],
        "interval": "ONE_DAY",
        "fromdate": from_dt.strftime("%Y-%m-%d 09:15"),
        "todate": to_dt.strftime("%Y-%m-%d 15:30"),
    }

    try:
        resp = api.getCandleData(params)

        if resp and resp.get("status") is True:

            raw = resp.get("data", [])

            if not raw:
                return pd.DataFrame()

            df = pd.DataFrame(
                raw,
                columns=[
                    "datetime",
                    "open",
                    "high",
                    "low",
                    "close",
                    "volume"
                ]
            )

            df["datetime"] = (
                pd.to_datetime(df["datetime"])
                .dt.tz_localize(None)
            )

            for col in [
                "open",
                "high",
                "low",
                "close",
                "volume"
            ]:
                df[col] = pd.to_numeric(
                    df[col],
                    errors="coerce"
                )

            df.dropna(inplace=True)

            df.sort_values(
                "datetime",
                inplace=True
            )

            df.reset_index(
                drop=True,
                inplace=True
            )

            return df

        else:

            message = (
                resp.get("message", "Unknown")
                if resp
                else "No response"
            )

            print(f"    API error: {message}")

            return pd.DataFrame()

    except Exception as e:

        print(f"    Exception: {e}")

        return pd.DataFrame()


def fetch_data(
    api,
    instrument: dict,
    from_date: datetime,
    to_date: datetime
) -> pd.DataFrame:
    """
    Fetch data between two dates.

    Automatically splits long periods into chunks.
    """

    all_chunks = []

    current_from = from_date

    while current_from <= to_date:

        current_to = min(
            current_from + timedelta(days=CHUNK_DAYS),
            to_date
        )

        print(
            f"  Fetching "
            f"{current_from.strftime('%Y-%m-%d')} "
            f"→ "
            f"{current_to.strftime('%Y-%m-%d')}",
            end=" "
        )

        chunk = fetch_daily_chunk(
            api,
            instrument,
            current_from,
            current_to
        )

        if not chunk.empty:

            all_chunks.append(chunk)

            print(
                f"→ {len(chunk)} candles ✅"
            )

        else:

            print("→ No data")

        current_from = (
            current_to
            + timedelta(days=1)
        )

        time.sleep(0.5)

    if not all_chunks:

        return pd.DataFrame()

    df = pd.concat(
        all_chunks,
        ignore_index=True
    )

    df.drop_duplicates(
        subset=["datetime"],
        inplace=True
    )

    df.sort_values(
        "datetime",
        inplace=True
    )

    df.reset_index(
        drop=True,
        inplace=True
    )

    return df


def create_backup(
    file_path: str,
    last_date: datetime
):
    """
    Copy the existing CSV into data/backup/
    using the last available date.

    Example:
    nifty50_daily.csv
    →
    data/backup/nifty50_daily_24aug.csv
    """

    filename = os.path.basename(file_path)

    name, extension = os.path.splitext(filename)

    date_suffix = last_date.strftime("%d%b%Y").lower()

    backup_filename = (
        f"{name}_{date_suffix}{extension}"
    )

    backup_path = os.path.join(
        BACKUP_FOLDER,
        backup_filename
    )

    shutil.copy2(
        file_path,
        backup_path
    )

    print(
        f"  Backup created → {backup_path}"
    )

    return backup_path


def update_instrument(
    api,
    instrument: dict
):

    print("\n" + "=" * 55)

    print(
        f"Updating: {instrument['name']}"
    )

    print("=" * 55)

    file_path = instrument["file"]


    # ── CASE 1: Existing file ─────────────────

    if os.path.exists(file_path):

        existing_df = pd.read_csv(
            file_path
        )

        if existing_df.empty:

            print(
                "  Existing file is empty."
            )

            from_date = INITIAL_FROM_DATE

        else:

            existing_df["datetime"] = (
                pd.to_datetime(
                    existing_df["datetime"]
                )
                .dt.tz_localize(None)
            )

            last_datetime = (
                existing_df["datetime"].max()
            )

            print(
                f"  Latest saved date: "
                f"{last_datetime.strftime('%Y-%m-%d')}"
            )

            # ── Create backup ───────────────────

            create_backup(
                file_path,
                last_datetime
            )

            # Fetch only after latest date

            from_date = (
                last_datetime
                + timedelta(days=1)
            )


    # ── CASE 2: File doesn't exist ─────────────

    else:

        print(
            "  No existing file found."
        )

        print(
            f"  Starting from "
            f"{INITIAL_FROM_DATE.strftime('%Y-%m-%d')}"
        )

        existing_df = pd.DataFrame()

        from_date = INITIAL_FROM_DATE


    # ── Check if update required ───────────────

    to_date = datetime.now()

    if from_date.date() > to_date.date():

        print(
            "  Already up to date ✅"
        )

        return {
            "instrument": instrument["name"],
            "status": "Already up to date",
            "added": 0,
            "latest": last_datetime.strftime(
                "%Y-%m-%d"
            ),
        }


    print(
        f"  Updating range: "
        f"{from_date.strftime('%Y-%m-%d')} "
        f"→ "
        f"{to_date.strftime('%Y-%m-%d')}"
    )


    # ── Fetch new data ─────────────────────────

    new_df = fetch_data(
        api,
        instrument,
        from_date,
        to_date
    )


    # ── No new data ────────────────────────────

    if new_df.empty:

        print(
            "  No new candles received."
        )

        return {
            "instrument": instrument["name"],
            "status": "No new data",
            "added": 0,
            "latest": (
                existing_df["datetime"]
                .max()
                .strftime("%Y-%m-%d")
                if not existing_df.empty
                else "—"
            ),
        }


    # ── Append old + new data ──────────────────

    updated_df = pd.concat(
        [
            existing_df,
            new_df
        ],
        ignore_index=True
    )


    # ── Clean duplicates ───────────────────────

    updated_df["datetime"] = (
        pd.to_datetime(
            updated_df["datetime"]
        )
        .dt.tz_localize(None)
    )

    updated_df.drop_duplicates(
        subset=["datetime"],
        keep="last",
        inplace=True
    )

    updated_df.sort_values(
        "datetime",
        inplace=True
    )

    updated_df.reset_index(
        drop=True,
        inplace=True
    )


    # ── Save original file ─────────────────────

    updated_df.to_csv(
        file_path,
        index=False
    )


    print(
        f"\n  Added: {len(new_df)} candles"
    )

    print(
        f"  Total rows: {len(updated_df)}"
    )

    print(
        f"  Latest date: "
        f"{updated_df['datetime'].iloc[-1].strftime('%Y-%m-%d')}"
    )

    print(
        f"  Saved → {file_path} ✅"
    )


    return {
        "instrument": instrument["name"],
        "status": "Updated",
        "added": len(new_df),
        "latest": (
            updated_df["datetime"]
            .iloc[-1]
            .strftime("%Y-%m-%d")
        ),
    }


def main():

    print("\n" + "=" * 55)

    print(
        "NIFTY HISTORICAL DATA UPDATER"
    )

    print(
        f"Run time: "
        f"{datetime.now().strftime('%d %b %Y %H:%M')}"
    )

    print("=" * 55)


    # ── Connect once ───────────────────────────

    print("\nConnecting to AngelOne...")

    api = get_connection()

    print("Connected ✅")


    # ── Update all instruments ─────────────────

    summary = []

    for instrument in INSTRUMENTS:

        result = update_instrument(
            api,
            instrument
        )

        summary.append(result)

        # Small rate-limit buffer

        time.sleep(0.5)


    # ── Summary ────────────────────────────────

    print("\n" + "=" * 55)

    print(
        "UPDATE SUMMARY"
    )

    print("=" * 55)

    for item in summary:

        print(
            f"  {item['instrument']:<20} "
            f"{item['status']:<20} "
            f"Added: {item['added']:<5} "
            f"Latest: {item['latest']}"
        )

    print("\nDone ✅")


if __name__ == "__main__":
    main()
