import os
import sys
import argparse
import numpy as np
import pandas as pd


def read_full_pld(file_path: str) -> pd.DataFrame:
    df = pd.read_csv(
        file_path,
        delimiter='|',
        skipinitialspace=True,
        skip_blank_lines=True,
        comment='_',
        low_memory=False
    )
    df = df.apply(pd.to_numeric)
    df = df.dropna(how='all')
    df = df.dropna(axis=1, how='all')
    df.columns = df.columns.str.strip()
    df.reset_index(drop=True, inplace=True)
    return df


def compute_robust_dt(df_time: pd.DataFrame, sample_rows: int = 2000) -> pd.DataFrame:
    if 'TIME' not in df_time.columns:
        raise ValueError("Provided data does not contain a TIME column.")
    if len(df_time) < 2:
        raise ValueError("Not enough rows to compute time step.")

    df_sorted = df_time.sort_values('TIME').head(sample_rows).copy()
    time_numeric = pd.to_numeric(df_sorted['TIME'], errors='coerce').astype(float)
    diffs = np.diff(time_numeric.values)
    positive_diffs = diffs[diffs > 0]
    if positive_diffs.size > 0:
        eps = max(1e-12, 1e-6 * float(np.median(positive_diffs)))
    else:
        eps = 1e-12
    diffs[(diffs <= eps)] = np.nan
    dt_series = pd.Series(np.concatenate([[np.nan], diffs]), index=df_sorted.index, name='Δt [s]')
    out = pd.DataFrame({'TIME': time_numeric, 'Δt [s]': dt_series})
    return out


def summarize_dt(dt_df: pd.DataFrame) -> str:
    dt = dt_df['Δt [s]']
    pos = dt[dt > 0]
    summary = []
    summary.append(f"Rows (sampled): {len(dt_df)}")
    summary.append(f"Valid positive Δt count: {pos.count()}")
    summary.append(f"NaN/nonpositive Δt count: {dt.isna().sum()}")
    if pos.count() > 0:
        summary.append(f"Δt min: {pos.min():.9f} s")
        summary.append(f"Δt median: {pos.median():.9f} s")
        summary.append(f"Δt 95th pct: {pos.quantile(0.95):.9f} s")
        # approximate modes
        modes = pos.round(9).value_counts().head(5)
        summary.append("Top Δt modes (rounded to 9 dp):")
        for val, cnt in modes.items():
            summary.append(f"  {val:.9f} s  (count={cnt})")
    return "\n".join(summary)


def main():
    parser = argparse.ArgumentParser(description='Test robust time step computation on a folder.')
    parser.add_argument('folder', help='Path to a data folder containing full.pld and max.pld')
    parser.add_argument('--rows', type=int, default=2000, help='Number of rows to sample (default: 2000)')
    args = parser.parse_args()

    folder = args.folder
    if not os.path.isdir(folder):
        print(f"Folder not found: {folder}")
        sys.exit(2)

    full_files = [os.path.join(folder, f) for f in os.listdir(folder) if f.endswith('full.pld')]
    if not full_files:
        print("No 'full.pld' files found in the folder.")
        sys.exit(3)

    # Use the first full.pld for a quick sample
    df_full = read_full_pld(full_files[0])

    if 'TIME' not in df_full.columns and 'FREQ' not in df_full.columns:
        print("Could not detect TIME or FREQ columns in full.pld; ensure files are in expected format.")
        sys.exit(4)
    if 'TIME' not in df_full.columns:
        print("Detected frequency-domain data; TIME column missing. This test expects TIME domain.")
        sys.exit(5)

    dt_df = compute_robust_dt(df_full, sample_rows=args.rows)
    print(summarize_dt(dt_df))
    print("\nFirst 20 rows (TIME, Δt):")
    print(dt_df.head(20).to_string(index=False))


if __name__ == '__main__':
    main()



