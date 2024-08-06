from ejtraderIQ import IQOption
import time

def stop_profit_loss(profit, stop_gain, stop_loss):
    if profit <= float('-' + str(abs(stop_loss))):
        print('\nStop Loss hit!')
        exit()
    if profit >= stop_gain:
        print('\nStop Gain hit!')
        exit()

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

while True:
    print('\n\nStarting operation!')
    direction = 'call'  # Siempre a la alza

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
                entry_value_b *= 2.33  # Increase by 20% after a loss

            profit += round(value, 2)

            print('Trade result: ', end='')
            print('WIN /' if value > 0 else 'LOSS /', round(value, 2), '/', round(profit, 2))

            win_loss_rate = (winning_trades / total_trades) * 100
            print(f'Win/Loss Rate: {win_loss_rate:.2f}%')

            stop_profit_loss(profit, stop_gain, stop_loss)

    except Exception as e:
        print(f'\nERROR IN TRADE EXECUTION: {e}\n\n')

    time.sleep(1)  # Tiempo de espera entre operaciones