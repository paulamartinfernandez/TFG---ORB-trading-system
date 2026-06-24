# src/features.py

import pandas as pd
import numpy as np
from datetime import time


def cargar_historico(path: str) -> pd.DataFrame:
    """Carga el CSV histórico de minutos y parsea fechas."""
    

    df = pd.read_csv(path, low_memory=False)
    fechas_str = df['<DTYYYYMMDD>'].astype(str).str.split('.').str[0]
    df = df[fechas_str.str.len() == 8].copy()

    df['date_str'] = df['<DTYYYYMMDD>'].astype(str).str.split('.').str[0]
    df['time_str'] = df['<TIME>'].astype(str).str.split('.').str[0].str.zfill(6)
    df['date_str'] = df['<DTYYYYMMDD>'].astype(str).str.split('.').str[0]
    df['time_str'] = df['<TIME>'].astype(str).str.split('.').str[0].str.zfill(6)

    df['datetime'] = pd.to_datetime(
        df['date_str'] + df['time_str'], format='%Y%m%d%H%M%S'
    )
    df['date'] = df['datetime'].dt.normalize()
    df['time'] = df['datetime'].dt.time

    df = df.rename(columns={
        '<OPEN>': 'OPEN', '<HIGH>': 'HIGH',
        '<LOW>':  'LOW',  '<CLOSE>': 'CLOSE',
        '<VOL>':  'VOL',  '<OPENINT>': 'OPENINT'
    })
    return df.sort_values(['date', 'datetime']).reset_index(drop=True)


def construir_diario(df_min: pd.DataFrame) -> pd.DataFrame:
    """Agrega OHLCV diario desde minutos."""
    return df_min.groupby('date').agg(
        D_OPEN  = ('OPEN',  'first'),
        D_HIGH  = ('HIGH',  'max'),
        D_LOW   = ('LOW',   'min'),
        D_CLOSE = ('CLOSE', 'last'),
        D_VOL   = ('VOL',   'sum')
    ).reset_index()


def construir_ventana(df_min: pd.DataFrame, hora_ini: time,
                      hora_fin: time, prefijo: str = 'm') -> pd.DataFrame:
    """
    Extrae ventana de minutos y la pivota a formato diario.
    prefijo: 'm' para mañana, 't' para tarde
    """
    df_ventana = df_min[
        (df_min['time'] >= hora_ini) &
        (df_min['time'] <= hora_fin)
    ].copy()

    df_ventana = (
        df_ventana
        .sort_values(['date', 'datetime'])
        .assign(min_id=lambda x: x.groupby('date').cumcount() + 1)
    )

    cols = ['date', 'min_id', 'OPEN', 'HIGH', 'LOW', 'CLOSE', 'VOL']
    df_ventana = df_ventana[cols]

    df_pivot = df_ventana.pivot(
        index='date', columns='min_id',
        values=['OPEN', 'HIGH', 'LOW', 'CLOSE', 'VOL']
    )
    df_pivot.columns = [
        f"{prefijo}{mid}_{var.lower()}"
        for var, mid in df_pivot.columns
    ]
    return df_pivot.reset_index()


