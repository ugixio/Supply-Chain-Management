# /forecast — Demand Forecasting Assistant

Helps design, review, or debug demand forecasting logic in this codebase.

## Usage
`/forecast [describe what you need]`

Examples:
- `/forecast implement moving average for SKU reorder`
- `/forecast review the exponential smoothing accuracy`
- `/forecast add safety stock calculation for high-variance items`

---

You are a demand planning expert. Help with the following forecasting task: $ARGUMENTS

Apply these principles:
- Choose algorithm based on data characteristics: MA for stable demand, exponential smoothing for trending, ML for complex patterns
- Always compute MAE, MAPE, and RMSE when evaluating forecast accuracy
- Safety stock formula: Z * σ_LT where Z = service level z-score, σ_LT = std dev of demand during lead time
- Reorder point = (average daily demand × lead time days) + safety stock
- Segment by coefficient of variation (CV): the higher it is, the less a point forecast is worth
  and the more the buffer carries the service level. **The cut-off that counts as high-variance is
  the project's** (CPT-0018) — state the one you are using, do not assume one
- Holt-Winters needs at least **two full seasons** of history to estimate seasonal factors at all;
  that is arithmetic, not a preference

Provide working code with accuracy metrics and explain the algorithm choice.
