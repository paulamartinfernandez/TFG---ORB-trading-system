# Bot de Trading — IBEX35 ORB Predictivo

Bot de ejecución autónoma del sistema ORB predictivo sobre el futuro del IBEX35 (MFXI) mediante la API de Interactive Brokers.

## Estructura

```
bot/
├── main.py                  # Punto de entrada — orquesta el pipeline completo
└── src/
    ├── bot.py               # Lógica principal del día de trading
    ├── broker.py            # Conexión con IB, descarga de barras y envío de órdenes
    ├── features.py          # Construcción del vector de características en tiempo real
    └── descargar_historico.py  # Actualización del CSV histórico desde IB
```


## Funcionamiento

El bot ejecuta cada día de mercado el siguiente pipeline:

1. **Actualiza el histórico** — `descargar_historico.py` detecta el último día disponible en el CSV y descarga desde IB los días que faltan hasta el día anterior.
2. **Carga el modelo** — carga desde disco el modelo de regresión logística, el scaler y las features de la ventana de mañana entrenados previamente.
3. **Espera la ventana de apertura** — el bot espera activamente hasta las 09:15 CET.
4. **Recoge las barras de apertura** — descarga en tiempo real los 15 minutos de cotización de 09:00 a 09:14 CET desde IB.
5. **Genera la señal** — construye el vector de características y predice la probabilidad de subida con el modelo.
6. **Opera** — si la probabilidad supera 0.70 lanza una orden LONG; si cae por debajo de 0.40 lanza una orden SHORT; si está entre ambos umbrales no opera.
7. **Gestión automática** — IB gestiona de forma autónoma el take-profit (+130 pts) y el stop-loss (−50 pts) mediante órdenes bracket.

