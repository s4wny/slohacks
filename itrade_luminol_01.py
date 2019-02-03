import time
import os
import pandas as pd
from luminol.anomaly_detector import AnomalyDetector
from pprint import pprint
from datetime import datetime
from matplotlib import pyplot
from matplotlib import dates

def clear():
    os.system( "cls" if (os.name == "nt") else "clear" )

def ingest_csv(fpath):
    pkl = fpath + '.pkl'
    # Check to see if there is a fpath.pkl file already.
    # If so, assume the file is a valid and well-formed pickle file and read from it
    try:
        df = pd.read_pickle(pkl)
    # If not, then read the file as normal and try to save a pickle file
    except:
        # Dateformat: 01-Mar-17 (%d-%b-%y)
        #dateparse = lambda x: (pd.to_datetime(pd.datetime.strptime(x, '%d-%b-%y')) - datetime(1970, 1, 1)).total_seconds()
        dateparse = lambda x: pd.to_datetime(pd.datetime.strptime(x, '%d-%b-%y'))
        # nrows=10000
        df = pd.read_csv(fpath, sep=',', parse_dates=['TRANSACTION_DATE'], date_parser=dateparse).set_index('TRANSACTION_DATE')
        #df = pd.read_csv(fpath, sep=',')
        #df['TRANSACTION_DATE'] = [int(dateparse(x)) for x in df['TRANSACTION_DATE']]
        pd.to_pickle(df, pkl)
    return df

def plot_anomalies(ts, anomalies, extreme = None):
    # Convert from UNIX timestamps back to regular timestamps
    x_ts_dates = [ datetime.fromtimestamp(x) for x in ts.keys() ]
    x_anomalies_dates = [ datetime.fromtimestamp(x) for x in anomalies.keys() ]

    fig, ax1 = pyplot.subplots()

    # Put data on graph
    #pyplot.plot(x_ts_dates, ts.values())
    if (not (extreme is None)):
        x_extreme_dates = [ datetime.fromtimestamp(x) for x in extreme.keys() ]
        pyplot.scatter(x_extreme_dates, extreme.values(), c='yellow')

    pyplot.scatter(x_ts_dates, list(ts.values()))
    pyplot.scatter(x_anomalies_dates, list(anomalies.values()), c='red')

    # Set axis to be labeled by dates
    monthyearFmt = dates.DateFormatter('%Y %B')
    ax1.xaxis.set_major_formatter(monthyearFmt)
    _ = pyplot.xticks(rotation=90)
    pyplot.show()

def print_plot_of_qty(csv_path, group_by, qty_interest, include_extremes=False, extreme_threshold=400000):
    doc = """

    @param csv_path (str)           :   path to the CSV file
    @param group_by (str)           :   a one-character long string (either "W", "D", "M") specifying in which units of time to
                                        group the data by (either weeks, days, or months, respectively)
    @param qty_interest (str)       :   the identifier of the quantity to be plotted
    @param include_extremes (bool)  :   whether or not to include extreme outliers. Defaults to false.
    @param extreme_threshold (float):   the threshold to cut off extreme outliers (using qty_interest). Exclusive.
    """

    # Ingest the CSV file
    df = ingest_csv(csv_path)
    # Group by a specific quantity, over a specific frequency
    group = df.groupby( pd.Grouper(freq=str(group_by).upper()) )[ [qty_interest] ].sum().apply(list).to_dict()[qty_interest]
    # Get the time (dates)
    gkeys = [ int( (x - datetime(1970, 1, 1)).total_seconds() ) for x in list(group.keys()) ]
    # Get tye values for each time
    gvals = list(group.values())
    # Make the timeseries
    timeseries = dict(zip(gkeys, gvals))

    # Default algorithm properties
    algo_name = 'derivative_detector'
    #algo_name = 'exp_avg_detector'
    algo_params = {
        'smoothing_factor' : 0.2,
    #    'lag_window_size' : int(0.2 * len(gkeys)),
    #    'use_lag_window' : True,
    }
    algo_threshold = 2

    # For any extreme anomalies
    extreme_anomalies = None
    # We ignore extremes by default
    if ( not include_extremes ):
        timeseries = { k:v for k,v in timeseries.items() if v < extreme_threshold }
    # For when we care about these
    else:
        extreme_anomalies = { k:v for k,v in timeseries.items() if v <= extreme_threshold }

        algo_name = 'bitmap_detector'
        algo_params = {
            'precision' : 10,
            'lag_window_size' : int(0.30 * len(keys)),
            'future_window_size' : int(0.30 * len(keys)),
            'chunk_size' : 2,
        }

    # Detector for anomalies
    detector = AnomalyDetector( time_series=timeseries,
                                algorithm_name=algo_name,
                                algorithm_params=algo_params,
                                score_threshold=algo_threshold
                                )
    # Dictionaries of anomalies found
    anomalies = {}
    # Number of anomalies
    n_anomaly = 0
    for anomaly in detector.get_anomalies():
        n_anomaly += 1
        anomalies[anomaly.exact_timestamp] = timeseries[anomaly.exact_timestamp]

    # Plot and print the graph, and anomalies (and include extremes if necessary)
    plot_anomalies(timeseries, anomalies, extreme_anomalies)

