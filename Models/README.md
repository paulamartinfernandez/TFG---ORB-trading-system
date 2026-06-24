# Sistema de Trading Algorítmico ORB Predictivo

> Trabajo Fin de Grado — Grado en Ingeniería y Sistemas de Datos
> Universidad Politécnica de Madrid, 2026

**Autora:** Paula Martín Fernández
**Título:** Diseño e implementación de un sistema de inversión basado en el rango de apertura aplicando procedimientos de aprendizaje hombre máquina


## Descripción

Sistema de trading algorítmico basado en el paradigma **ORB (Opening Range Breakout) predictivo**. A diferencia del sistema ORB clásico, que actúa de forma reactiva esperando a que el precio rompa el rango de apertura, este sistema entrena un modelo de clasificación supervisada sobre los primeros minutos de cotización para **predecir la dirección del día antes de que se produzca la ruptura**.

El desarrollo sigue una metodología iterativa que parte de modelos con datos exclusivamente diarios y evoluciona progresivamente hasta un sistema completo con gestión empírica del riesgo, validado sobre **28 activos de distintas familias**.



## Estructura del repositorio

```
Models/
├── 0_First_approach.ipynb        # Exploración inicial y análisis descriptivo
│                                 # Gráficos de vela (minuto, hora, día)
│                                 # ES500, GC, BP y CL
│
├── 1_ES_500.ipynb                # Primer modelado con datos diarios
│                                 # Vector de características: gaps, ATR, HINGE, DISPLAY
│                                 # Regresión logística y XGBoost → accuracy ~49%
│
├── 2_ES_500.ipynb                # Incorporación de la ventana de apertura
│                                 # Filtrado 15:30–15:44 CET para ES500
│                                 # Estrategias de tratamiento de NaN
│                                 # Clasificación ternaria
│
├── 2_ES_500_version2.ipynb       # Extensión del notebook anterior
│                                 # Transfer learning y redes neuronales
│                                 # Grid search de arquitecturas y dropout
│
├── 3_ES500_ConMins.ipynb         # Refinamiento del pipeline con datos de minuto
│                                 # Variables de microestructura de apertura
│                                 # Selección de variables con mutual_info_classif
│
├── 4_ES500_Probabilidades.ipynb  # Enfoque probabilístico con umbrales asimétricos
│                                 # Umbrales 0.70/0.40 para largo/corto
│                                 # Análisis MAE/MFE → stop-loss −40 / take-profit +110
│                                 # Grid search de umbrales y sistema dinámico
│
├── 5_IBex35.ipynb                # Traslado del pipeline al IBEX35
│                                 # Ventana de apertura 09:00–09:14 CET
│                                 # Equity curve y optimización de umbrales
│
└── 6_IBex35_2Modelos.ipynb       # Sistema con dos ventanas horarias
                                  # Modelo mañana (09:00) + modelo tarde (15:30)
                                  # Análisis de fuga de información y corrección
                                  # Conclusión: se descarta el modelo de tarde
```

---

## Datos

Series históricas de precios en granularidad de **minuto y diaria** para futuros financieros en formato MetaStock:

| Campo | Descripción |
|---|---|
| `TICKER` | Identificador del activo |
| `PER` | Periodicidad |
| `DTYYYYMMDD` | Fecha en formato numérico |
| `TIME` | Hora |
| `OPEN` | Precio de apertura |
| `HIGH` | Máximo |
| `LOW` | Mínimo |
| `CLOSE` | Cierre |
| `VOL` | Volumen de contratos negociados |

> Los ficheros de datos no se incluyen en este repositorio por razones de tamaño. Pueden obtenerse a través de [Visual Chart](https://visualchart.com/).

---


## Pipeline multi-activo

La extensión del sistema a **28 activos de distintas familias** (índices bursátiles, metales, energía, materias primas agrícolas, divisas y derivados financieros) se encuentra en un notebook independiente desarrollado sobre Google Colab con acceso a Google Drive. Disponible bajo petición.

---

## Referencia

Este trabajo se basa en el sistema ORB predictivo propuesto en:

> López Gonzalo, E. y Rodríguez Crespo, M.Á. (2021). *Proposal of a new trading system on the DAX, based on a predictive Machine Learning model*. Universidad Politécnica de Madrid.

---

## Licencia

Repositorio de uso académico. Todos los derechos reservados © Paula Martín Fernández, 2026.
