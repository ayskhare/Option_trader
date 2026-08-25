# 📊 NIFTY Option Trader

A data-driven research and automation project for analysing the Indian equity market and eventually supporting systematic option-selling strategies.

The project is being built as a modular system that collects market data, maintains historical datasets, generates market signals, and will eventually support strategy selection and execution.

---

# 🎯 Project Goal

The primary objective is to develop a market direction prediction system for the Indian NIFTY market.

The model will eventually analyse available market data and generate a directional classification before the trading period.

The planned market classifications are:

- 🟢 Extreme Bullish
- 🟢 Bullish
- 🟡 Sideways
- 🔴 Bearish
- 🔴 Extreme Bearish
- ⚪ Undeterministic

The resulting signal will eventually be used to support systematic option-selling strategy selection.

---

# 🗓 Planned Trading Framework

The initial trading framework is based around a weekly cycle:

```text
Monday Close
      ↓
Market data updated
      ↓
Historical features calculated
      ↓
Model generates market signal
      ↓
Tuesday Entry
      ↓
Position monitored
      ↓
Profit target / Stop-loss management
      ↓
Friday mandatory exit
