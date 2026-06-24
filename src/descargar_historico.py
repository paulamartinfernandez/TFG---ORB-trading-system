# descargar_historico.py
# Descarga los días que faltan desde IB y los añade a mfxi1min.txt

import pandas as pd
from datetime import datetime, timedelta, timezone
from dateutil import tz
from ib_insync import IB, Future


SYMBOL       = 'IBEX'
EXPIRY       = '20260619'
EXCHANGE     = 'MEFFRV'
CURRENCY     = 'EUR'

HOST         = '127.0.0.1'
PORT         = 7497
CLIENT_ID    = 2          # distinto al de broker.py (CLIENT_ID=1) por si acaso
ZONA         = 'Europe/Madrid'
TRADING_CLASS = 'MIX'



def _ultimo_dia_csv(path_csv: str) -> pd.Timestamp:
    df = pd.read_csv(path_csv)
    fechas_str = df['<DTYYYYMMDD>'].astype(str).str.split('.').str[0]
    fechas_str = fechas_str[fechas_str.str.len() == 8]
    return pd.to_datetime(fechas_str, format='%Y%m%d').max()


def _dias_laborables_faltantes(ultimo_dia: pd.Timestamp) -> list:
    """
    Devuelve lista de fechas desde el día siguiente al último hasta anteayer.
    """
    zona     = tz.gettz(ZONA)
    hoy      = datetime.now(zona).date()
    anteayer = hoy - timedelta(days=1)

    inicio = ultimo_dia.date() + timedelta(days=1)
    dias   = []
    fecha  = inicio
    while fecha <= anteayer:
        if fecha.weekday() < 5:   # lunes-viernes
            dias.append(fecha)
        fecha += timedelta(days=1)
    return dias


def _descargar_dia(ib: IB, contract, fecha) -> list:
    """Descarga barras de 1 min de un día concreto desde IB."""
    zona    = tz.gettz(ZONA)
    fin_dia = datetime(fecha.year, fecha.month, fecha.day, 23, 59, 0, tzinfo=zona)
    end_str = fin_dia.astimezone(timezone.utc).strftime("%Y%m%d %H:%M:%S") + " UTC"

    bars = ib.reqHistoricalData(
        contract,
        endDateTime=end_str,
        durationStr="1 D",
        barSizeSetting='1 min',
        whatToShow='TRADES',
        useRTH=False,
        formatDate=2,
    )
    return bars or []


def _bars_to_rows(bars: list, zona_str: str) -> list:
    """
    Convierte barras IB al formato de fila de mfxi1min.txt:
    <DTYYYYMMDD>, <TIME>, <OPEN>, <HIGH>, <LOW>, <CLOSE>, <VOL>, <OPENINT>
    """
    zona = tz.gettz(zona_str)
    filas = []
    for b in bars:
        dt = b.date
        if hasattr(dt, 'astimezone'):
            dt = dt.astimezone(zona)
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=zona)
        dt_naive = dt.replace(tzinfo=None)
        filas.append({
            '<DTYYYYMMDD>': int(dt_naive.strftime('%Y%m%d')),
            '<TIME>':       int(dt_naive.strftime('%H%M%S')),
            '<OPEN>':       b.open,
            '<HIGH>':       b.high,
            '<LOW>':        b.low,
            '<CLOSE>':      b.close,
            '<VOL>':        int(b.volume),
            '<OPENINT>':    0,
        })
    return filas


def descargar_historico(path_csv: str):
    """
    Lee el CSV, detecta el último día disponible, descarga los días
    que faltan desde IB (1 en 1) y los añade al CSV.
    """
    print("\n── Actualizando histórico ──────────────────────────")

    ultimo_dia = _ultimo_dia_csv(path_csv)
    print(f"  Último día en CSV: {ultimo_dia.date()}")

    dias_faltantes = _dias_laborables_faltantes(ultimo_dia)

    if not dias_faltantes:
        print("  CSV ya está al día. No hay nada que descargar.")
        return

    print(f"  Días a descargar: {len(dias_faltantes)} "
          f"({dias_faltantes[0]} → {dias_faltantes[-1]})")

    # Conectar a IB
    ib = IB()
    ib.connect(HOST, PORT, clientId=CLIENT_ID)
    print(f"  Conectado a IB ({HOST}:{PORT})")

    contract = Future(SYMBOL, EXPIRY, EXCHANGE, currency=CURRENCY, tradingClass=TRADING_CLASS)

    nuevas_filas = []

    try:
        for dia in dias_faltantes:
            print(f"  Descargando {dia}...", end=" ", flush=True)
            bars = _descargar_dia(ib, contract, dia)
            if bars:
                filas = _bars_to_rows(bars, ZONA)
                nuevas_filas.extend(filas)
                print(f"{len(filas)} barras")
            else:
                print("sin datos (festivo o mercado cerrado)")
    finally:
        ib.disconnect()
        print("  Desconectado de IB.")

    if not nuevas_filas:
        print("  No se obtuvieron datos nuevos.")
        return

    # Añadir al CSV
    df_nuevo = pd.DataFrame(nuevas_filas)
    df_nuevo.to_csv(path_csv, mode='a', header=False, index=False)
    print(f"  ✓ Añadidas {len(nuevas_filas)} barras nuevas a {path_csv}")
    print("────────────────────────────────────────────────────\n")
