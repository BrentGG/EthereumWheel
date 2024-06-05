import yfinance as yf
import serial
import time
import argparse
from gpiozero import PWMOutputDevice
import time


def do_speed_price_mapping(min_speed_price, max_speed_price, limit, price):
    price_range = max_speed_price - min_speed_price
    if price < min_speed_price:
        if not limit:
            count = 0
            # Move the range until the current price falls within
            while price < min_speed_price:
                count += 1
                min_speed_price -= price_range
                max_speed_price -= price_range
            print("adjusted range down {} {}: {:0.2f} - {:0.2f}".format(count, "times" if count > 1 else "time", min_speed_price, max_speed_price))
        else:
            return 0
    elif price > max_speed_price:
        if not limit:
            count = 0
            # Move the range until the current price falls within
            while price > max_speed_price:
                count += 1
                min_speed_price += price_range
                max_speed_price += price_range
            print("adjusted range down {} {}: {:0.2f} - {:0.2f}".format(count, "times" if count > 1 else "time", min_speed_price, max_speed_price))
        else:
            return 1
    return (price - min_speed_price) / (max_speed_price - min_speed_price)


def wheel(ticker_symbol, update_rate_secs, min_speed_price, max_speed_price, limit, port=None, baud=9600, pin=None):
    # Connect serial port
    if port is not None:
        try:
            ser = serial.Serial(port, baud)
            print("serial port connected")
        except ValueError:
            print("serial parameter out of range, make sure baud rate is correct")
            exit(-1)
        except serial.SerialException:
            print("serial device could not be found or configured")
            exit(-1)
    else:
        ser = None
        print("no serial port provided, running without serial communication.")
    # Setup GPIO pin
    if pin is not None:
        gpio = PWMOutputDevice(pin)
        print("pin {} set as output.".format(pin))
    
    prev_speed_value = -1
    while True:
        # Get last stock price
        ticker = yf.Ticker(ticker_symbol)
        last_price = ticker.fast_info["last_price"]
        # Map price to speed
        speed_value = do_speed_price_mapping(min_speed_price, max_speed_price, limit, last_price)
        if speed_value != prev_speed_value:
            prev_speed_value = speed_value
            print("> price: {:0.2f} / speed: {:0.2f}%".format(last_price, speed_value * 100))
            if ser is not None:
                ser.write(bytearray(str(speed_value * 100),"ascii"))
            if pin is not None:
                gpio.value = speed_value
        else:
            print("checked for new stock price, no change.")
        # Wait for next check
        time.sleep(update_rate_secs)


def main():
    # Create argument parser
    parser = argparse.ArgumentParser(description="Control the speed of a bike wheel using the price of Ethereum. No input validation yet!")
    parser.add_argument("price_range", type=float, nargs="*", action="store", default="100",
                        help="Specify the range of the price to speed mapping. 1 value: a range centered on the current price. 2 values: the minimum and maximum price.")
    parser.add_argument("--limit", "-l", action="store_true", help="Limits the range, i.e. if the price goes outside of the range, the range doesn't auto-adjust.")
    parser.add_argument("--ticker", "-t", action="store", default="ETH-EUR", help="Which ticker symbol to use, i.e. which stock.")
    parser.add_argument("--rate", "-r", type=float, action="store", default=5, help="Time between checking for stock value updates, in seconds.")
    parser.add_argument("--port", "-po", type=str, action="store", help="COM port of the Arduino controlling the wheel.")
    parser.add_argument("--baud", "-b", type=int, action="store", default=9600, help="Baud rate of the Arduino controlling the wheel.")
    parser.add_argument("--pin", "-pi", type=int, action="store", help="GPIO pin to output the speed on.")

    # Parse arguments
    args = parser.parse_args()
    price_range = args.price_range
    ticker = yf.Ticker(args.ticker)
    last_price = ticker.fast_info["last_price"]
    if len(price_range) == 1:
        min_speed_price = last_price - (float(price_range[0]) / 2)
        max_speed_price = last_price + (float(price_range[0]) / 2)
    else:
        min_speed_price = float(price_range[0])
        max_speed_price = float(price_range[1])

    # Run the wheel
    print("checking for new prive every {} seconds".format(args.rate))
    print("current range: {:0.2f} - {:0.2f}".format(min_speed_price, max_speed_price))
    wheel(args.ticker, args.rate, min_speed_price, max_speed_price, args.limit, port=args.port, baud=int(args.baud), pin=int(args.pin))


if __name__ == '__main__':
    gpio = PWMOutputDevice(22)
    gpio.value=0.5
    while True:
        continue
    for i in range(0, 110, 10):
        print(i)
        gpio.value = i / 100
        time.sleep(5) 
    exit()
    main()
