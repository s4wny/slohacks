################################################################################
# FILE:         itrade_luminol_01.py
# ORIGINATOR:   WALLSTROM, Andreas
################################################################################

import time
import os
import pandas as pd
from luminol.anomaly_detector import AnomalyDetector
from pprint import pprint
from datetime import datetime
from matplotlib import pyplot
from matplotlib import dates

def localdirpath(filename):
    rawPath=os.path.realpath(__file__)
    absPath=rawPath[:rawPath.rindex('/') +1]
    return absPath + filename

def in_localdir(filename):
    absFilePath = absPath + filename
    return os.path.exists(absFilePath)

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

def plot_anomalies(ts, anomalies):
    # Convert from UNIX timestamps back to regular timestamps
    x_ts_dates = [ datetime.fromtimestamp(x) for x in ts.keys() ]
    x_anomalies_dates = [ datetime.fromtimestamp(x) for x in anomalies.keys() ]

    fig, ax1 = pyplot.subplots()

    # Put data on graph
    #pyplot.plot(x_ts_dates, ts.values())
    pyplot.scatter(x_ts_dates, ts.values())
    pyplot.scatter(x_anomalies_dates, anomalies.values(), c='red')

    # Set axis to be labeled by dates
    monthyearFmt = dates.DateFormatter('%Y %B')
    ax1.xaxis.set_major_formatter(monthyearFmt)
    _ = pyplot.xticks(rotation=90)
    pyplot.show()

def main():
    check_time = time.time()

    #FILE = 'anomaly-5k.csv'
    FILE = 'Anomaly_Data_NO-CR.csv'
    df = ingest_csv(FILE)

    print("Finished loading in : %s" %(time.time() - check_time))
    check_time = time.time()

    #ts = {}
    #group_tdate = df.groupby(['TRANSACTION_DATE'])[ ['DELIVERED_PRICE'] ].sum().apply(list).to_dict()[ 'DELIVERED_PRICE' ]
    group_tdate = df.groupby( pd.Grouper(freq='W') )[ ['DELIVERED_PRICE'] ].sum().apply(list).to_dict()[ 'DELIVERED_PRICE' ]
    #keys = list( ts['TRANSACTION_DATE'] )
    #keys = list( (group_tdate.keys() - datetime(1970, 1, 1)).total_seconds()
    keys = [  int( (x - datetime(1970, 1, 1)).total_seconds()) for x in list(group_tdate.keys()) ]
    #values = list( ts['DELIVERED_PRICE'])
    values = list( group_tdate.values() )

    ts = dict(zip(keys, values))

    print("Finished making ts in : %s" %(time.time() - check_time))

    #ts = df['DELIVERED_PRICE'].groupby(df['TRANSACTION_DATE']).sum()

    # In case we need it laters
    # extreme_anomalies = []
    # 400000 is a magic number that is a lower limit for the extreme outliers
    # Remove this; is not helpful for our modeling of other outliers
    ts = { k:v for k,v in ts.items() if v < 400000 }

    #print("keys: ", len(keys))
    #print("values: ", len(values))
    #print("df.size(): ", df.size)
    #print("len(ts.keys())", len(ts.keys()))

    #pprint(ts)

    check_time = time.time()
    detector = AnomalyDetector( time_series=ts,
                                algorithm_name='derivative_detector',
                                #algorithm_name='exp_avg_detector',
                                algorithm_params={
                                        'smoothing_factor' : 0.20,
                                #        'use_lag_window' : True
                                #},
                                #algorithm_name='bitmap_detector',
                                #algorithm_params={
                                #        'precision' : 4,
                                #        'lag_window_size' : int(0.30 * len(keys)),
                                #        'future_window_size' : int(0.30 * len(keys)),
                                #        'chunk_size' : 2
                                #},
                                #score_percent_threshold=0.9
                                score_threshold=2
                                )
    print("Finished detecting in : %s" %(time.time() - check_time))
    score = detector.get_all_scores()

    n_anomaly = 0
    anomalies = {}
    #for timestamp, value in score.iteritems():
        #if value > 2:
            #n_anomaly += 1
            #print(timestamp, value)
            #anomalies[timestamp] = ts[timestamp]
        # print(timestamp, value)

    #print("n_anomaly:", n_anomaly, "of", len(df), "(", (n_anomaly/len(df))*100, "%)")

    for anomaly in detector.get_anomalies():
        n_anomaly += 1
        anomalies[anomaly.exact_timestamp] = ts[anomaly.exact_timestamp]
        pprint( vars(anomaly) )

    #print(len(detector.get_anomalies()))

    plot_anomalies(ts, anomalies)

if __name__ == "__main__":
    main()
