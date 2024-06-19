import yfinance as yf
import serial
import time
import argparse
import serial.tools.list_ports as ls


def wheel(ticker_symbol, update_rate_secs, num_gears=6, num_hist=10, ser=None):
    gear = int(num_gears / 2)
    history = []
    while True:
        # Get last stock price
        ticker = yf.Ticker(ticker_symbol)
        last_price = ticker.fast_info["last_price"]
        # Get average difference of the history
        if len(history) >= 2:
            avg_diff = sum([abs(history[i] - history[i + 1]) for i in range(len(history) - 1)]) / (len(history) - 1)
        else:
            avg_diff = None
        # Remove oldest value and insert new value
        if len(history) >= num_hist:
            history.pop()
        history.insert(0, last_price)
        # Check for gear change
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
        # Calculate the amount of fluctuation. 0 diff = 0% fluct, avg_diff = 50% fluct, 2 * avg_diff = 100% fluct
        if avg_diff is not None and avg_diff > 0:
            diff = abs(history[0] - history[1])
            fluct = int((diff / (2 * avg_diff)) * 100)
            if fluct > 100:
                fluct = 100
            elif fluct < 0:
                fluct = 0
        else:
            fluct = 50
        print("price: {:0.2f} | gear: {} | fluctuation: {}%".format(last_price, gear, fluct))
        # Send to Arduino
        if ser is not None:
            msg = f"{str(gear)} {str(fluct)}\n"
            ser.write(bytearray(msg, "ascii"))
        # Wait for next check
        time.sleep(update_rate_secs)


def main():
    # Create argument parser
    parser = argparse.ArgumentParser(description="Control the speed of a bike wheel using the price of Ethereum. No input validation yet!")
    parser.add_argument("--gears", "-g", type=int, action="store", default="6", help="Number of gears driving the wheel.")
    parser.add_argument("--ticker", "-t", action="store", default="ETH-EUR", help="Which ticker symbol to use, i.e. which stock.")
    parser.add_argument("--rate", "-r", type=float, action="store", default=30, help="Time between checking for stock value updates, in seconds.")
    parser.add_argument("--hist", "-hi", type=int, action="store", default=10, help="Number of values to keep in the history.")
    parser.add_argument("--dev", "-d", type=str, action="store", help="Device name of the Arduino. Tries to automatically find it if none provided.")
    parser.add_argument("--baud", "-b", type=int, action="store", default=9600, help="Baud rate of the Arduino controlling the wheel.")

    # Parse arguments
    args = parser.parse_args()
    
    # Connect serial port
    dev = args.dev
    if dev is None:
        devs = [p.device for p in ls.comports()]
        if len(devs) > 0:
            print(f"searching for devices, found {devs}")
            for device in devs:
                print(f"attempting connection with {device}... ", end="")
                try:
                    ser = serial.Serial(device, args.baud)
                    print("success")
                    break
                except ValueError:
                    print("failed")
                except serial.SerialException:
                    print("failed")
                ser = None
            if ser is None:
                print(f"couldn't find serial device to connect with, running without serial communication")
        else:
            ser = None
            print("no serial device found, running without serial communication")
    else:
        try:
            ser = serial.Serial(dev, args.baud)
            print(f"serial device {dev} connected")
        except ValueError:
            print("serial parameter out of range, make sure baud rate is correct")
            exit(-1)
        except serial.SerialException:
            print("serial device could not be found or configured")
            exit(-1)

    # Run the wheel
    print("checking for new price every {} seconds".format(args.rate))
    wheel(args.ticker, args.rate, num_gears=args.gears, num_hist=args.hist, ser=ser)


if __name__ == '__main__':
    main()
