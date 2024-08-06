import time
import os
import pandas as pd
from datetime import datetime, timedelta
from ejtraderIQ import IQOption

# Definición de la función que verifica si se han alcanzado el stop loss o stop gain
def stop_profit_loss(profit, stop_gain, stop_loss):
    if profit <= float('-' + str(abs(stop_loss))):
        print('\nStop Loss hit!')
        return False  # Cambia `exit()` a `return False` para que el script no se detenga
    if profit >= stop_gain:
        print('\nStop Gain hit!')
        return False  # Cambia `exit()` a `return False` para que el script no se detenga
    return True  # Continúa si no se alcanzan los límites

# Función para calcular el valor de la próxima entrada utilizando la estrategia Martingale
def Martingale(entry_value, payout):
    return round(entry_value * 2.33, 2)  # Multiplica el valor de la entrada por 2.33 (factor de Martingale)

# Inicializa la conexión con IQ Option
api = IQOption(email="rubepatt@gmail.com", password="Ru2514340,", account_type="DEMO", verbose=True)

# Define el par de divisas y el intervalo de tiempo
activo = "EURUSD"
timeframe = "M1"  # Intervalo en minutos (M1 = 1 minuto)
file_path = f"historical_data_{datetime.now().strftime('%Y-%m-%d')}.csv"

# Si el archivo no existe, crear un DataFrame vacío
if not os.path.exists(file_path):
    df_existente = pd.DataFrame(columns=["date", "open", "high", "low", "close", "volume"])
else:
    # Cargar el archivo existente
    df_existente = pd.read_csv(file_path, parse_dates=['date'])
    df_existente.set_index('date', inplace=True)

# Parámetros para las operaciones
pair = "EURUSD-OTC"
operation = 1  # 1 para "Digital", 2 para "Turbo"
entry_value_b = 1
stop_gain = 10000
stop_loss = 30000
martingale = 25
profit = 0
mhi_type = 1
enter = True
total_trades = 0
winning_trades = 0

# Inicia el bucle para continuar descargando datos en tiempo real y operar
while True:
    # Descarga la última vela y actualiza el archivo
    nuevas_velas = api.history(symbol=activo, timeframe=timeframe, candles=1)
    nuevas_velas['date'] = pd.to_datetime(nuevas_velas['date'])
    nuevas_velas.set_index('date', inplace=True)
    
    # Añade la nueva vela al DataFrame y guarda en el CSV
    df_actualizado = pd.concat([df_existente, nuevas_velas])
    df_actualizado.to_csv(file_path)

    # Calcular la tendencia del mercado (simplificado)
    if len(df_actualizado) >= 3:
        ultima_cierre = df_actualizado['close'].iloc[-1]
        penultima_cierre = df_actualizado['close'].iloc[-2]
        antepenultima_cierre = df_actualizado['close'].iloc[-3]

        if ultima_cierre > penultima_cierre > antepenultima_cierre:
            tendencia = "Alcista"
        elif ultima_cierre < penultima_cierre < antepenultima_cierre:
            tendencia = "Bajista"
        else:
            tendencia = "Incierta"

        print(f"Tendencia del mercado: {tendencia}")

        # Realizar operación basada en la tendencia
        if tendencia == "Alcista" and enter:
            print('Iniciando operación: Call')
            direction = 'call'
        elif tendencia == "Bajista" and enter:
            print('Iniciando operación: Put')
            direction = 'put'
        else:
            direction = None  # No hacer nada si la tendencia es incierta

        if direction:
            entry_value = entry_value_b
            for i in range(martingale):
                id = (api.buy(entry_value, pair, timeframe, turbo=True)
                      if operation == 2
                      else api.buy(entry_value, pair, timeframe))

                win = api.checkwin(id)
                if win is not None:
                    total_trades += 1
                    value = win if win > 0 else float('-' + str(abs(entry_value)))
                    if value > 0:
                        winning_trades += 1
                    profit += round(value, 2)

                    print('Resultado de la operación: ', end='')
                    print('WIN /' if value > 0 else 'LOSS /', round(value, 2), '/', round(profit, 2),
                          ('/ ' + str(i) + ' GALE' if i > 0 else ''))

                    win_loss_rate = (winning_trades / total_trades) * 100
                    print(f'Tasa de Ganancia/Pérdida: {win_loss_rate:.2f}%')

                    entry_value = Martingale(entry_value, api.payout(pair))

                    if not stop_profit_loss(profit, stop_gain, stop_loss):
                        enter = False

                    if value > 0:
                        break

                else:
                    print('\nERROR EN LA EJECUCIÓN DE LA OPERACIÓN\n\n')

    # Espera 60 segundos antes de la siguiente operación
    time.sleep(60)
