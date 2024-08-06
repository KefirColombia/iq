import time
import os
import pandas as pd
from datetime import datetime, timedelta
from ejtraderIQ import IQOption
import logging

# Desactivar logging completamente
logging.getLogger().setLevel(logging.CRITICAL)

# Inicializa la conexión con IQ Option
api = IQOption(email="rubepatt@gmail.com", password="Ru2514340,", account_type="DEMO", verbose=False)

# Define el par de divisas y el intervalo de tiempo
activo = "EURUSD"
timeframe = "S30"  # Intervalo en segundos (S30 = 30 segundos)

# Definir los días para los que se desean descargar datos (día de mañana)
dias_descarga = [datetime.now() + timedelta(days=1)]

for fecha_objetivo in dias_descarga:
    # Convertir la fecha objetivo a string para el nombre del archivo
    fecha_str = fecha_objetivo.strftime("%Y-%m-%d")
    file_path = f"historical_data_{fecha_str}.csv"
    
    # Si el archivo no existe, empezar desde el inicio del día objetivo
    inicio_del_dia = time.mktime(time.strptime(f"{fecha_objetivo.year}-{fecha_objetivo.month}-{fecha_objetivo.day} 00:00:00", "%Y-%m-%d %H:%M:%S"))
    fin_del_dia = inicio_del_dia + 86400  # Sumar 86400 segundos (1 día) para obtener el final del día
    cantidad_velas = int((fin_del_dia - inicio_del_dia) // 30)  # 30 segundos por vela
    df_existente = pd.DataFrame()  # Crear un DataFrame vacío para concatenar

    # Obtén las velas desde el inicio del día hasta el final del día
    if cantidad_velas > 0:
        nuevas_velas = api.history(symbol=activo, timeframe=timeframe, candles=cantidad_velas)
        
        # Concatenar las nuevas velas con las existentes
        df_actualizado = pd.concat([df_existente, nuevas_velas])
        
        # Guardar el DataFrame actualizado en el archivo CSV
        df_actualizado.to_csv(file_path, mode='w', header=True)
    else:
        print(f"No hay nuevas velas para agregar para el día {fecha_str}.")

    # Imprime las últimas velas obtenidas para cada día
    print(f"Últimas velas obtenidas para {fecha_str}:")
    print(df_actualizado.tail())

# Función para calcular el RSI
def calcular_rsi(data, periodos=14):
    delta = data['close'].diff()
    ganancia = (delta.where(delta > 0, 0)).rolling(window=periodos).mean()
    perdida = (-delta.where(delta < 0, 0)).rolling(window=periodos).mean()
    rs = ganancia / perdida
    rsi = 100 - (100 / (1 + rs))
    return rsi

# Función para calcular las Bandas de Bollinger
def calcular_bollinger_bands(data, window=14, num_std_dev=2):
    sma = data['close'].rolling(window=window).mean()
    std_dev = data['close'].rolling(window=window).std()
    banda_superior = sma + (std_dev * num_std_dev)
    banda_inferior = sma - (std_dev * num_std_dev)
    return sma, banda_superior, banda_inferior

# Función para calcular la tendencia
def calcular_tendencia(data):
    cierre_inicial = data['close'].iloc[0]
    cierre_final = data['close'].iloc[-1]

    if cierre_final > cierre_inicial:
        return "Alcista"
    elif cierre_final < cierre_inicial:
        return "Bajista"
    else:
        return "Incierta"

# Función para monitorear el precio en tiempo real
def monitorear_precio_segundo_a_segundo():
    while True:
        # Obtener el precio actual usando velas de 1 segundo
        precio_actual = api.history(symbol=activo, timeframe="M1", candles=1)  # Usar M1 en lugar de S1
        ultimo_precio = precio_actual['close'].iloc[-1]

        # Imprime el precio actual
        print(f"Precio actual: {ultimo_precio:.4f}")

        # Espera 1 segundo antes de la siguiente consulta
        time.sleep(1)

# Inicia el bucle para continuar descargando datos en tiempo real y calcular la tendencia
try:
    while True:
        # Capturar la fecha y hora actuales
        fecha_hora_actual = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Monitorea el precio segundo a segundo
        monitorear_precio_segundo_a_segundo()
        
        # Cada 30 segundos realiza las operaciones adicionales
        if datetime.now().second % 30 == 0:
            # Descarga la última vela
            nuevas_velas = api.history(symbol=activo, timeframe=timeframe, candles=1)
            
            # Añade la nueva vela al DataFrame y guarda en el CSV
            df_actualizado = pd.concat([df_actualizado, nuevas_velas])
            df_actualizado.to_csv(file_path, mode='w', header=True)

            # Calcular la tendencia del mercado en diferentes periodos de tiempo
            periodos_tiempo = {
                "4 horas": 480,  # Para S30, 480 velas = 4 horas
                "1 hora": 120,   # 120 velas = 1 hora
                "30 minutos": 60,  # 60 velas = 30 minutos
                "10 minutos": 20,  # 20 velas = 10 minutos
                "5 minutos": 10   # 10 velas = 5 minutos
            }

            for periodo, num_velas in periodos_tiempo.items():
                if len(df_actualizado) >= num_velas:
                    velas_recientes = df_actualizado[-num_velas:]
                    tendencia = calcular_tendencia(velas_recientes)
                    print(f"{fecha_hora_actual} - Tendencia del mercado en {periodo}: {tendencia}")

            # Calcular RSI
            if len(df_actualizado) >= 14:  # Necesitamos al menos 14 velas para calcular el RSI
                rsi = calcular_rsi(df_actualizado)
                ultimo_rsi = rsi.iloc[-1]
                
                if ultimo_rsi > 70:
                    print(f"{fecha_hora_actual} - RSI: {ultimo_rsi:.2f} - Sobrecompra")
                elif ultimo_rsi < 30:
                    print(f"{fecha_hora_actual} - RSI: {ultimo_rsi:.2f} - Sobreventa")
                else:
                    print(f"{fecha_hora_actual} - RSI: {ultimo_rsi:.2f} - Neutral")

            # Calcular las Bandas de Bollinger
            if len(df_actualizado) >= 14:  # Asegúrate de tener suficientes datos para Bollinger Bands
                sma, banda_superior, banda_inferior = calcular_bollinger_bands(df_actualizado)
                ultimo_precio = df_actualizado['close'].iloc[-1]

                # Imprime si el precio cruza las bandas superior o inferior
                if ultimo_precio > banda_superior.iloc[-1]:
                    print(f"{fecha_hora_actual} - El precio ha superado la Banda Superior: {ultimo_precio:.4f}, SMA: {sma.iloc[-1]:.4f}")
                elif ultimo_precio < banda_inferior.iloc[-1]:
                    print(f"{fecha_hora_actual} - El precio ha caído por debajo de la Banda Inferior: {ultimo_precio:.4f}, SMA: {sma.iloc[-1]:.4f}")

        # Espera 1 segundo antes de la siguiente iteración
        time.sleep(1)
except KeyboardInterrupt:
    print("Deteniendo el monitoreo de precios...")
    print("Monitoreo detenido.")
