# -*- coding: UTF-8 -*-

import time
import dateparser
import pytz
import json

from datetime import datetime
from binance.client import Client
import json
import time
import csv
import sys

def date_to_milliseconds(date_str):
    """Convert UTC date to milliseconds

    If using offset strings add "UTC" to date string e.g. "now UTC", "11 hours ago UTC"

    See dateparse docs for formats http://dateparser.readthedocs.io/en/latest/

    :param date_str: date in readable format, i.e. "January 01, 2018", "11 hours ago UTC", "now UTC"
    :type date_str: str
    """
    # get epoch value in UTC
    epoch = datetime.utcfromtimestamp(0).replace(tzinfo=pytz.utc)
    # parse our date string
    d = dateparser.parse(date_str)
    # if the date is not timezone aware apply UTC timezone
    if d.tzinfo is None or d.tzinfo.utcoffset(d) is None:
        d = d.replace(tzinfo=pytz.utc)

    # return the difference in time
    return int((d - epoch).total_seconds() * 1000.0)


def interval_to_milliseconds(interval):
    """Convert a Binance interval string to milliseconds

    :param interval: Binance interval string 1m, 3m, 5m, 15m, 30m, 1h, 2h, 4h, 6h, 8h, 12h, 1d, 3d, 1w
    :type interval: str

    :return:
         None if unit not one of m, h, d or w
         None if string not in correct format
         int value of interval in milliseconds
    """
    ms = None
    seconds_per_unit = {
        "m": 60,
        "h": 60 * 60,
        "d": 24 * 60 * 60,
        "w": 7 * 24 * 60 * 60
    }

    unit = interval[-1]
    if unit in seconds_per_unit:
        try:
            ms = int(interval[:-1]) * seconds_per_unit[unit] * 1000
        except ValueError:
            pass
    return ms


def get_historical_klines(symbol, interval, start_str, end_str=None):
    """Get Historical Klines from Binance

    See dateparse docs for valid start and end string formats http://dateparser.readthedocs.io/en/latest/

    If using offset strings for dates add "UTC" to date string e.g. "now UTC", "11 hours ago UTC"

    :param symbol: Name of symbol pair e.g BNBBTC
    :type symbol: str
    :param interval: Biannce Kline interval
    :type interval: str
    :param start_str: Start date string in UTC format
    :type start_str: str
    :param end_str: optional - end date string in UTC format
    :type end_str: str

    :return: list of OHLCV values

    """
    # create the Binance client, no need for api key
    client = Client("", "")

    # init our list
    output_data = []

    # setup the max limit
    limit = 500

    # convert interval to useful value in seconds
    timeframe = interval_to_milliseconds(interval)

    # convert our date strings to milliseconds
    start_ts = date_to_milliseconds(start_str)

    # if an end time was passed convert it
    end_ts = None
    if end_str:
        end_ts = date_to_milliseconds(end_str)

    idx = 0
    # it can be difficult to know when a symbol was listed on Binance so allow start time to be before list date
    symbol_existed = False
    while True:
        # fetch the klines from start_ts up to max 500 entries or the end_ts if set
        temp_data = client.get_klines(
            symbol=symbol,
            interval=interval,
            limit=limit,
            startTime=start_ts,
            endTime=end_ts
        )

        # handle the case where our start date is before the symbol pair listed on Binance
        if not symbol_existed and len(temp_data):
            symbol_existed = True

        if symbol_existed:
            # append this loops data to our output data
            output_data += temp_data

            # update our start timestamp using the last value in the array and add the interval timeframe
            start_ts = temp_data[len(temp_data) - 1][0] + timeframe
        else:
            # it wasn't listed yet, increment our start date
            start_ts += timeframe

        idx += 1
        # check if we received less than the required limit and exit the loop
        if len(temp_data) < limit:
            # exit the while loop
            break

        # sleep after every 3rd call to be kind to the API
        if idx % 3 == 0:
            time.sleep(1)

    return output_data



