# File: app/analysis/data_processing.py

import pandas as pd
from scipy.signal.windows import tukey
from scipy.signal import butter, filtfilt


def apply_data_section(df: pd.DataFrame, t_min_str: str, t_max_str: str) -> pd.DataFrame:
    """Slices the DataFrame to a specified time interval."""
    try:
        t_min = float(t_min_str)
        t_max = float(t_max_str)
        if t_min < t_max:
            return df[(df['TIME'] >= t_min) & (df['TIME'] <= t_max)].copy()
    except (ValueError, KeyError):
        # If input is invalid or 'TIME' column is missing, return original df
        return df
    return df


def apply_tukey_window(df: pd.DataFrame, alpha: float) -> pd.DataFrame:
    """Applies a Tukey window to all data columns in the DataFrame."""
    if 'TIME' not in df.columns or len(df) <= 1:
        return df

    df_windowed = df.copy()
    window = tukey(len(df_windowed), alpha)
    data_cols = [c for c in df_windowed.columns if c not in ['TIME', 'FREQ', 'NO', 'DataFolder']]
    df_windowed.loc[:, data_cols] = df_windowed.loc[:, data_cols].multiply(window, axis=0)
    return df_windowed


def apply_low_pass_filter(df: pd.DataFrame, column: str, cutoff: float, order: int) -> pd.DataFrame:
    """Applies a low-pass Butterworth filter to a specific column in the DataFrame."""
    df_filtered = df.copy()
    try:
        # Calculate sampling frequency
        fs = 1 / df_filtered.index.to_series().diff().mean()

        # Perform filtering
        b, a = butter(order, cutoff / (0.5 * fs), btype='low', analog=False)
        df_filtered[column] = filtfilt(b, a, df_filtered[column])

    except (ValueError, ZeroDivisionError) as e:
        print(f"Could not apply filter: {e}")
        return df  # Return original DataFrame on error

    return df_filtered


# --- Helpers for computed metrics ---
def compute_time_step_series(df: pd.DataFrame) -> pd.DataFrame:
    """Returns a DataFrame with index=TIME and one column 'Δt [s]' computed robustly.
    Assumes df contains a 'TIME' column.
    """
    if 'TIME' not in df.columns or len(df) < 2:
        return pd.DataFrame()
    df_sorted = df.sort_values('TIME')
    time_numeric = pd.to_numeric(df_sorted['TIME'], errors='coerce').astype(float)
    diffs = time_numeric.diff().to_numpy()
    positive = diffs[diffs > 0]
    if positive.size > 0:
        eps = max(1e-12, 1e-6 * float(positive[~pd.isna(positive)].mean()))
    else:
        eps = 1e-12
    diffs[(diffs <= eps)] = float('nan')
    dt_series = pd.Series(diffs, index=df_sorted.index, name='Δt [s]')
    out = dt_series.to_frame()
    out.index = time_numeric
    out.index.name = 'Time [s]'
    return out


def compute_sampling_rate_series(df: pd.DataFrame) -> pd.DataFrame:
    """Returns a DataFrame with index=TIME and one column 'Sampling Rate [Hz]' computed as 1/Δt.
    Assumes df contains a 'TIME' column.
    """
    dt_df = compute_time_step_series(df)
    if dt_df.empty:
        return dt_df
    with pd.option_context('mode.use_inf_as_na', True):
        sr = 1.0 / dt_df['Δt [s]']
    sr = sr.replace([pd.NA, pd.NaT], float('nan'))
    out = sr.to_frame(name='Sampling Rate [Hz]')
    out.index = dt_df.index
    out.index.name = 'Time [s]'
    return out


# --- Builders that return per-folder DataFrames ready for plotting ---
def build_series_by_folder(
        df: pd.DataFrame,
        selected_col: str,
        data_domain: str,
        section_enabled: bool = False,
        t_min_text: str = '',
        t_max_text: str = '',
        filter_enabled: bool = False,
        cutoff_text: str = '',
        filter_order: int = 2,
) -> dict:
    """
    Builds a dict of plot-ready DataFrames per DataFolder for a single selected column.
    - Applies sectioning first (TIME domain only)
    - Sets index to TIME or FREQ
    - Applies low-pass filter if requested (TIME domain only)
    """
    result = {}
    if df is None or selected_col not in df.columns:
        return result

    group_iter = df.groupby('DataFolder') if 'DataFolder' in df.columns else [(None, df)]
    for folder_name, group_df in group_iter:
        proc = group_df
        if data_domain == 'TIME' and section_enabled:
            proc = apply_data_section(proc, t_min_text, t_max_text)

        # Verify required columns
        if data_domain not in proc.columns or selected_col not in proc.columns:
            continue

        # Build plot df with correct index
        x_label = 'Time [s]' if data_domain == 'TIME' else 'Freq [Hz]'
        x_data = proc[data_domain]
        plot_df = proc[[selected_col]].copy()
        plot_df.index = x_data
        plot_df.index.name = x_label

        # Optional low-pass filter for time domain
        if data_domain == 'TIME' and filter_enabled:
            try:
                cutoff = float(cutoff_text)
                plot_df = apply_low_pass_filter(plot_df, selected_col, cutoff, filter_order)
            except (ValueError, TypeError):
                pass

        key = folder_name if folder_name is not None else 'Data'
        result[key] = plot_df

    return result


