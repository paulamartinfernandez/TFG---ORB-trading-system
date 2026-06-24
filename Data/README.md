# Datos

Series históricas de precios en granularidad de **minuto** para 28 contratos de futuros en formato MetaStock. Los ficheros no se incluyen directamente en el repositorio por razones de tamaño y están disponibles en Google Drive en el siguiente enlace: [Acceder a los datos](
https://drive.google.com/drive/folders/1GrzS2DJXN73rHUGP-ixRK3DucYhIQd-A?usp=drive_link)

---

## Formato

Cada fichero `.txt` contiene datos separados por comas con las siguientes columnas:

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
| `OPENINT` | Interés abierto |

---

## Activos disponibles

### Índices bursátiles
- `es1min.txt` — E-Mini S&P 500
- `nq1min.txt` — E-Mini NASDAQ-100
- `ym1min.txt` — E-Mini Dow Jones
- `rty1min.txt` — E-Mini Russell 2000
- `mfxi1min.txt` — Futuro IBEX35

### Metales
- `gc1min.txt` — Oro (Gold)
- `si1min.txt` — Plata (Silver)
- `hg1min.txt` — Cobre (Copper)
- `pa1min.txt` — Paladio (Palladium)
- `pl1min.txt` — Platino (Platinum)

### Energía
- `cl1min.txt` — Petróleo crudo (Crude Oil)
- `ho1min.txt` — Fuel oil (Heating Oil)
- `ng1min.txt` — Gas natural (Natural Gas)

### Materias primas agrícolas
- `cc1min.txt` — Cacao (Cocoa)
- `ct1min.txt` — Algodón (Cotton)
- `kc1min.txt` — Café (Coffee)
- `sb1min.txt` — Azúcar (Sugar)
- `zc1min.txt` — Maíz (Corn)
- `zm1min.txt` — Harina de soja (Soybean Meal)

### Divisas frente al dólar
- `ad1min.txt` — AUD/USD (Dólar australiano)
- `bp1min.txt` — GBP/USD (Libra esterlina)
- `cad1min.txt` — CAD/USD (Dólar canadiense)
- `chf1min.txt` — CHF/USD (Franco suizo)
- `ec1min.txt` — EUR/USD (Euro)

### Otros derivados financieros
- `dx1min.txt` — Dollar Index
- `ed1min.txt` — Eurodólar
- `vx1min.txt` — Futuros sobre volatilidad (VIX)
- `zb1min.txt` — T-Bond (Bono del Tesoro 30 años)

---

> Los ficheros `jpy1min.txt`, `eo1min.txt`, `et1min.txt` y `ez1min.txt` están disponibles en Drive pero no se emplean en el análisis final del trabajo.

---







