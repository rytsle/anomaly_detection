"""
C4IIoT BACS Anomaly Detection Component

The base module for anomaly detection models

author: Milos Savic, UNSPMF (svc@dmi.uns.ac.rs)
"""

import numpy as np
import pickle
import math

from abc import ABC, abstractmethod  
from Dataset import SWDataset
import statistics as stat
from sklearn.metrics import precision_score, recall_score, accuracy_score


class BaseAD(ABC):
    """
    The base class for AD models
    """
    
    def __init__(self, model_name, ad_method, dataset, mse_thr=0.05):
        """
        model_name - anomaly detection model name
        ad_method  - anomaly detection method
        dataset - an object of SWDataset to train the model
        """
        self.model_name = model_name
        self.ad_method = ad_method
        self.dataset = dataset
        self.num_features = dataset.num_features * dataset.window_length
        self.features = dataset.features
        self.mse_thr = mse_thr
        

    @abstractmethod
    def train(self):
        pass

    
    def train_from_npmatrix(self):
        """
        Train the AD model using the numpy matrix representation
        of the training dataset
        """
        td = self.dataset.get_train_data_npmatrix()    
        self.ad_method.fit(td)
        self.compute_training_scores()


    def compute_training_scores(self):
        """
        Computes the mean and stdev of outlier scores for training 
        data points
        """
        train_data = self.dataset.get_train_data()[0]
        scores = []
        for instance in train_data:
            _, score = self.is_anomaly_raw_score(instance)
            scores.append(score)
    
        self.mean_training_score = stat.mean(scores)
        self.stddev_training_score = stat.stdev(scores)

        scores.sort(reverse=True)
        top_thr = int(self.mse_thr * len(scores))
        self.max_training_score = scores[top_thr]

        
    @abstractmethod
    def ad_inference(self, test_instance):
        """ 
        Derived implementations should return X, Y where 
            X is a boolean value, true means anomaly detected, false means regular data point
            Y is a normalized confidence score in interval [-1, 1]
        """
        pass


    @abstractmethod
    def ad_inference_raw_score(self, test_instance):
        """ 
        Derived implementations should return X, Y where 
            X is a boolean value, true means anomaly detected, false means regular data point
            Y is a raw outlier score returned by the anomaly detection method 
        """
        pass


    def is_anomaly_raw_score(self, feature_values):
        """
        Inference function returning raw confidence score
        Returns ANOMALY_DETECTED (boolean), CONFIDENCE_SCORE (float)
        """
        test_instance = make_np_test_instance(feature_values, self.num_features)
        return self.ad_inference_raw_score(test_instance)


    def is_anomaly(self, feature_values):
        """
        Inference function
        Returns ANOMALY_DETECTED (boolean), CONFIDENCE_SCORE (float)
        """
        test_instance = make_np_test_instance(feature_values, self.num_features)
        return self.ad_inference(test_instance)

    
    def test(self, out_file):
        """
        Makes AD inference for all instances in test data
        """
        f = open(out_file, "w")
        total_data_points = 0
        detected_anomalies = 0
        for test_instance in self.dataset.get_test_data()[0]:
            anomaly_detected, score = self.is_anomaly(test_instance)
            total_data_points += 1
            if anomaly_detected:
                instance = tostr(test_instance)
                f.write(str(score) + "," + instance + "\n")
                detected_anomalies += 1
            
        f.close()
        print("Num test data points = ", total_data_points)
        print("Detected anomalies   = ", detected_anomalies)


    def info(self):
        print("model = " + self.model_name)


    def normalize_score(self, score):
        """
        Normalize outlier score to be in interval [-1, 1]
        """
        diff = score - self.max_training_score
        diff /= self.stddev_training_score
        return 1 / (1 + math.exp(-diff))


    def get_features(self):
        return self.features


class BaseSAD(ABC):
    """
    The base class for supervised AD models
    """
    def __init__(self, model_name, classfier_method, dataset):
        """
        model_name             - anomaly detection model name
        dataset                - an object of LDPDataset to train the model
        classfier_method       - classification method
        """
        self.model_name = model_name
        self.dataset = dataset
        self.num_features = dataset.num_features
        self.classifier_method = classfier_method
        self.regular_data_labels = dataset.regular_data_labels

    
    @abstractmethod
    def train(self):
        pass


    @abstractmethod
    def sad_inference(self, test_instance):
        """
        Derived implementations should return X, Y where 
            X is class label
            Y is prediction confidence
        """


    def is_anomaly(self, feature_values):
        """
        Inference function
        Returns ANOMALY_DETECTED (boolean), ANOMALY_TYPE (string), CONFIDENCE_SCORE (float)
        """
        test_instance = make_np_test_instance(feature_values, self.num_features)
        class_label, confidence = self.sad_inference(test_instance)
        anom = class_label not in self.regular_data_labels
        return anom, class_label, confidence


    def evaluate(self):
        test_data, test_labels = self.dataset.get_test_data()
        print("Test data points = ", len(test_data))
        predictions = []
        for tdp in test_data:
            _, class_label, _ = self.is_anomaly(tdp)
            predictions.append(class_label)

        acc = accuracy_score(test_labels, predictions)
        print("Labels = ", self.dataset.classes)
        prec = precision_score(test_labels, predictions, labels = list(self.dataset.classes), average = None, zero_division = 0)
        rec = recall_score(test_labels, predictions, labels = list(self.dataset.classes), average = None, zero_division = 0) 
        print("Accuracy", acc)
        print("Precision", prec)
        print("Recall", rec)
        print("\n")


def save_model(model, out_file):
    """
    Save sklearn/pyod AD model to a file 
    """
    print("Saving model to " + out_file)
    outf = open(out_file, "wb") 
    del model.dataset
    pickle.dump(model, outf)
    outf.flush()
    outf.close()


def load_model(in_file):
    """
    Load sklearn/pyod AD model to a file 
    """
    print("Loading model from " + in_file)
    inf = open(in_file, "rb")
    ret = pickle.load(inf)
    inf.close()
    return ret


def make_np_test_instance(feature_values, num_required_features):
    if num_required_features != len(feature_values):
        raise ValueError(str(num_required_features) + " feature values required. " + str(len(feature_values)) + " features provided")

    test_instance = np.zeros((1, len(feature_values)))
    cnt = 0
    for fv in feature_values:
        test_instance[0][cnt] = fv
        cnt += 1

    return test_instance


### Utilities

def tostr(l):
    s = ""
    lenl = len(l)
    for i in range(0, lenl):
        s += str(l[i])
        if i < lenl - 1:
            s += ","
    return s