def build_dt_by_folder(
        df: pd.DataFrame,
        section_enabled: bool = False,
        t_min_text: str = '',
        t_max_text: str = '',
) -> dict:
    """Builds a dict of Δt DataFrames per DataFolder."""
    result = {}
    if df is None or 'TIME' not in df.columns:
        return result
    group_iter = df.groupby('DataFolder') if 'DataFolder' in df.columns else [(None, df)]
    for folder_name, group_df in group_iter:
        proc = group_df
        if section_enabled:
            proc = apply_data_section(proc, t_min_text, t_max_text)
        dt_df = compute_time_step_series(proc)
        if not dt_df.empty:
            key = folder_name if folder_name is not None else 'Data'
            result[key] = dt_df
    return result


def build_fs_by_folder(
        df: pd.DataFrame,
        section_enabled: bool = False,
        t_min_text: str = '',
        t_max_text: str = '',
) -> dict:
    """Builds a dict of sampling-rate DataFrames per DataFolder."""
    result = {}
    if df is None or 'TIME' not in df.columns:
        return result
    group_iter = df.groupby('DataFolder') if 'DataFolder' in df.columns else [(None, df)]
    for folder_name, group_df in group_iter:
        proc = group_df
        if section_enabled:
            proc = apply_data_section(proc, t_min_text, t_max_text)
        fs_df = compute_sampling_rate_series(proc)
        if not fs_df.empty:
            key = folder_name if folder_name is not None else 'Data'
            result[key] = fs_df
    return result


# --- Single-folder builders ---
def build_series_for_single(
        df: pd.DataFrame,
        selected_col: str,
        data_domain: str,
        section_enabled: bool = False,
        t_min_text: str = '',
        t_max_text: str = '',
        filter_enabled: bool = False,
        cutoff_text: str = '',
        filter_order: int = 2,
) -> pd.DataFrame:
    """Builds a single plot-ready DataFrame (index set) for one column in single-folder mode."""
    if df is None or selected_col not in df.columns or data_domain not in df.columns:
        return pd.DataFrame()
    proc = df
    if data_domain == 'TIME' and section_enabled:
        proc = apply_data_section(proc, t_min_text, t_max_text)
    x_label = 'Time [s]' if data_domain == 'TIME' else 'Freq [Hz]'
    plot_df = proc[[selected_col]].copy()
    plot_df.index = proc[data_domain]
    plot_df.index.name = x_label
    if data_domain == 'TIME' and filter_enabled:
        try:
            cutoff = float(cutoff_text)
            plot_df = apply_low_pass_filter(plot_df, selected_col, cutoff, filter_order)
        except (ValueError, TypeError):
            pass
    return plot_df


def build_multi_series_for_single(
        df: pd.DataFrame,
        columns: list,
        data_domain: str,
        section_enabled: bool = False,
        t_min_text: str = '',
        t_max_text: str = '',
        tukey_enabled: bool = False,
        tukey_alpha: float = 0.1,
) -> pd.DataFrame:
    """Builds a single plot-ready DataFrame with multiple columns in single-folder mode.
    Applies sectioning (TIME) then optional Tukey window (TIME) to data columns only.
    """
    if df is None or data_domain not in df.columns:
        return pd.DataFrame()
    if not all(col in df.columns for col in columns):
        return pd.DataFrame()
    proc = df
    if data_domain == 'TIME' and section_enabled:
        proc = apply_data_section(proc, t_min_text, t_max_text)
    if data_domain == 'TIME' and tukey_enabled and len(proc) > 1:
        proc = apply_tukey_window(proc, tukey_alpha)
    plot_df = proc[columns].copy()
    x_label = 'Time [s]' if data_domain == 'TIME' else 'Freq [Hz]'
    plot_df.index = proc[data_domain]
    plot_df.index.name = x_label
    return plot_df