# src/broker.py
# Solo descarga en tiempo real los 15 minutos de la ventana.
 
import pandas as pd
from datetime import datetime, timezone
from dateutil import tz
from src.features import cargar_historico
from ib_insync import IB, Future, MarketOrder, LimitOrder, StopOrder
 
SYMBOL        = 'IBEX'
EXPIRY        = '20260619'
EXCHANGE      = 'MEFFRV'
CURRENCY      = 'EUR'
TRADING_CLASS = 'MIX'
 
HOST      = '127.0.0.1'
PORT      = 7497
CLIENT_ID = 1
 
CANTIDAD  = 1
TP_PUNTOS = 130
SL_PUNTOS = 50
ZONA      = 'Europe/Madrid'
 
 
def conectar() -> IB:
    ib = IB()
    ib.connect(HOST, PORT, clientId=CLIENT_ID)
    print(f"Conectado a IB — {HOST}:{PORT} (clientId={CLIENT_ID})")
    return ib
 
 
def desconectar(ib: IB):
    if ib.isConnected():
        ib.disconnect()
        print("Desconectado de IB.")
  
def obtener_historico_reciente(path_csv: str) -> pd.DataFrame:
    """
    Lee el CSV histórico (ya actualizado por descargar_historico.py)
    y devuelve el DataFrame en el formato que espera la función.
    No hace ninguna llamada a IB.
    """
    df = cargar_historico(path_csv)
    print(f"  Histórico cargado: {len(df)} barras "
          f"({df['date'].min().date()} → {df['date'].max().date()})")
    return df

def pedir_barras_hoy(ib: IB, hora_ini: str, hora_fin: str) -> list:
    """
    Pide a IB las barras de 1 min de HOY entre hora_ini y hora_fin.
    Formato hora: 'HH:MM:SS'
    Devuelve lista de dicts {open, high, low, close, volume}.
    """
    contract = Future(SYMBOL, EXPIRY, EXCHANGE, currency=CURRENCY, tradingClass=TRADING_CLASS)
    zona     = tz.gettz(ZONA)
    hoy      = datetime.now(zona).date()
 
    h, m, s   = [int(x) for x in hora_fin.split(':')]
    fin_local = datetime(hoy.year, hoy.month, hoy.day, h, m, s, tzinfo=zona)
 
    h0, m0, s0 = [int(x) for x in hora_ini.split(':')]
    ini_local   = datetime(hoy.year, hoy.month, hoy.day, h0, m0, s0, tzinfo=zona)
 
    dur_seg = int((fin_local - ini_local).total_seconds()) + 60
    end_str = fin_local.astimezone(timezone.utc).strftime("%Y%m%d %H:%M:%S") + " UTC"
 
    bars = ib.reqHistoricalData(
        contract,
        endDateTime=end_str,
        durationStr=f"{dur_seg} S",
        barSizeSetting='1 min',
        whatToShow='TRADES',
        useRTH=False,
        formatDate=2,
    )
 
    barras_ventana = []
    for b in bars:
        dt = b.date
        if hasattr(dt, 'astimezone'):
            dt = dt.astimezone(zona)
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=zona)
        if ini_local <= dt <= fin_local:
            barras_ventana.append({
                'open':   b.open,
                'high':   b.high,
                'low':    b.low,
                'close':  b.close,
                'volume': int(b.volume),
            })
 
    print(f"  Barras {hora_ini}–{hora_fin}: {len(barras_ventana)} recibidas.")
    return barras_ventana
 
 
def lanzar_orden_bracket(ib: IB, señal: int):
    """
    Lanza bracket a mercado para el IBEX35.
      señal = 1 → LONG  (BUY,  TP = +110 pts, SL = -40 pts)
      señal = 0 → SHORT (SELL, TP = -110 pts, SL = +40 pts)
    Usa ib.bracketOrder() para que IB gestione los IDs correctamente.
    """
    contract = Future(SYMBOL, EXPIRY, EXCHANGE, currency=CURRENCY, tradingClass=TRADING_CLASS)
 
    # Precio de referencia
    ticker     = ib.reqMktData(contract, '', False, False)
    ib.sleep(2)
    precio_ref = ticker.last if (ticker.last and ticker.last > 0) else ticker.close
    ib.cancelMktData(contract)
 
    if not precio_ref or precio_ref <= 0:
        print("  ERROR: sin precio de referencia orden no lanzada.")
        return None
 
    precio_ref = round(precio_ref)
 
    if señal == 1:
        action   = 'BUY'
        tp_price = precio_ref + TP_PUNTOS
        sl_price = precio_ref - SL_PUNTOS
    else:
        action   = 'SELL'
        tp_price = precio_ref - TP_PUNTOS
        sl_price = precio_ref + SL_PUNTOS
 
    print(f"  Bracket {action} | ref={precio_ref} | TP={tp_price} | SL={sl_price}")
 
    bracket = ib.bracketOrder(
        action          = action,
        quantity        = CANTIDAD,
        limitPrice      = precio_ref,
        takeProfitPrice = tp_price,
        stopLossPrice   = sl_price,
    )
 

    bracket.parent.orderType = 'MKT'
    bracket.parent.lmtPrice  = 0.0
 
    trades = []
    for orden in [bracket.parent, bracket.takeProfit, bracket.stopLoss]:
        bracket.parent.tif = 'DAY'
        bracket.takeProfit.tif = 'DAY'
        bracket.stopLoss.tif   = 'DAY'
        trades.append(ib.placeOrder(contract, orden))
 
    ib.sleep(1)
    print(f"  Enviado — entry={trades[0].order.orderId} | "
          f"TP={trades[1].order.orderId} | SL={trades[2].order.orderId}")
 
    return trades