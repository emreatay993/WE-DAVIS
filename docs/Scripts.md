Scripts

scripts/test_dt.py

Purpose

- Validate robust Δt calculation for TIME-domain datasets in a quick, CLI-friendly way.

Usage

1. Open a terminal and activate the venv
   venv\Scripts\activate

2. Run with a data folder containing full.pld and max.pld
   python scripts/test_dt.py "C:\\path\\to\\data_folder"

3. Optional: limit sampled rows (default 2000)
   python scripts/test_dt.py "C:\\path\\to\\data_folder" --rows 5000

Output

- Summary of Δt statistics (count, min, median, 95th percentile, top modes rounded to 9 dp)
- First 20 rows of (TIME, Δt) pairs

Notes

- Exits with messages if FREQ data is provided (expects TIME); use a TIME folder
- Internally: reads full.pld with the same CSV parameters as the app; sorts by TIME; removes zero/near-zero steps with an adaptive epsilon; reports statistics













