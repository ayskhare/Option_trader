# calculate_metrics.py
# ─────────────────────────────────────────────
# Reads historical market data from ./data/
# Calculates derived technical metrics
# Saves results in ./data/derived/
# ─────────────────────────────────────────────

import os
import pandas as pd
import numpy as np


# ── Folders ──────────────────────────────────

DATA_FOLDER = "data"
OUTPUT_FOLDER = "data/derived"

os.makedirs(OUTPUT_FOLDER, exist_ok=True)


# ── Instruments ──────────────────────────────

INSTRUMENTS = [
    {
        "name": "Nifty 50",
        "input": "nifty50_daily.csv",
        "output": "nifty50_metrics.csv",
    },
    {
        "name": "Bank Nifty",
        "input": "banknifty_daily.csv",
        "output": "banknifty_metrics.csv",
    },
    {
        "name": "Nifty Midcap 50",
        "input": "nifty_midcap50_daily.csv",
        "output": "nifty_midcap50_metrics.csv",
    },
    {
        "name": "India VIX",
        "input": "nifty_vix.csv",
        "output": "nifty_vix_metrics.csv",
    },
]


def calculate_rsi(close, period=14):
    """
    Calculate Relative Strength Index.
    """

    delta = close.diff()

    gain = delta.where(
        delta > 0,
        0
    )

    loss = -delta.where(
        delta < 0,
        0
    )

    avg_gain = gain.rolling(
        window=period,
        min_periods=period
    ).mean()

    avg_loss = loss.rolling(
        window=period,
        min_periods=period
    ).mean()

    rs = avg_gain / avg_loss

    rsi = 100 - (
        100 / (1 + rs)
    )

    return rsi


def calculate_atr(df, period=14):
    """
    Calculate Average True Range.
    """

    previous_close = df["close"].shift(1)

    high_low = (
        df["high"] -
        df["low"]
    )

    high_close = (
        df["high"] -
        previous_close
    ).abs()

    low_close = (
        df["low"] -
        previous_close
    ).abs()

    true_range = pd.concat(
        [
            high_low,
            high_close,
            low_close
        ],
        axis=1
    ).max(axis=1)

    atr = true_range.rolling(
        window=period,
        min_periods=period
    ).mean()

    return atr


def calculate_metrics(df):
    """
    Calculate all derived metrics.
    """

    df = df.copy()

    df["datetime"] = pd.to_datetime(
        df["datetime"]
    )

    df.sort_values(
        "datetime",
        inplace=True
    )

    df.reset_index(
        drop=True,
        inplace=True
    )


    # ── Moving Averages ──────────────────────

    for period in [
        20,
        50,
        100,
        200
    ]:

        df[f"dma_{period}"] = (
            df["close"]
            .rolling(
                window=period,
                min_periods=period
            )
            .mean()
        )


    # ── Distance From Moving Averages ────────

    for period in [
        20,
        50,
        100,
        200
    ]:

        df[f"distance_dma_{period}_pct"] = (
            (
                df["close"] -
                df[f"dma_{period}"]
            )
            /
            df[f"dma_{period}"]
            * 100
        )


    # ── Returns ──────────────────────────────

    for period in [
        1,
        5,
        10,
        20
    ]:

        df[f"return_{period}d_pct"] = (
            df["close"]
            .pct_change(
                periods=period
            )
            * 100
        )


    # ── RSI ──────────────────────────────────

    df["rsi_14"] = calculate_rsi(
        df["close"],
        14
    )

    df["rsi_21"] = calculate_rsi(
        df["close"],
        21
    )


    # ── Historical Volatility ────────────────

    daily_returns = (
        df["close"]
        .pct_change()
    )

    for period in [
        20,
        50
    ]:

        df[
            f"historical_volatility_{period}d"
        ] = (
            daily_returns
            .rolling(
                window=period,
                min_periods=period
            )
            .std()
            * np.sqrt(252)
            * 100
        )


    # ── ATR ──────────────────────────────────

    df["atr_14"] = calculate_atr(
        df,
        14
    )

    df["atr_14_pct"] = (
        df["atr_14"]
        /
        df["close"]
        * 100
    )


    # ── Rolling High / Low ───────────────────

    df["high_20d"] = (
        df["high"]
        .rolling(
            window=20,
            min_periods=20
        )
        .max()
    )

    df["low_20d"] = (
        df["low"]
        .rolling(
            window=20,
            min_periods=20
        )
        .min()
    )


    # ── 52 Week High / Low ───────────────────

    df["high_52w"] = (
        df["high"]
        .rolling(
            window=252,
            min_periods=252
        )
        .max()
    )

    df["low_52w"] = (
        df["low"]
        .rolling(
            window=252,
            min_periods=252
        )
        .min()
    )


    # ── Distance From 52 Week Levels ─────────

    df["distance_52w_high_pct"] = (
        (
            df["close"] -
            df["high_52w"]
        )
        /
        df["high_52w"]
        * 100
    )

    df["distance_52w_low_pct"] = (
        (
            df["close"] -
            df["low_52w"]
        )
        /
        df["low_52w"]
        * 100
    )


    return df


