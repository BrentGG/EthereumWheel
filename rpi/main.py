import yfinance as yf
import time
import argparse


def doSpeedPriceMapping(min_speed_price, max_speed_price, limit, price):
    if price < min_speed_price:
        if not limit:
            while price < min_speed_price:
                price_range = max_speed_price - min_speed_price
                min_speed_price -= price_range
                max_speed_price -= price_range
        else:
            return 0
    elif price > max_speed_price:
        if not limit:
            while price > min_speed_price:
                price_range = max_speed_price - min_speed_price
                min_speed_price += price_range
                max_speed_price += price_range
        else:
            return 1
    return (price - min_speed_price) / (max_speed_price - min_speed_price)


def wheel(ticker_symbol, update_rate_secs, min_speed_price, max_speed_price, limit):
    prev_speed_value = -1
    while True:
        ticker = yf.Ticker(ticker_symbol)
        last_price = ticker.fast_info["last_price"]
        speed_value = doSpeedPriceMapping(min_speed_price, max_speed_price, limit, last_price)
        if speed_value != prev_speed_value:
            prev_speed_value = speed_value
            print("{:0.2f} speed: {:0.2f}%".format(last_price, speed_value * 100))
        time.sleep(update_rate_secs)


def main():
    parser = argparse.ArgumentParser(description="Control the speed of a bike wheel using the price of Ethereum")
    parser.add_argument("price_range", type=float, nargs="*", action="store", default="200",
                        help="Specify the range of the price to speed mapping. 1 value: a range centered on the current price. 2 values: the minimum and maximum price.")
    parser.add_argument("--limit", action="store_true", help="Limits the range, i.e. if the price goes outside of the range, the range doesn't adjust.")
    parser.add_argument("--ticker", action="store", default="ETH-EUR", help="Which ticker symbol to use, i.e. which stock.")
    parser.add_argument("--rate", type=float, action="store", default=5, help="How often to check for a price update, in seconds.")
    args = parser.parse_args()

    price_range = args.price_range
    ticker = yf.Ticker(args.ticker)
    last_price = ticker.fast_info["last_price"]
    if type(price_range) != list:
        min_speed_price = last_price - (float(price_range) / 2)
        max_speed_price = last_price + (float(price_range) / 2)
    else:
        min_speed_price = price_range[0]
        max_speed_price = price_range[1]

    wheel(args.ticker, args.rate, min_speed_price, max_speed_price, args.limit)


if __name__ == '__main__':
    main()
