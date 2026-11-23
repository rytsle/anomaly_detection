"""
C4IIoT BACS Anomaly Detection Component

This module defines dataset classes
-- SWDataset: timeseries constructed using the sliding window approach
-- DPDataset: a set of data points

author: Milos Savic, UNSPMF (svc@dmi.uns.ac.rs)
"""

import numpy as np
from datetime import datetime


class SWDataset:
    """
    Datasets constructed using sliding window approach
    It is assumed that the first three features (columns) in the input 
        file are time, latitude and longitude
    """

    def __init__(self, input_file, train_fraction, window_length,\
        time_delta=3600, lat_lon_present=True, use_location_for_ad=False):
        """
        input_file - file used to train and test the ad model
        train_fraction - the percetage of input_file used to train the model
        window_length - sliding window length (the number of data points contained in a slice)
        time_delta - the maximal difference between the last and the first event in the slice (in seconds)
        lat_lon_present - True if latitude and longitude are the second and the third column
                          False if latitude and longitued are not present in the dataset
        use_location_for_ad - if True latitude and longitude are used as features to train anomaly detection models
        """
        self.window_length = window_length
        self.time_delta = time_delta
        self.use_location_for_ad = use_location_for_ad
        with open(input_file) as f:
            self.lines = [line[:-1] for line in f]
        
        self.num_data_points = len(self.lines) - 1
        self.train_data_points = int(train_fraction * self.num_data_points)
        self.test_data_points = self.num_data_points - self.train_data_points
        
        if window_length <= 0:
            raise ValueError("Invalid sliding window length")
        
        self.__init_fields(lat_lon_present)
    
    
    def __init_fields(self, lat_lon_present):    
        header_line = self.lines[0]
        self.fields = header_line.split(",")
        
        # by default the first three features are: time, lat and lon
        if lat_lon_present and not self.use_location_for_ad:
            self.num_features = len(self.fields) - 3
            self.first_feature_index = 3
        else:
            self.num_features = len(self.fields) - 1
            self.first_feature_index = 1

        self.features = []
        for i in range(self.first_feature_index, len(self.fields)):
            self.features.append(self.fields[i]) 

    
    def __form_data_point(self, i):
        data_instance = np.zeros(self.num_features * self.window_length)
        cnt = 0
        zero_lat_lon = False
        gps_alt_negative = False
        oversampled = False

        for j in range (i, i + self.window_length):
            fields = self.lines[j].split(",")
            if j == i:
                start_time_str = fields[0]
            elif j == i + self.window_length - 1:
                end_time_str = fields[0]

            for k in range(self.first_feature_index, len(fields)):
                data_instance[cnt] = float(fields[k])
                cnt += 1

            if float(fields[1]) == 0 and float(fields[2]) == 0:
                zero_lat_lon = True

            if float(fields[3]) < 0:
                gps_alt_negative = True

            if float(fields[-1]) > 10000:
                oversampled = True

        #start_time = datetime.strptime(start_time_str, '%Y-%m-%d %H:%M:%S')
        start_time = parse_time(start_time_str)
        if self.window_length == 1:
            end_time = start_time
            end_time_str = start_time_str
        else:
            #end_time = datetime.strptime(end_time_str, '%Y-%m-%d %H:%M:%S')
            end_time = parse_time(end_time_str) 
        
        if zero_lat_lon or gps_alt_negative or oversampled:
            return (data_instance, False, start_time_str, end_time_str)

        delta = end_time - start_time
        delta_secs = delta.total_seconds()
        if delta_secs >= 0 and delta_secs <= self.time_delta:  
            return (data_instance, True, start_time_str, end_time_str)
        else:
            return (data_instance, False, start_time_str, end_time_str)

    
    def get_train_data(self):
        """
        Retruns the training part of the dataset
        """
        num_slices = self.train_data_points - self.window_length + 1
        train_data_list = []
        train_data_timestamps = []

        for i in range(1, num_slices + 1):
            (dp, ok, st, et) = self.__form_data_point(i)
            if ok:
                train_data_list.append(dp)
                train_data_timestamps.append((st, et))

        return train_data_list, train_data_timestamps

    
    def get_train_data_npmatrix(self):
        """
        Retruns the training part of the dataset as a numpy matrix
        """
        return to_np_matrix(self.get_train_data()[0])
    

    def get_test_data(self):
        """
        Retruns the test part of the dataset
        """
        test_data_list = []
        test_data_timestamps = []
        for i in range(self.train_data_points + 1, len(self.lines) - self.window_length + 1):
            (dp, ok, st, et) = self.__form_data_point(i)
            if ok:
                test_data_list.append(dp)
                test_data_timestamps.append((st, et))

        return test_data_list, test_data_timestamps
  

    def get_test_data_npmatrix(self):
        """
        Retruns the test part of the dataset as a numpy matrix
        """
        return to_np_matrix(self.get_test_data()[0])


    def info(self):
        print("num_features = " + str(self.num_features))
        print("features = " + str(self.fields))
        print("window length = " + str(self.window_length))


