################################################################################
# FILE:         itrade_luminol_01.py
# ORIGINATOR:   WALLSTROM, Andreas
################################################################################

import pandas as pd
from luminol.anomaly_detector import AnomalyDetector
from pprint import pprint
from datetime import datetime
from matplotlib import pyplot
from matplotlib import dates

def ingest_csv(fpath):
    # Dateformat: 01-Mar-17 (%d-%b-%y)
    dateparse = lambda x: (pd.to_datetime(pd.datetime.strptime(x, '%d-%b-%y')) - datetime(1970, 1, 1)).total_seconds()
    # nrows=10000
    # df = pd.read_csv(fpath, sep=',', parse_dates=['TRANSACTION_DATE'], date_parser=dateparse)
    df = pd.read_csv(fpath, sep=',')
    df['TRANSACTION_DATE'] = [int(dateparse(x)) for x in df['TRANSACTION_DATE']]
    return df

def plot_anomalies(ts, anomalies):
    # Convert from UNIX timestamps back to regular timestamps
    x_ts_dates = [ datetime.fromtimestamp(x) for x in ts.keys() ]
    x_anomalies_dates = [ datetime.fromtimestamp(x) for x in anomalies.keys() ]

    fig, ax1 = pyplot.subplots()

    # Put data on graph
    pyplot.plot(x_ts_dates, ts.values())
    pyplot.scatter(x_anomalies_dates, anomalies.values(), c='red')

    # Set axis to be labeled by dates
    monthyearFmt = dates.DateFormatter('%Y %B')
    ax1.xaxis.set_major_formatter(monthyearFmt)
    _ = pyplot.xticks(rotation=90)
    pyplot.show()

def main():
    FILE = 'anomaly-5k.csv'
    # FILE = 'Anomaly_Data_NO-CR.csv'
    df = ingest_csv(FILE)
    #ts = {}
    group_tdate = df.groupby(['TRANSACTION_DATE'])[ ['DELIVERED_PRICE'] ].sum().apply(list).to_dict()[ 'DELIVERED_PRICE' ]
    #keys = list( ts['TRANSACTION_DATE'] )
    keys = list( group_tdate.keys() )
    #values = list( ts['DELIVERED_PRICE'])
    values = list( group_tdate.values() )

    ts = dict(zip(keys, values))
    #ts = df['DELIVERED_PRICE'].groupby(df['TRANSACTION_DATE']).sum()

    print("keys: ", len(keys))
    print("values: ", len(values))
    print("df.size(): ", df.size)
    print("len(ts.keys())", len(ts.keys()))

    pprint(ts)

    detector = AnomalyDetector( time_series=ts,
                                #algorithm_name='derivative_detector',
                                algorithm_name='exp_avg_detector',
                                algorithm_params={
                                        'smoothing_factor' : 0.05,
                                        'use_lag_window' : True
                                })
    score = detector.get_all_scores()

    n_anomaly = 0
    anomalies = {}
    for timestamp, value in score.iteritems():
        if value > 2:
            n_anomaly += 1
            print(timestamp, value)
            anomalies[timestamp] = ts[timestamp]
        # print(timestamp, value)

    print("n_anomaly:", n_anomaly, "of", len(df), "(", (n_anomaly/len(df))*100, "%)")

    for anomaly in detector.get_anomalies():
        pprint( vars(anomaly) )

    print(len(detector.get_anomalies()))

    plot_anomalies(ts, anomalies)

if __name__ == "__main__":
    main()
