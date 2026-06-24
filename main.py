import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.descargar_historico import descargar_historico
from src.features import cargar_historico
import joblib
import json

PATH_CSV    = r'C:\Users\pauum\Desktop\PAULA\uni\TFG_Proyecto\data\mfxi1min.txt'
PATH_MODELS = r'C:\Users\pauum\Desktop\PAULA\uni\TFG_Proyecto\models'


def test_carga():
    print("Verificando carga de historico...")
    df_min = cargar_historico(PATH_CSV)
    print(f"  Historico cargado: {len(df_min)} filas")
    print(f"  Primer dato: {df_min['datetime'].min()}")
    print(f"  Ultimo dato:  {df_min['datetime'].max()}")

    print("\nVerificando carga de modelos...")
    for nombre in ['model_manana', 'model_tarde', 'scaler_manana', 'scaler_tarde']:
        ruta = os.path.join(PATH_MODELS, f'{nombre}.pkl')
        joblib.load(ruta)
        print(f"  {nombre}.pkl cargado correctamente")

    for nombre in ['feature_cols_manana', 'feature_cols_tarde']:
        ruta = os.path.join(PATH_MODELS, f'{nombre}.json')
        with open(ruta) as f:
            cols = json.load(f)
        print(f"  {nombre}.json cargado: {len(cols)} features")

    print("\nTodo correcto. El sistema esta listo para operar.")


if __name__ == '__main__':
    descargar_historico(PATH_CSV)
    test_carga()

    from src.bot import ejecutar_dia
    ejecutar_dia(PATH_MODELS, PATH_CSV) 