def calcular_features_diarias(df_dia: pd.DataFrame) -> pd.DataFrame:
    """Calcula todos los lags y features diarias."""
    df = df_dia.copy().sort_values('date').reset_index(drop=True)

    high  = df['D_HIGH']
    low   = df['D_LOW']
    open_ = df['D_OPEN']
    close = df['D_CLOSE']
    vol   = df['D_VOL']

    df['year']       = df['date'].dt.year
    df['DISPLAY']    = ((high + low) / 2) - open_
    df['BULLISH']    = df['DISPLAY'] > 0
    df['CLOSE_OPEN'] = close - open_
    df['HINGE']      = (high - low) / 2

    for i in range(1, 6):
        df[f'p{i}_close_open'] = df['CLOSE_OPEN'].shift(i)
        df[f'p{i}_high_low']   = high.shift(i) - low.shift(i)
        df[f'p{i}_is_bullish'] = df['BULLISH'].shift(i).astype(float)
        df[f'p{i}_HINGE']      = df['HINGE'].shift(i)
        df[f'p{i}_volume']     = vol.shift(i)
        df[f'p{i}_display']    = df['DISPLAY'].shift(i)

    df['p_close_open_mean'] = df[[f'p{i}_close_open' for i in range(1,6)]].mean(axis=1)
    df['p_close_open_sd']   = df[[f'p{i}_close_open' for i in range(1,6)]].std(axis=1)
    df['p_HINGE_mean']      = df[[f'p{i}_HINGE'      for i in range(1,6)]].mean(axis=1)
    df['p_HINGE_sd']        = df[[f'p{i}_HINGE'      for i in range(1,6)]].std(axis=1)
    df['p_volume_mean']     = df[[f'p{i}_volume'      for i in range(1,6)]].mean(axis=1)
    df['p_volume_sd']       = df[[f'p{i}_volume'      for i in range(1,6)]].std(axis=1)

    # Gaps
    df['prev_close'] = df['D_CLOSE'].shift(1)
    df['gap_abs']    = df['D_OPEN'] - df['prev_close']
    df['gap_pct']    = df['gap_abs'] / df['prev_close']
    df['gap_dir']    = (df['gap_abs'] > 0).astype(int)
    df['gap_zscore'] = (
        df['gap_pct'] - df['gap_pct'].rolling(20).mean()
    ) / df['gap_pct'].rolling(20).std()

    for i in range(1, 6):
        df[f'p{i}_gap_abs']    = df['gap_abs'].shift(i)
        df[f'p{i}_gap_pct']    = df['gap_pct'].shift(i)
        df[f'p{i}_gap_dir']    = df['gap_dir'].shift(i)
        df[f'p{i}_gap_zscore'] = df['gap_zscore'].shift(i)

    # ATR
    df['prev_high'] = df['D_HIGH'].shift(1)
    df['prev_low']  = df['D_LOW'].shift(1)
    tr1 = df['D_HIGH'] - df['D_LOW']
    tr2 = (df['D_HIGH'] - df['prev_close']).abs()
    tr3 = (df['D_LOW']  - df['prev_close']).abs()
    df['true_range'] = np.maximum.reduce([tr1, tr2, tr3])
    df['ATR_5']      = df['true_range'].rolling(5).mean()
    df['ATR_10']     = df['true_range'].rolling(10).mean()
    df['ATR_zscore'] = (
        df['ATR_5'] - df['ATR_5'].rolling(20).mean()
    ) / df['ATR_5'].rolling(20).std()

    for i in range(1, 6):
        df[f'lag{i}_true_range'] = df['true_range'].shift(i)
        df[f'lag{i}_ATR_5']      = df['ATR_5'].shift(i)
        df[f'lag{i}_ATR_10']     = df['ATR_10'].shift(i)
        df[f'lag{i}_ATR_zscore'] = df['ATR_zscore'].shift(i)

    # Volatilidad y tendencia
    df['vol_regime']     = df['ATR_5'] / df['ATR_10']
    df['MA5']            = df['D_CLOSE'].rolling(5).mean()
    df['MA20']           = df['D_CLOSE'].rolling(20).mean()
    df['trend_MA_cross'] = (df['MA5'] > df['MA20']).astype(int)

    for i in range(1, 6):
        df[f'lag{i}_vol_regime']     = df['vol_regime'].shift(i)
        df[f'lag{i}_MA5']            = df['MA5'].shift(i)
        df[f'lag{i}_MA20']           = df['MA20'].shift(i)
        df[f'lag{i}_trend_MA_cross'] = df['trend_MA_cross'].shift(i)

    df['log_ret'] = np.log(df['D_CLOSE'] / df['D_OPEN'])
    return df


def calcular_features_ventana(df_final: pd.DataFrame,
                               prefijo: str = 'm') -> pd.DataFrame:
    """Calcula features resumen de la ventana de minutos."""
    df = df_final.copy()
    p = prefijo

    open_cols  = [f'{p}{i}_open'  for i in range(1, 16)]
    close_cols = [f'{p}{i}_close' for i in range(1, 16)]
    high_cols  = [f'{p}{i}_high'  for i in range(1, 16)]
    low_cols   = [f'{p}{i}_low'   for i in range(1, 16)]
    vol_cols   = [f'{p}{i}_vol'   for i in range(1, 16)]

    suffix = '_t' if p == 't' else ''

    df[f'vol_15m_total{suffix}'] = df[vol_cols].sum(axis=1)
    df[f'vol_15m_mean{suffix}']  = df[vol_cols].mean(axis=1)
    df[f'open_15m{suffix}']      = df[f'{p}1_open']
    df[f'close_15m{suffix}']     = df[f'{p}15_close']
    df[f'log_ret_15m{suffix}']   = np.log(
        df[f'close_15m{suffix}'] / df[f'open_15m{suffix}']
    )
    df[f'range_15m{suffix}']     = (
        df[high_cols].max(axis=1) - df[low_cols].min(axis=1)
    )
    df[f'dir_15m{suffix}']       = np.sign(df[f'log_ret_15m{suffix}'])
    return df


