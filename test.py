from luminol.anomaly_detector import AnomalyDetector

ts = {0: 0,
      10: 1,
      20: 1,
      30: 1,
      40: 1,
      50: 1,
      60: 1,
      70: 8,
      80: 1}

my_detector = AnomalyDetector(ts)
score = my_detector.get_all_scores()
for timestamp, value in score.iteritems():
    print(timestamp, value)
