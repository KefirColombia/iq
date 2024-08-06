from ejtraderIQ import IQOption
import time
import random
import threading
import csv

def should_close_trade():
    global operation_count
    return operation_count % 2 == 0

def execute_trade(action, entry_value, api, pair, timeframe, operation):
    global operation_count
    try:
        if action == "call":
            trade_id = api.buy(entry_value, pair, timeframe, turbo=(operation == 2))
        else:  # action == "put"
            trade_id = api.sell(entry_value, pair, timeframe, turbo=(operation == 2))

        operation_count += 1

        if should_close_trade():
            api.close_digital_option(trade_id)
            print("Operación cancelada anticipadamente.")
            return None

        win = api.checkwin(trade_id)
        return win
    except Exception as e:
        print(f'\nERROR IN TRADE EXECUTION: {e}\n\n')
        return None

def decide_action():
    return random.choice(["call", "put"])

def followup_operation(action, entry_value_initial):
    global profit, total_trades, winning_trades, stop_gain, stop_loss, last_value_followup
    entry_value_followup = entry_value_initial

    while True:
        time.sleep(31)
        print(f'\n\nExecuting follow-up operation: {action.upper()} with entry value: {entry_value_followup}!')
        win = execute_trade(action, entry_value_followup, api, pair, timeframe, operation)

        if win is not None:
            total_trades += 1
            value = win if win > 0 else float('-' + str(abs(entry_value_followup)))
            if value > 0:
                winning_trades += 1
                entry_value_followup = initial_entry_value
            else:
                entry_value_followup *= 2.33

            profit += round(value, 2)
            print('Follow-up trade result: ', end='')
            print('WIN /' if value > 0 else 'LOSS /', round(value, 2), '/', round(profit, 2))
            stop_profit_loss(profit, stop_gain, stop_loss)
            last_value_followup = entry_value_followup

def stop_profit_loss(profit, stop_gain, stop_loss):
    if profit <= float('-' + str(abs(stop_loss))):
        print('\nStop Loss hit!')
        exit()
    if profit >= stop_gain:
        print('\nStop Gain hit!')
        exit()

# Configuración inicial
api = IQOption("rubepatt@gmail.com", "Ru2514340,", "DEMO")  # DEMO OR REAL
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
followup_thread_active = False
last_value_main = initial_entry_value
last_value_followup = initial_entry_value
operation_count = 0
def historical_data_thread(api, pair):
    with open(f'{pair}_historical_data.csv', 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(["Timestamp", "Price"])

        while True:
            # Obtiene los datos históricos
            candles = api.get_candles(pair, 60, 10, time.time())

            for candle in candles:
                timestamp = candle['from']
                price = candle['close']
                writer.writerow([timestamp, price])
                print(f'{pair} Timestamp: {timestamp}, Price: {price}')

            time.sleep(5)  # Recoge datos cada 5 segundos

# Inicia el hilo para recoger datos históricos
historical_data = threading.Thread(target=historical_data_thread, args=(api, pair,))
historical_data.start()

while True:
    action = decide_action()
    print(f'\n\nStarting main operation: {action.upper()} with entry value: {entry_value_b}!')

    win = execute_trade(action, entry_value_b, api, pair, timeframe, operation)
    if win is not None:
        total_trades += 1
        value = win if win > 0 else float('-' + str(abs(entry_value_b)))
        if value > 0:
            winning_trades += 1
            entry_value_b = initial_entry_value
        else:
            entry_value_b *= 2.33

        profit += round(value, 2)
        print('Trade result: ', end='')
        print('WIN /' if value > 0 else 'LOSS /', round(value, 2), '/', round(profit, 2))
        stop_profit_loss(profit, stop_gain, stop_loss)
        last_value_main = entry_value_b

        if not followup_thread_active or not followup_thread.is_alive():
            followup_thread = threading.Thread(target=followup_operation, args=(action, last_value_main,))
            followup_thread.start()
            followup_thread_active = True

    time.sleep(1)  # Tiempo de espera entre operaciones
