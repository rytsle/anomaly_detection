"""
C4IIoT BACS Anomaly Detection Component

Anomaly detection models based on scikit-learn 

author: Milos Savic, UNSPMF (svc@dmi.uns.ac.rs)
"""

import numpy as np

from BaseAD import BaseAD, tostr

from sklearn import svm
from sklearn.covariance import EllipticEnvelope
from sklearn.ensemble import IsolationForest
from sklearn.neighbors import LocalOutlierFactor

class SKLAD(BaseAD):
    """
    Scikit-learn AD models
    """

    def __init__(self, model_name, ad_method, dataset):
        """
        model_name - anomaly detection model name
        ad_method - anomaly detection algorithm
        dataset - an object of SWDataset to train the model
        """
        super().__init__(model_name, ad_method, dataset)
       
    
    def train(self):
        self.train_from_npmatrix()


    def __do_inference(self, test_instance):
        res = self.ad_method.predict(test_instance)
        score = self.ad_method.score_samples(test_instance)[0]
        return res, score


    def ad_inference_raw_score(self, test_instance):
        res, score = self.__do_inference(test_instance)
        # low SKLAD scores indicate anomalies
        return res == -1, -1.0 * score

    
    def ad_inference(self, test_instance):
        res, score = self.__do_inference(test_instance)
        # low SKLAD scores indicate anomalies
        norm_score = self.normalize_score(-1.0 * score)
        return res == -1, norm_score


class EE_SKLAD(SKLAD):
    def __init__(self, dataset, outliers_fraction=0.03):
        ad_method = EllipticEnvelope(contamination = outliers_fraction, support_fraction=0.9)
        super().__init__("EE", ad_method, dataset)

class SVM_SKLAD(SKLAD):
    def __init__(self, dataset, outliers_fraction=0.03):
        ad_method = svm.OneClassSVM(nu=outliers_fraction, gamma='scale')
        super().__init__("SVM", ad_method, dataset)

class LOF_SKLAD(SKLAD):
    def __init__(self, dataset, outliers_fraction=0.03):
        ad_method = LocalOutlierFactor(n_neighbors=100, contamination=outliers_fraction, novelty=True)
        super().__init__("LOF", ad_method, dataset)

class IF_SKLAD(SKLAD):
    def __init__(self, dataset, outliers_fraction=0.03):
        ad_method = IsolationForest(n_estimators=20, contamination='auto')
        super().__init__("IF", ad_method, dataset)
