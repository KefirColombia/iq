import unittest
from ejtraderIQ import IQOption
import urllib3
import ssl

# Deshabilitar advertencias SSL y HTTP no verificadas
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

class TestIQOptionAPI(unittest.TestCase):
    def setUp(self):
        # Crea una instancia de IQOption
        self.api = IQOption('rubepatt@gmail.com', 'Ru2514340', 'DEMO')
        self.api.login()

    def tearDown(self):
        # Cierra la sesión al finalizar
        self.api.close_socket()
    
    def test_quote(self):
        # Suscríbete a un par de divisas y marco de tiempo
        symbol = "EURUSD"
        timeframe = "M1"
        self.api.subscribe(symbol, timeframe)
        
        # Obtiene una cotización en tiempo real
        quote = self.api.quote()
        print(quote)
        
        # Desuscríbete del par de divisas y marco de tiempo
        self.api.unsubscribe(symbol, timeframe)
    
    def test_history(self):
        # Suscríbete a un par de divisas y marco de tiempo
        symbol = "EURUSD"
        timeframe = "M1"
        self.api.subscribe(symbol, timeframe)
        
        # Obtiene datos históricos
        candles = 1000
        history = self.api.history(symbol, timeframe, candles)
        print(history)
        
        # Desuscríbete del par de divisas y marco de tiempo
        self.api.unsubscribe(symbol, timeframe)
    
    def test_trade_operations(self):
        # Realiza una operación de compra
        symbol = "EURUSD"
        timeframe = "M1"
        volume = 1  # Tamaño de la posición en dólares
        id = self.api.buy(volume, symbol, timeframe)
        print(f"Buy Order ID: {id}")
        
        # Realiza una operación de venta
        id = self.api.sell(volume, symbol, timeframe)
        print(f"Sell Order ID: {id}")
        
        # Verifica el resultado de una operación
        id = self.api.buy(volume, symbol, timeframe)
        win = self.api.checkwin(id)
        
        if win > 0:
            print("WIN")
        elif win < 0:
            print("LOSS")
        else:
            print("Tied")

    def test_account_info(self):
        # Verifica el pago para un activo
        symbol = "EURUSD"
        payout = self.api.payout(symbol)
        print(f"Payout for {symbol}: {payout:.2f}%")
        
        # Verifica el saldo de la cuenta
        balance = self.api.balance()
        print(f"Balance: {balance}")
        
        # Verifica el tiempo restante para una operación
        expire = self.api.remaining("M1")
        print(f"Remaining: {expire}")
    
    def test_real_time_data(self):
        # Inicia la transmisión de datos en tiempo real
        symbol = "EURUSD"
        self.api.powerbar_start(symbol)
        
        # Obtiene datos en tiempo real sobre el lado de venta (%)
        sell_data = self.api.powerbar_get(symbol)
        print(sell_data)
        
        # Detiene la transmisión de datos en tiempo real
        self.api.powerbar_stop(symbol)
    
    def test_server_time(self):
        # Obtiene la hora del servidor
        server_time = self.api.server_time()
        print(f"Server Time: {server_time}")

    def test_market_status(self):
        # Verifica el estado de los mercados
        markets = self.api.isOpen()
        print(markets)

if __name__ == "__main__":
    unittest.main()