def process_instrument(instrument):

    input_path = os.path.join(
        DATA_FOLDER,
        instrument["input"]
    )

    output_path = os.path.join(
        OUTPUT_FOLDER,
        instrument["output"]
    )


    print("\n" + "=" * 60)

    print(
        f"Processing: "
        f"{instrument['name']}"
    )

    print("=" * 60)


    if not os.path.exists(
        input_path
    ):

        print(
            f"ERROR: File not found: "
            f"{input_path}"
        )

        return False


    # ── Load Data ────────────────────────────

    df = pd.read_csv(
        input_path
    )

    print(
        f"Loaded "
        f"{len(df)} rows"
    )


    # ── Calculate Metrics ────────────────────

    df = calculate_metrics(
        df
    )

    print(
        "Calculated metrics:"
    )

    print(
        "  ✓ Moving averages "
        "(20, 50, 100, 200 DMA)"
    )

    print(
        "  ✓ Distance from moving averages"
    )

    print(
        "  ✓ Returns "
        "(1, 5, 10, 20 days)"
    )

    print(
        "  ✓ RSI "
        "(14, 21)"
    )

    print(
        "  ✓ Historical volatility "
        "(20, 50 days)"
    )

    print(
        "  ✓ ATR "
        "(14)"
    )

    print(
        "  ✓ 20-day high / low"
    )

    print(
        "  ✓ 52-week high / low"
    )


    # ── Save ─────────────────────────────────

    df.to_csv(
        output_path,
        index=False
    )

    latest = df.iloc[-1]

    print()

    print(
        f"Saved: {output_path}"
    )

    print(
        f"Latest date: "
        f"{latest['datetime']}"
    )

    print(
        f"Latest close: "
        f"{latest['close']:,.2f}"
    )


    if pd.notna(
        latest["dma_200"]
    ):

        print(
            f"200 DMA: "
            f"{latest['dma_200']:,.2f}"
        )

        print(
            f"Distance from 200 DMA: "
            f"{latest['distance_dma_200_pct']:.2f}%"
        )

    return True


def main():

    print()

    print(
        "=" * 60
    )

    print(
        "OPTION TRADER — DERIVED METRICS"
    )

    print(
        "=" * 60
    )


    success_count = 0


    for instrument in INSTRUMENTS:

        success = process_instrument(
            instrument
        )

        if success:

            success_count += 1


    print()

    print(
        "=" * 60
    )

    print(
        f"COMPLETED: "
        f"{success_count}/"
        f"{len(INSTRUMENTS)} instruments"
    )

    print(
        "=" * 60
    )


if __name__ == "__main__":
    main()
