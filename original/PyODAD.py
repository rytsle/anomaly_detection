"""
C4IIoT BACS Anomaly Detection Component

Anomaly detection models based on PyOD

authors: Vladimir Jankov & Tamara Krivokuca (UNSPMF)
updates by: Milos Savic, UNSPMF (svc@dmi.uns.ac.rs)
"""

import numpy as np
from BaseAD import BaseAD, tostr
from pyod.models import knn, pca, hbos, cblof, lscp, abod


class PyODAD(BaseAD):
    """
    PyOD AD models
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
        score = self.ad_method.decision_function(test_instance)[0]
        return res, score


    def ad_inference_raw_score(self, test_instance):
        res, score = self.__do_inference(test_instance)
        return res == 1, score

    
    def ad_inference(self, test_instance):
        res, score = self.__do_inference(test_instance)
        norm_score = self.normalize_score(score)
        return res == 1, norm_score
   

class ABOD_PyODAD(PyODAD):
    def __init__(self, dataset, outliers_fraction=0.03):
        ad_method = abod.ABOD(contamination=outliers_fraction, n_neighbors=10)
        super().__init__("ABOD", ad_method, dataset)     


class KNN_PyODAD(PyODAD):
    def __init__(self, dataset, outliers_fraction=0.03):
        ad_method = knn.KNN(contamination=outliers_fraction, n_neighbors=10)
        super().__init__("KNN", ad_method, dataset)    


class PCA_PyODAD(PyODAD):
    def __init__(self, dataset, outliers_fraction=0.03):
        ad_method = pca.PCA(n_components=10, n_selected_components=10,\
            contamination = outliers_fraction)
        super().__init__("PCA", ad_method, dataset)


class HBO_PyODAD(PyODAD):
    def __init__(self, dataset, outliers_fraction=0.03):
        ad_method =  hbos.HBOS(n_bins=10, alpha=0.1, tol=0.5,\
            contamination = outliers_fraction)
        super().__init__("HBO", ad_method, dataset)
