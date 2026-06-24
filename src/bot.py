# src/bot.py

import time
import json
import joblib
import pandas as pd
from datetime import datetime, time as dtime
from dateutil import tz

from src.features import preparar_fila_hoy
from src.broker import (conectar, desconectar, obtener_historico_reciente,
                        pedir_barras_hoy, lanzar_orden_bracket)

# Umbrales de señal
THRESHOLD_UP   = 0.70   # prob >= 0.70 → LONG
THRESHOLD_DOWN = 0.40   # prob <= 0.40 → SHORT


HORA_MANANA_ESPERAR = dtime(9, 15)
HORA_MANANA_INI     = '09:00:00'
HORA_MANANA_FIN     = '09:14:00'


def label_from_prob(p: float) -> int:
    if p >= THRESHOLD_UP:
        return 1
    elif p <= THRESHOLD_DOWN:
        return 0
    else:
        return -1


def cargar_modelos(path_models: str) -> dict:
    """Carga modelo y scaler de mañana desde disco. No hace fit."""
    model_m  = joblib.load(f'{path_models}/model_manana.pkl')
    scaler_m = joblib.load(f'{path_models}/scaler_manana.pkl')

    with open(f'{path_models}/feature_cols_manana.json') as f:
        cols_m = json.load(f)

    return {
        'model_m': model_m,
        'scaler_m': scaler_m,
        'cols_m': cols_m,
    }


def esperar_hasta(hora: dtime):
    """Bloquea hasta que el reloj de Madrid alcanza `hora`."""
    zona = tz.gettz('Europe/Madrid')
    while True:
        ahora = datetime.now(zona).time()
        if ahora >= hora:
            break
        seg = (datetime.combine(datetime.today(), hora) -
               datetime.combine(datetime.today(), ahora)).seconds
        print(f"  Esperando hasta {hora} — faltan {seg}s")
        time.sleep(10)


def predecir(fila: pd.DataFrame, cols: list, scaler, model) -> tuple:
    """Escala la fila y devuelve (señal, probabilidad). Sin reentrenamiento."""
    X        = fila[cols].values
    X_scaled = scaler.transform(X)
    prob     = model.predict_proba(X_scaled)[0][1]
    señal    = label_from_prob(prob)
    return señal, prob


def ejecutar_dia(path_models: str, path_csv: str):
    """
    Pipeline completo de un día de trading:
      1. Carga modelo de mañana
      2. Conecta a IB
      3. Lee histórico del CSV
      4. Espera ventana 9:00-9:14 → pide barras → predice → opera
      5. Desconecta
    """
    print(f"\n{'='*50}")
    print(f"Inicio sesion: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'='*50}")

    modelos = cargar_modelos(path_models)
    ib = conectar()

    try:
        #  VENTANA DE MAÑANA 

        zona = tz.gettz('Europe/Madrid')
        ahora = datetime.now(zona).time()
        if ahora > HORA_MANANA_ESPERAR:
            print(f"  Son las {ahora} en Madrid — ventana ya cerrada. Ejecuta mañana antes de las 9:00.")
            return     
        
        
        print("\nDescargando historico reciente...")
        df_min = obtener_historico_reciente(path_csv)  
        print(f"\nEsperando ventana de manana ({HORA_MANANA_INI}–{HORA_MANANA_FIN})...")
        esperar_hasta(HORA_MANANA_ESPERAR)

        barras_m = pedir_barras_hoy(ib, HORA_MANANA_INI, HORA_MANANA_FIN)

        if len(barras_m) < 14:
            print(f"  Advertencia: solo {len(barras_m)} barras (se esperaban 15).")

        fila_m          = preparar_fila_hoy(df_min, barras_manana=barras_m)
        señal_m, prob_m = predecir(fila_m, modelos['cols_m'],
                                   modelos['scaler_m'], modelos['model_m'])

        print(f"  Modelo manana — prob: {prob_m:.3f} | señal: {señal_m}")

        if señal_m != -1:
            print(f"  Lanzando orden manana ({'LONG' if señal_m == 1 else 'SHORT'})...")
            lanzar_orden_bracket(ib, señal_m)
        else:
            print("  Señal neutral — sin operacion.")

    except Exception as e:
        print(f"\nError durante la sesion: {e}")
        raise

    finally:
        desconectar(ib)
        print(f"\nSesion finalizada: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
