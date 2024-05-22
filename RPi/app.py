import threading
import queue

# Bluez gatt uart service (SERVER)
from bluetooth_uart_server.bluetooth_uart_server import ble_gatt_uart_loop

# extend this code so the value received via Bluetooth gets printed on the LCD
# (maybe together with you Bluetooth device name or Bluetooth MAC?)
from lcd import LCD
lcd = LCD()
def main():
    lcd.lcd_init()
    i = 0
    rx_q = queue.Queue()
    tx_q = queue.Queue()
    device_name = "danyukezz-pi-gatt-uart" # TODO: replace with your own (unique) device name
    threading.Thread(target=ble_gatt_uart_loop, args=(rx_q, tx_q, device_name), daemon=True).start()
    while True:
        try:
            incoming = rx_q.get(timeout=1) # Wait for up to 1 second 
            if incoming:
                print("In main loop: {}".format(incoming))
                lcd.send_string(f"Drones: {incoming}", 0x80)
        except Exception as e:
            pass # nothing in Q 
            lcd.clear()
        # if i%5 == 0: # Send some data every 5 iterations
        #     tx_q.put("test{}".format(i))
        # i += 1
if __name__ == '__main__':
    main()


