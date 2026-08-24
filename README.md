# NIFTY Option Trader

A data-driven project to build a market direction prediction system for the Indian NIFTY market and eventually use the prediction to support systematic option-selling strategies.

## Project Goal

The objective is to generate a market signal at the end of Monday and use it to guide option strategy selection and execution from Tuesday to Friday.

The model will classify the expected market movement into:

- Extreme Bullish
- Bullish
- Sideways
- Bearish
- Extreme Bearish
- Undeterministic

The prediction focuses on the market's first meaningful movement after entry. A favourable move that occurs early in the Tuesday–Friday holding period can be considered successful even if the market later reverses.

The trading framework is:

```text
Monday Close
     ↓
Market data updated
     ↓
Model generates market signal
     ↓
Tuesday Entry
     ↓
Position monitored during the week
     ↓
Exit on profit target / stop-loss
     ↓
Friday mandatory exit
