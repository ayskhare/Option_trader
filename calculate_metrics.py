# calculate_metrics.py
# ─────────────────────────────────────────────
# Reads historical market data from ./data/
# Calculates derived technical metrics.
#
# Standard metrics for:
#   - Nifty 50
#   - Bank Nifty
#   - Nifty Midcap 50
#   - India VIX
#
# Additional VIX-specific metrics are calculated
# only for India VIX.
#
# Saves results in ./data/derived/
# ─────────────────────────────────────────────

import os
import pandas as pd
import numpy as np


# ── Folders ──────────────────────────────────

DATA_FOLDER = "data"
OUTPUT_FOLDER = "data/derived"

os.makedirs(
    OUTPUT_FOLDER,
    exist_ok=True
)


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


# ── RSI ──────────────────────────────────────

def calculate_rsi(
    close,
    period=14
):
    """Calculate Relative Strength Index."""

    delta = close.diff()

    gain = delta.where(
        delta > 0,
        0.0
    )

    loss = -delta.where(
        delta < 0,
        0.0
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


# ── ATR ──────────────────────────────────────

def calculate_atr(
    df,
    period=14
):
    """Calculate Average True Range."""

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


# ── Main Metrics Calculation ─────────────────

def calculate_metrics(
    df,
    instrument_name
):
    """Calculate derived metrics."""

    df = df.copy()

    # ── Prepare Data ─────────────────────────

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

        df[
            f"distance_dma_{period}_pct"
        ] = (
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

        df[
            f"return_{period}d_pct"
        ] = (
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


    # ── 20-Day High / Low ────────────────────

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


    # ── 52-Week High / Low ───────────────────

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


    # ── Distance From 52-Week Levels ─────────

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


    # ═════════════════════════════════════════
    # INDIA VIX SPECIFIC METRICS
    # ═════════════════════════════════════════

    if instrument_name == "India VIX":

        # ── VIX Position in 52-Week Range ────

        df["vix_52w_high"] = (
            df["close"]
            .rolling(
                window=252,
                min_periods=252
            )
            .max()
        )

        df["vix_52w_low"] = (
            df["close"]
            .rolling(
                window=252,
                min_periods=252
            )
            .min()
        )

        range_52w = (
            df["vix_52w_high"] -
            df["vix_52w_low"]
        )

        df["vix_52w_percentile"] = (
            (
                df["close"] -
                df["vix_52w_low"]
            )
            /
            range_52w
            * 100
        )


        # ── VIX vs Moving Averages ───────────

        df["vix_vs_20dma_pct"] = (
            (
                df["close"] -
                df["dma_20"]
            )
            /
            df["dma_20"]
            * 100
        )

        df["vix_vs_50dma_pct"] = (
            (
                df["close"] -
                df["dma_50"]
            )
            /
            df["dma_50"]
            * 100
        )

        df["vix_vs_200dma_pct"] = (
            (
                df["close"] -
                df["dma_200"]
            )
            /
            df["dma_200"]
            * 100
        )


        # ── VIX Z-Score ──────────────────────

        vix_mean_20 = (
            df["close"]
            .rolling(
                window=20,
                min_periods=20
            )
            .mean()
        )

        vix_std_20 = (
            df["close"]
            .rolling(
                window=20,
                min_periods=20
            )
            .std()
        )

        df["vix_zscore_20"] = (
            (
                df["close"] -
                vix_mean_20
            )
            /
            vix_std_20
        )


        # ── 50-Day VIX Z-Score ───────────────

        vix_mean_50 = (
            df["close"]
            .rolling(
                window=50,
                min_periods=50
            )
            .mean()
        )

        vix_std_50 = (
            df["close"]
            .rolling(
                window=50,
                min_periods=50
            )
            .std()
        )

        df["vix_zscore_50"] = (
            (
                df["close"] -
                vix_mean_50
            )
            /
            vix_std_50
        )


        # ── 20-Day VIX Percentile ────────────

        df["vix_20d_percentile"] = (
            df["close"]
            .rolling(
                window=20,
                min_periods=20
            )
            .rank(
                pct=True
            )
            * 100
        )


        # ── 50-Day VIX Percentile ────────────

        df["vix_50d_percentile"] = (
            df["close"]
            .rolling(
                window=50,
                min_periods=50
            )
            .rank(
                pct=True
            )
            * 100
        )


    return df


# ── Process Individual Instrument ────────────

def process_instrument(
    instrument
):

    input_path = os.path.join(
        DATA_FOLDER,
        instrument["input"]
    )

    output_path = os.path.join(
        OUTPUT_FOLDER,
        instrument["output"]
    )


    print()

    print("=" * 60)

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
        f"Loaded {len(df)} rows"
    )


    # ── Calculate Metrics ────────────────────

    df = calculate_metrics(
        df,
        instrument["name"]
    )


    print()

    print(
        "Calculated standard metrics:"
    )

    print(
        "  ✓ 20 / 50 / 100 / 200 DMA"
    )

    print(
        "  ✓ Distance from moving averages"
    )

    print(
        "  ✓ Returns: 1 / 5 / 10 / 20 days"
    )

    print(
        "  ✓ RSI: 14 / 21"
    )

    print(
        "  ✓ Historical volatility: 20 / 50 days"
    )

    print(
        "  ✓ ATR 14 and ATR %"
    )

    print(
        "  ✓ 20-day high / low"
    )

    print(
        "  ✓ 52-week high / low"
    )


    if instrument["name"] == "India VIX":

        print()

        print(
            "Calculated India VIX-specific metrics:"
        )

        print(
            "  ✓ 52-week VIX percentile"
        )

        print(
            "  ✓ Distance from 20 / 50 / 200 DMA"
        )

        print(
            "  ✓ 20-day VIX Z-score"
        )

        print(
            "  ✓ 50-day VIX Z-score"
        )

        print(
            "  ✓ 20-day VIX percentile"
        )

        print(
            "  ✓ 50-day VIX percentile"
        )


    # ── Save Metrics ─────────────────────────

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


    if (
        instrument["name"] == "India VIX"
        and pd.notna(
            latest["vix_52w_percentile"]
        )
    ):

        print()

        print(
            f"VIX 52-week percentile: "
            f"{latest['vix_52w_percentile']:.2f}%"
        )

        print(
            f"VIX 20-day Z-score: "
            f"{latest['vix_zscore_20']:.2f}"
        )

        print(
            f"VIX 50-day Z-score: "
            f"{latest['vix_zscore_50']:.2f}"
        )


    return True


# ── Main ─────────────────────────────────────

def main():

    print()

    print("=" * 60)

    print(
        "OPTION TRADER — DERIVED METRICS"
    )

    print("=" * 60)


    success_count = 0


    for instrument in INSTRUMENTS:

        success = process_instrument(
            instrument
        )

        if success:

            success_count += 1


    print()

    print("=" * 60)

    print(
        f"COMPLETED: "
        f"{success_count}/"
        f"{len(INSTRUMENTS)} instruments"
    )

    print("=" * 60)


if __name__ == "__main__":
    main()