class DPDataset:
    """
    A set of data points
    """
    def __init__(self, input_file, train_fraction):
        self.window_length = 1

        with open(input_file) as f:
            self.lines = [line[:-1] for line in f]
        
        header_line = self.lines[0]
        self.fields = header_line.split(",")
        self.num_features = len(self.fields)
        self.num_data_points = len(self.lines) - 1
        
        self.train_data_points = int(train_fraction * self.num_data_points)
        train_part = self.lines[1 : self.train_data_points + 1]
        test_part = self.lines[self.train_data_points + 1 : ]
        self.train_data = [floatify(x.split(",")) for x in train_part]
        self.test_data = [floatify(x.split(",")) for x in test_part]


    def get_train_data(self):
        """
        Retruns the training part of the dataset
        """
        return self.train_data


    def get_train_data_npmatrix(self):
        """
        Retruns the training part of the dataset as a numpy matrix
        """
        return to_np_matrix(self.train_data)


    def get_test_data(self):
        """
        Retruns the test part of the dataset
        """
        return self.test_data


    def get_test_data_npmatrix(self):
        """
        Retruns the test part of the dataset as a numpy matrix
        """
        return to_np_matrix(self.test_data)


    def info(self):
        print("num data points = ", self.num_data_points)
        print("num features = ", self.num_features)
        print("features = ", self.fields)


class LDPDataset:
    """
    A set of labelled data points
    """
    def __init__(self, input_file, train_fraction, label_field_name, regular_data_labels):
        import pandas
        from sklearn.model_selection import train_test_split
        
        ds = pandas.read_csv(input_file)
        self.fields = ds.columns.values
        self.num_features = len(self.fields) - 1   # class excluded
        self.labels = ds[label_field_name].values
        self.classes = set(self.labels)
        self.num_classes = len(self.classes)
        self.instances = ds.drop(label_field_name, axis = 1).values
        self.regular_data_labels = regular_data_labels
        
        if train_fraction == 1.0:
            self.train_data = self.instances
            self.train_labels = self.labels
            self.test_data = None
            self.test_labels = None
        else:
            self.train_data, self.test_data, self.train_labels, self.test_labels = \
                train_test_split(self.instances, self.labels, test_size = 1.0 - train_fraction)

    
    def get_train_data(self):
        """
        Retruns the training part of the dataset
        """
        return self.train_data, self.train_labels


    def get_test_data(self):
        """
        Retruns the test part of the dataset
        """
        return self.test_data, self.test_labels


    def info(self):
        print("num data points = ", len(self.instances))
        print("num features = ", self.num_features)
        print("num_classes = ", self.num_classes)
        print("features = ", self.fields)
        print("classes = ", self.classes)
        print("regular data labels = ", self.regular_data_labels)


### helper functions

def floatify(str_list):
    return [float(x) for x in str_list]


def to_np_matrix(list):
    dimx = len(list)
    dimy = len(list[0])
    mat = np.zeros((dimx, dimy))
    for i in range(0, len(list)):
        mat[i] = list[i]

    return mat


def try_parse_time(time_str, format):
    try:
        t = datetime.strptime(time_str, format)
        return True, t
    except ValueError:
        return False, None


def parse_time(time_str):
    ok, t = try_parse_time(time_str, '%Y-%m-%d %H:%M:%S')
    if ok:
        return t

    ok, t = try_parse_time(time_str, '%Y-%m-%d %H:%M')
    if ok:
        return t

    # 10-03-21 12:21
    ok, t = try_parse_time(time_str, '%d-%m-%y %H:%M')
    if ok:
        return t

    return None

"""
if __name__ == '__main__':
    training_data = SWDataset("training.csv", train_fraction=1, window_length=1, use_location_for_ad=True)
    training_data.info()
    print("Total data points = ", len(training_data.get_train_data()[0]))
"""