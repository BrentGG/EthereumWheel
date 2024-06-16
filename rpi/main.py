import yfinance as yf
import serial
import time
import argparse
import time


def wheel(ticker_symbol, update_rate_secs, num_gears=6, num_hist=10, port=None, baud=9600):
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
        print("no serial port provided, running without serial communication")
    
    # Main loop
    gear = int(num_gears / 2)
    history = []
    while True:
        # Get last stock price
        ticker = yf.Ticker(ticker_symbol)
        last_price = ticker.fast_info["last_price"]
        if len(history) >= num_hist:
            history.pop()
        history.insert(0, last_price)
        if len(history) >= 2:
            if history[0] > history[1]:
                gear = gear + 1 if gear + 1 < num_gears else 1
                print("^ ", end="")
            elif history[0] < history[1]:
                gear = gear - 1 if gear - 1 > 1 else num_gears
                print("v ", end="")
            else:
                print("- ", end="")
        else:
            print("- ", end="")
        print("price: {:0.2f} / gear: {}".format(last_price, gear))
        if ser is not None:
            ser.write(bytearray(str(gear), "ascii"))
        # Wait for next check
        time.sleep(update_rate_secs)


def main():
    # Create argument parser
    parser = argparse.ArgumentParser(description="Control the speed of a bike wheel using the price of Ethereum. No input validation yet!")
    parser.add_argument("--gears", "-g", type=int, action="store", default="6", help="Number of gears driving the wheel.")
    parser.add_argument("--ticker", "-t", action="store", default="ETH-EUR", help="Which ticker symbol to use, i.e. which stock.")
    parser.add_argument("--rate", "-r", type=float, action="store", default=30, help="Time between checking for stock value updates, in seconds.")
    parser.add_argument("--hist", "-hi", type=int, action="store", default=10, help="Number of values to keep in the history.")
    parser.add_argument("--port", "-p", type=str, action="store", help="COM port of the Arduino controlling the wheel.")
    parser.add_argument("--baud", "-b", type=int, action="store", default=9600, help="Baud rate of the Arduino controlling the wheel.")

    # Parse arguments
    args = parser.parse_args()

    # Run the wheel
    print("checking for new price every {} seconds".format(args.rate))
    wheel(args.ticker, args.rate, num_gears=args.gears, num_hist=args.hist, port=args.port, baud=int(args.baud))


if __name__ == '__main__':
    main()
