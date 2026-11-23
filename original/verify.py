"""
Verifier of anomalous events computing precision, recall and F1 scores

author: Milos Savic, UNSPMF (svc@dmi.uns.ac.rs)
"""

from datetime import datetime

format = '%Y-%m-%d %H:%M:%S'

class Verifier:
    def __init__(self, anom_file="anomalies.timestamps"):
        with open(anom_file) as f:
            self.anom_ts = [line.rstrip() for line in f]

        #print(self.anom_ts)
        self.anomaly_ts = []
        for t in self.anom_ts:
            self.anomaly_ts.append(datetime.strptime(t, format))

    def is_real_anomaly(self, start_time, end_time):
        start_time = self.round_time_down(start_time)
        end_time = self.round_time_up(end_time)
        s = datetime.strptime(start_time, format)
        e = datetime.strptime(end_time, format)
        for t in self.anomaly_ts:
            if s <= t <= e:
                return True

        return False

    def is_real_anomaly_index(self, start_time, end_time):
        start_time = self.round_time_down(start_time)
        end_time = self.round_time_up(end_time)
        s = datetime.strptime(start_time, format)
        e = datetime.strptime(end_time, format)
        for i in range(len(self.anomaly_ts)):
            t = self.anomaly_ts[i]
            if s <= t <= e:
                return i

        return -1

    def round_time_down(self, start_time):
        red = start_time[:-2]
        m = int(red[-3:-1])
        if m > 0:
            m -= 1
        mstr = str(m).zfill(2)
        red = red[:-3]
        red += mstr + ":00"
        return red

    def round_time_up(self, end_time):
        red = end_time[:-2]
        m = int(red[-3:-1])
        if m < 59:
            m += 1
        mstr = str(m).zfill(2)
        red = red[:-3]
        red += mstr + ":59"
        return red

    def compute_scores(self, detected_anomalies, to_print=False):
        b = [False] * len(self.anom_ts)
        false_positive = 0
        for i in range(len(detected_anomalies)):
            t = detected_anomalies[i][0]
            st = t[0]
            et = t[1]
            prev = detected_anomalies[i][1]
            
            isa = self.is_real_anomaly_index(st, et)
            if isa != -1:
                b[isa] = True
            else:
                if not prev:
                    false_positive += 1

        true_positive = 0
        for i in range(len(b)):
            if b[i]:
                true_positive += 1

        precision = 0
        if true_positive + false_positive > 0:
            precision = true_positive / (true_positive + false_positive)
        recall = true_positive / len(b)

        if to_print:
            print(true_positive, ",", false_positive, ",", precision, ",", recall)
        return precision, recall