def extract_Kline_data_from_strJSON_to_NestedList(filename):
    data_str = open(filename).read()
    data_str = data_str.replace(" ", "").replace("\"", "")
    data_str = data_str[1 : len(data_str) - 1]

    i = 0 # loop index
    result = [] # Result needs to return
    cur_start = 0 # Record first '['
    col_position = [] # Record commas in a pair []
    temp = []   # Just a temp
    comma_between_brackets = False # Check which kind of comma

    while (i < len(data_str)): 
        if (data_str[i] == '['):
            cur_start = i + 1
            comma_between_brackets = True

        if (data_str[i] == ']'):
            #print (col_position)
            for x in range(len(col_position)):
                if (x == 0):
                    temp.append(float(data_str[cur_start : col_position[x]]))
                elif (x >= 6):
                    break
                else:
                    temp.append(float(data_str[col_position[x - 1] + 1: col_position[x]]))

            result.append(temp)
            temp = []
            col_position = []
            comma_between_brackets = False

        if (data_str[i] == ',' and comma_between_brackets):
            col_position.append(i)

        i += 1
    return result


def wirte_to_csv(filename, nestedlist):
    with open(filename, "w") as csvfile: 
        writer = csv.writer(csvfile)
        writer.writerow(["timestamp","open","high","low","close","volume"])
        writer.writerows(nestedlist)



def API(pair_symbol, start_data, end_data, _interval):
    symbol = pair_symbol
    start = start_data
    end = end_data
    if (_interval == '1m'):
        interval = Client.KLINE_INTERVAL_1MINUTE
    elif (_interval == '3m'):
        interval = Client.KLINE_INTERVAL_3MINUTE
    elif (_interval == '5m'):
        interval = Client.KLINE_INTERVAL_5MINUTE
    elif (_interval == '15m'):
        interval = Client.KLINE_INTERVAL_15MINUTE
    elif (_interval == '30m'):
        interval = Client.KLINE_INTERVAL_30MINUTE
    elif (_interval == '1h'):
        interval = Client.KLINE_INTERVAL_1HOUR
    elif (_interval == '2h'):
        interval = Client.KLINE_INTERVAL_2HOUR
    elif (_interval == '4h'):
        interval = Client.KLINE_INTERVAL_4HOUR
    elif (_interval == '6h'):
        interval = Client.KLINE_INTERVAL_6HOUR
    elif (_interval == '8h'):
        interval = Client.KLINE_INTERVAL_8HOUR
    elif (_interval == '12h'):
        interval = Client.KLINE_INTERVAL_12HOUR
    elif (_interval == '1d'):
        interval = Client.KLINE_INTERVAL_1DAY
    elif (_interval == '3d'):
        interval = Client.KLINE_INTERVAL_3DAY
    elif (_interval == '1M'):
        interval = Client.KLINE_INTERVAL_1MONTH


    klines = get_historical_klines(symbol, interval, start, end)

    # open a file with filename including symbol, interval and start and end converted to milliseconds
    with open(
        "Binance_{}_{}_{}-{}.json".format(
            symbol,
            interval,
            date_to_milliseconds(start),
            date_to_milliseconds(end)
        ),
        'w'
    ) as f:
        f.write(json.dumps(klines))

    # Write into 
    temp_list = extract_Kline_data_from_strJSON_to_NestedList("Binance_{}_{}_{}-{}.json".format(symbol, interval, date_to_milliseconds(start), date_to_milliseconds(end)))
    # print(temp_list)
    wirte_to_csv("Binance_{}_{}_{}-{}.csv".format(symbol, interval, date_to_milliseconds(start), date_to_milliseconds(end)), temp_list)
    print("Write CSV OK")


def read_pairs(path):
    _list = []
    file_object = open(path,'rU')
    try:
        for line in file_object:
            if (not line[0].isalpha()):
                continue
            _list.append(line.replace("/", "").rstrip('\n'))
    finally:
        file_object.close()
    return _list




list_pairs = read_pairs("./pairs.txt")
list_fuck_me = []
num_of_error = 1

for i in range(len(list_pairs)):
    try: 
        print("Pair: " + str(i))
        API(list_pairs[i], "1 Jan, 2010", "30 Dec, 2018", "1m")
    except:
        print("Error: " + str(num_of_error))
        num_of_error += 1
        list_fuck_me.append(list_pairs[i])

with open(("Pair_fuck_me.txt"),'w') as ff:
    for p in list_fuck_me:
        ff.write(p)
        ff.write('\n')
ff.close()