def display_menu():
    print(
        """
################################################################################
                        TIME SERIES TSAR (Python) MENU

    Thank you for using TIME SERIES TSAR!

    This instance has been configured for:  iTradeNetworks
    The file loaded is: Anomaly_Data_NO-CR.csv

    Please input your selection for the query:

        [1]     Delivery price vs. Time (by week)*
        [2]     Delivery price vs. Time (by day)*
        [3]     Delivery price vs. Time (by month)*
        [4]     Delivered quantity vs. Time (by week)*

        [q]     Exit the TIME SERIES TSAR system

    *: excludes extreme outliers
################################################################################
        """
    )

def main():
    #FILE = 'anomaly-5k.csv'
    FILE = 'Anomaly_Data_NO-CR.csv'
    s_input = ""
    cmd = ""

    while (not "q" in str(s_input).strip().lower() ):
        clear()
        if (not (cmd is None)):
            print("Executed: ", cmd)
        else:
            #if (len( str(cmd).strip()) > 0) :
            print("Option `%s` was not understood!" % s_input)

        display_menu()
        s_input = input("Please enter your selection: ")

        cmd = {
            '1' :   "print_plot_of_qty(FILE, 'W', 'DELIVERED_PRICE', include_extremes=False, extreme_threshold=400000)",
            '2' :   "print_plot_of_qty(FILE, 'D', 'DELIVERED_PRICE', include_extremes=False, extreme_threshold=400000)",
            '3' :   "print_plot_of_qty(FILE, 'M', 'DELIVERED_PRICE', include_extremes=False, extreme_threshold=400000)",
            '4' :   "print_plot_of_qty(FILE, 'W', 'DELIVERED_QUANTITY', include_extremes=False, extreme_threshold=30000)",

            ### For future expansion
            #'41' :   "print_plot_of_qty(FILE, 'W', 'DELIVERED_PRICE', include_extremes=True, extreme_threshold=400000)",
            #'44' :   "print_plot_of_qty(FILE, 'W', 'DELIVERED_QUANTITY', include_extremes=True, extreme_threshold=30000)",

            'q' :   None,
        }.get(s_input, None)

        if (not (cmd is None)) and ( len(str(cmd).strip()) > 0 ):
            eval(cmd)

        # Let's not fork... it gets confusing for the user
        #new_pid = os.fork()
        #if (0 == new_pid):
        #    eval(cmd)
        #    break
        #else:
        #    continue

    print(""" >> OK, goodbye! """)

if __name__ == "__main__":
    main()