def preparar_fila_hoy(df_min_historico: pd.DataFrame,
                      barras_manana: list,
                      barras_tarde: list = None) -> pd.DataFrame:
    """
    Construye la fila de features para HOY.
    barras_manana: lista de dicts {open, high, low, close, volume}
                   para los 15 minutos de 9:00-9:14
    barras_tarde:  igual pero para 15:30-15:44 (None si no disponible)
    """
    from datetime import date
    hoy = pd.Timestamp(date.today())

    # Histórico hasta ayer
    df_dia = construir_diario(df_min_historico)
    df_dia = calcular_features_diarias(df_dia)

    fila_ayer = df_dia.iloc[-1]

    fila = {'date': hoy, 'year': hoy.year}

    # D_OPEN = primer minuto de mañana
    fila['D_OPEN'] = barras_manana[0]['open']


    # Minutos de mañana
    for i, barra in enumerate(barras_manana[:15], start=1):
        fila[f'm{i}_open']  = barra['open']
        fila[f'm{i}_high']  = barra['high']
        fila[f'm{i}_low']   = barra['low']
        fila[f'm{i}_close'] = barra['close']
        fila[f'm{i}_vol']   = barra['volume']

    # Si faltan barras rellenar hasta 15 con la última disponible
    ultima = barras_manana[-1]
    for i in range(len(barras_manana) + 1, 16):
        fila[f'm{i}_open']  = ultima['open']
        fila[f'm{i}_high']  = ultima['high']
        fila[f'm{i}_low']   = ultima['low']
        fila[f'm{i}_close'] = ultima['close']
        fila[f'm{i}_vol']   = ultima['volume']

    # Lags diarios — copiar de ayer
    cols_lag = [c for c in df_dia.columns if c.startswith((
        'p1_', 'p2_', 'p3_', 'p4_', 'p5_',
        'lag', 'prev_close', 'gap_', 'p_close', 'p_HINGE', 'p_volume'
    ))]
    for col in cols_lag:
        fila[col] = fila_ayer[col]

    # Features resumen de mañana
    n_m     = len(barras_manana)
    high_m  = max(b['high']   for b in barras_manana)
    low_m   = min(b['low']    for b in barras_manana)
    vol_m   = sum(b['volume'] for b in barras_manana)
    open_m  = barras_manana[0]['open']
    close_m = barras_manana[min(14, n_m - 1)]['close']   # fix IndexError

    fila['vol_15m_total'] = vol_m
    fila['vol_15m_mean']  = vol_m / max(n_m, 1)
    fila['open_15m']      = open_m
    fila['close_15m']     = close_m
    fila['log_ret_15m']   = np.log(close_m / open_m)
    fila['range_15m']     = high_m - low_m
    fila['dir_15m']       = np.sign(np.log(close_m / open_m))

    if barras_tarde:
        n_t = len(barras_tarde)
        for i, barra in enumerate(barras_tarde[:15], start=1):
            fila[f't{i}_open']  = barra['open']
            fila[f't{i}_high']  = barra['high']
            fila[f't{i}_low']   = barra['low']
            fila[f't{i}_close'] = barra['close']
            fila[f't{i}_vol']   = barra['volume']

        ultima = barras_tarde[-1]
        for i in range(len(barras_tarde) + 1, 16):
            fila[f't{i}_open']  = ultima['open']
            fila[f't{i}_high']  = ultima['high']
            fila[f't{i}_low']   = ultima['low']
            fila[f't{i}_close'] = ultima['close']
            fila[f't{i}_vol']   = ultima['volume']

        high_t  = max(b['high']   for b in barras_tarde)
        low_t   = min(b['low']    for b in barras_tarde)
        vol_t   = sum(b['volume'] for b in barras_tarde)
        open_t  = barras_tarde[0]['open']
        close_t = barras_tarde[min(14, n_t - 1)]['close']   # fix IndexError

        fila['vol_15m_total_t'] = vol_t
        fila['vol_15m_mean_t']  = vol_t / max(n_t, 1)
        fila['open_15m_t']      = open_t
        fila['close_15m_t']     = close_t
        fila['log_ret_15m_t']   = np.log(close_t / open_t)
        fila['range_15m_t']     = high_t - low_t
        fila['dir_15m_t']       = np.sign(np.log(close_t / open_t))

    return pd.DataFrame([fila])
