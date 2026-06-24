# TFG - Diseño e implementación de un sistema de inversión basado en el rango de apertura aplicando procedimientos hombre máquina
> Trabajo Fin de Grado — Grado en Ingeniería y Sistemas de Datos
> Universidad Politécnica de Madrid, 2026

**Autora:** Paula Martín Fernández
**Supervisor:** Dr. Eduardo López Gonzalo
**Título:** Diseño e implementación de un sistema de inversión basado en el rango de apertura aplicando procedimientos de aprendizaje hombre máquina

## Descripción

Sistema de trading algorítmico basado en el paradigma **ORB (Opening Range Breakout) predictivo** que predice la dirección diaria de futuros financieros mediante modelos de machine learning entrenados sobre los primeros minutos de cotización. El sistema se valida tanto en backtesting sobre datos históricos como en producción mediante paper trading con la API de Interactive Brokers.


## Estructura del repositorio

```
/
├── data/                  # Series históricas de precios en formato MetaStock (.txt)
│                          # Datos de minuto y diarios para 28 activos de distintas familias
│                          # Ver README interno para detalle de activos y formato
│
├── models/                # Notebooks de desarrollo del pipeline (Google Colab)
│                          # Desarrollo iterativo desde modelos diarios hasta sistema completo
│                          # Ver README interno para detalle de cada notebook
│
└── bot/                   # Implementación en tiempo real con Interactive Brokers
                           # Bot de ejecución autónoma mediante IB API y TWS
                           # Ver README interno para instrucciones de uso
```


## Resumen del desarrollo

El repositorio se estructura en 3 bloques:

**Modelos (`/models`):** desarrollo progresivo del pipeline de machine learning, desde un primer modelo con datos exclusivamente diarios hasta un sistema completo con ventana de apertura, umbrales de probabilidad asimétricos y calibración empírica del stop-loss y take-profit mediante análisis MAE/MFE. Validado sobre el ES500 e IBEX35 y extendido a 28 activos.

**Datos (`/data`):** series históricas en formato MetaStock para 28 contratos de futuros de distintas familias — índices bursátiles, metales, energía, materias primas agrícolas, divisas y derivados financieros.

**Bot (`/bot`):** implementación del sistema en producción mediante la API de Interactive Brokers, con recogida de datos en tiempo real, generación de señales y ejecución autónoma de órdenes bracket con stop-loss y take-profit automáticos.


