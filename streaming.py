import time
import logging
import datetime
from ejtraderIQ.stable_api import IQ_Option
from ejtraderIQ import IQOption

# Desactivar logging completamente
logging.getLogger().setLevel(logging.CRITICAL)

# Inicializar IQ Option
api = IQOption(email="rubepatt@gmail.com", password="Ru2514340,", account_type="DEMO", verbose=False)

# Conectar
connected, reason = api.connect()
if connected:
    print("Conectado con éxito")
else:
    print(f"No se pudo conectar: {reason}")
    exit(1)

# Iniciar el streaming de velas de 1 segundo para EURUSD
api.start_candles_stream("EURUSD", 1, 1)  # 1 = 1 segundo, 10 = número de velas a almacenar

# Monitorear velas en tiempo real
while True:
    velas = api.get_realtime_candles("EURUSD", 1)  # Obtener velas de 1 segundo
    if velas:
        for timestamp, data in velas.items():
            # Convertir el timestamp a un formato legible
            time_str = datetime.datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S')
            
            # Extraer los datos necesarios
            open_price = data['open']
            high_price = data['max']
            low_price = data['min']
            close_price = data['close']
            volume = data['volume']
            
            # Formatear la salida como "YYYY-MM-DD HH:MM:SS,open,high,low,close,volume"
            formatted_data = f"{time_str},{open_price},{high_price},{low_price},{close_price},{volume}"
            print(formatted_data)
    
    time.sleep(1)
