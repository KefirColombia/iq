from ejtraderIQ import IQOption
import time
def get_historical_data(api, pair, interval, duration):
    """
    Obtiene datos históricos de velas.
    :param api: instancia de la API
    :param pair: par de divisas
    :param interval: intervalo de tiempo de la vela en segundos (ej. 60 para M1)
    :param duration: duración en minutos de los datos que queremos recuperar
    :return: lista de datos de velas
    """
    end_from_time = time.time()
    since_time = end_from_time - (duration * 60)  # duración en minutos
    candles = api.get_candles(pair, interval, duration, end_from_time)
    return candles
def analyze_trend(candles):
    """
    Analiza la tendencia basada en medias móviles simples.
    :param candles: datos de velas
    :return: 'call' si la tendencia es alcista, 'put' si es bajista, 'neutral' si no hay tendencia clara
    """
    closes = [candle['close'] for candle in candles]
    
    # Calculamos la media móvil simple a corto plazo (ej. 5 periodos)
    sma_short = sum(closes[-5:]) / 5
    
    # Calculamos la media móvil simple a largo plazo (ej. 20 periodos)
    sma_long = sum(closes[-20:]) / 20
    
    if sma_short > sma_long:
        return 'call'
    elif sma_short < sma_long:
        return 'put'
    else:
        return 'neutral'





def stop_profit_loss(profit, stop_gain, stop_loss):
    if profit <= float('-' + str(abs(stop_loss))):
        print('\nStop Loss hit!')
        exit()
    if profit >= stop_gain:
        print('\nStop Gain hit!')
        exit()

# Inicialización de la API
api = IQOption("rubepatt@gmail.com", "Ru2514340,", "DEMO")
pair = "EURUSD"
timeframe = "M1"
operation = 1
initial_entry_value = 1
entry_value_b = initial_entry_value
stop_gain = 300
stop_loss = 1000
profit = 0

total_trades = 0
winning_trades = 0

while True:
    print('\n\nStarting operation!')
    
    # Obtener datos históricos para determinar la tendencia
    candles = get_historical_data(api, pair, 60, 30)  # Velas de 1 minuto para los últimos 30 minutos
    trend = analyze_trend(candles)
    
    # Si la tendencia es neutral, omitimos la operación
    if trend == 'neutral':
        print("Tendencia neutral, no se realiza operación.")
        time.sleep(60)
        continue
    
    direction = trend  # Usar la tendencia como la dirección de la operación

    try:
        id = (api.buy(entry_value_b, pair, timeframe, turbo=True) 
              if operation == 2 
              else api.buy(entry_value_b, pair, timeframe))
        win = api.checkwin(id)

        if win is not None:
            total_trades += 1
            value = win if win > 0 else float('-' + str(abs(entry_value_b)))
            if value > 0:
                winning_trades += 1
                entry_value_b = initial_entry_value  # Reset to initial value after a win
            else:
                entry_value_b *= 1.53  # Increase by 53% after a loss

            profit += round(value, 2)

            print('Trade result: ', end='')
            print('WIN /' if value > 0 else 'LOSS /', round(value, 2), '/', round(profit, 2))

            win_loss_rate = (winning_trades / total_trades) * 100
            print(f'Win/Loss Rate: {win_loss_rate:.2f}%')

            stop_profit_loss(profit, stop_gain, stop_loss)

    except Exception as e:
        print(f'\nERROR IN TRADE EXECUTION: {e}\n\n')

    time.sleep(60)  # Tiempo de espera entre operaciones
