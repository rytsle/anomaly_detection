"""
Experimental analysis of anomaly detection models

author: Milos Savic, UNSPMF (svc@dmi.uns.ac.rs)
"""

from Dataset import SWDataset
from TFAutoAD import TFAutoAD
from verify import Verifier
import statistics
from SKLAD import SVM_SKLAD
from PyODAD import ABOD_PyODAD, KNN_PyODAD, PCA_PyODAD, HBO_PyODAD
import datetime

# traininig dataset for anomaly detection on individual data points, NO-GPS case
training_data = SWDataset("training.csv", train_fraction=1, window_length=1, use_location_for_ad=False)
test_data = SWDataset("test.csv", train_fraction=0, window_length=1, use_location_for_ad=False)

# training dataset for anomaly detection on individual data points, GPS case
training_data_loc = SWDataset("training.csv", train_fraction=1, window_length=1, use_location_for_ad=True)
test_data_loc = SWDataset("test.csv", train_fraction=0, window_length=1, use_location_for_ad=True)

verifier = Verifier()

# function computing precision, recall and f1 scores
def compute_scores(method, test_dataset):
    td, tdt = test_dataset.get_test_data()
    anom_ts = []
    prev_anom = False
    for i in range(len(td)):
        dp = td[i]
        time = tdt[i]
        anom, cs = method.is_anomaly(dp)
        if not anom:
            cs = 1.0 - cs

        if anom:
            anom_ts.append((time, prev_anom))

        prev_anom = anom
        
    verifier = Verifier()
    precision, recall = verifier.compute_scores(anom_ts)

    f1_score = 0
    if precision + recall > 0:
        f1_score = 2 * precision * recall / (precision + recall)
    
    return precision, recall, f1_score

# function evaluating EDGE autoencoder anomaly detection models
def eval_edge_ae(K, training_data, test_data, msg, num_hidden_layers):
    print("\n" + msg)
    prec = []
    rec = []
    for _ in range(0, K):
        lightAE = TFAutoAD(dataset=training_data, num_hidden_layers=num_hidden_layers)
        lightAE.train()
        p, r, _ = compute_scores(lightAE, test_data)
        prec.append(p)
        rec.append(r)

    p = sum(prec) / len(prec)
    r = sum(rec) / len(rec)
    f1 = 0
    if p + r > 0:
        f1 = 2 * p * r / (p + r)

    print("Avg precision", sum(prec) / len(prec))
    if K > 1:
        print("STD precision", statistics.stdev(prec))
    print("Avg recall", sum(rec) / len(rec))
    if K > 1:
        print("STD recall", statistics.stdev(rec))

    print("F1-score = ", f1)

    
# function evaluting baseline anomaly detection models trained on individual data points
def eval_baseline_models(training_data, test_data):
    print("Evaluating SVM, single data points")
    svm = SVM_SKLAD(training_data)
    svm.train()
    p, r, f1 = compute_scores(svm, test_data)
    print("Precision", p, "Recall", r, "F1", f1)

    print("Evaluating ABOD")
    abod = ABOD_PyODAD(training_data)
    abod.train()
    p, r, f1 = compute_scores(abod, test_data)
    print("Precision", p, "Recall", r, "F1", f1)

    print("Evaluating KNN")
    knn = KNN_PyODAD(training_data)
    knn.train()
    p, r, f1 = compute_scores(knn, test_data)
    print("Precision", p, "Recall", r, "F1", f1)

    print("Evaluating PCA")
    pca = PCA_PyODAD(training_data)
    pca.train()
    p, r, f1 = compute_scores(pca, test_data)
    print("Precision", p, "Recall", r, "F1", f1)

    print("Evaluating HBO")
    hbo = HBO_PyODAD(training_data)
    hbo.train()
    p, r, f1 = compute_scores(hbo, test_data)
    print("Precision", p, "Recall", r, "F1", f1)


# function evaluating baseline anomaly detection models trained on timeseries
def eval_baseline_timeseries(model, max_ts_length, use_location_for_ad):
    print("\n\n\nExperiment started, model = ", model, "use_location = ", use_location_for_ad)
    aprec = []
    arec = []
    for ts_len in range(1, max_ts_length + 1):
        training_data = SWDataset("training.csv", train_fraction=1, window_length=ts_len, use_location_for_ad=use_location_for_ad)
        test_data = SWDataset("test.csv", train_fraction=0, window_length=ts_len, use_location_for_ad=use_location_for_ad)
        
        if model == "SVM":
            m = SVM_SKLAD(training_data)
        elif model == "ABOD":
            m = ABOD_PyODAD(training_data)
        elif model == "KNN":
            m = KNN_PyODAD(training_data)
        elif model == "PCA":
            m = PCA_PyODAD(training_data)
        elif model == "HBO":
            m = HBO_PyODAD(training_data)

        m.train()
        p, r, _ = compute_scores(m, test_data)
        
        aprec.append(p)
        arec.append(r)
    
    for i in range(0, len(aprec)):
        tsl = i + 1
        f1 = 0
        if aprec[i] + arec[i] > 0:
            f1 = 2 * aprec[i] * arec[i] / (aprec[i] + arec[i])
        print(str(tsl) + "," + str(aprec[i]) + "," + str(arec[i]) + "," + str(f1))


# function evaluating baseline models on individual data points in the GPS case
def eval_baselines_loc():
    print("BASELINE MODELS, INDIVIDUAL DATA POINTS, LOC (GPS CASE)")
    eval_baseline_models(training_data_loc, test_data_loc)


# function evaluating baseline models on individual data points in the NO-GPS case
def eval_baselines_woloc():
    print("BASELINE MODELS, INDIVIDUAL DATA POINTS, NO LOC (NO-GPS CASE)")
    eval_baseline_models(training_data, test_data)


# function evaluating baseline models on timeseries in the GPS case
def eval_baselines_timeseries_loc(max_ts_length=20):
    print("BASELINE MODELS, TIMESERIES, LOC (GPS CASE)")
    eval_baseline_timeseries("SVM", max_ts_length, True)
    eval_baseline_timeseries("ABOD", max_ts_length, True)
    eval_baseline_timeseries("KNN", max_ts_length, True)
    eval_baseline_timeseries("PCA", max_ts_length, True)
    eval_baseline_timeseries("HBO", max_ts_length, True)


# function evaluating baseline models on timeseries in the NO-GPS case
def eval_baselines_timeseries_woloc(max_ts_length=20):
    print("BASELINE MODELS, TIMESERIES, NO-LOC (NO-GPS CASE)")
    eval_baseline_timeseries("SVM", max_ts_length, False)
    eval_baseline_timeseries("ABOD", max_ts_length, False)
    eval_baseline_timeseries("KNN", max_ts_length, False)
    eval_baseline_timeseries("PCA", max_ts_length, False)
    eval_baseline_timeseries("HBO", max_ts_length, False)


# function evaluating EDGE ADM in the GPS case
def eval_edge_ae_loc(K=20):
    print("K = ", K)
    eval_edge_ae(K, training_data_loc, test_data_loc, "Evaluating , location", 1)
    eval_edge_ae(K, training_data_loc, test_data_loc, "Evaluating , location", 3)
    eval_edge_ae(K, training_data_loc, test_data_loc, "Evaluating , location", 5)


# function evaluating EDGE ADM in the NO-GPS case
def eval_edge_ae_woloc(K=20):
    print("K = ", K)
    eval_edge_ae(K, training_data, test_data, "Evaluating LightAE, without location", 1)
    eval_edge_ae(K, training_data, test_data, "Evaluating LightAE, without location", 3)
    eval_edge_ae(K, training_data, test_data, "Evaluating LightAE, without location", 5)


# function evaluating FOG ADM for timeseries in the interval [1, max_ts_length]
def eval_fog_ae(K, max_ts_length, num_layers, use_location_for_ad):
    eval_fog_ae_custom(K, list(range(1, max_ts_length + 1)), num_layers, use_location_for_ad)


# function evaluating FOG ADM for timeseries in the interval [min, max]
def eval_fog_ae_mm(K, min, max, num_layers, use_location_for_ad):
    eval_fog_ae_custom(K, list(range(min, max + 1)), num_layers, use_location_for_ad)


# function evaluating FOG ADM for timeseries contained in tslens list
def eval_fog_ae_custom(K, tslens, num_layers, use_location_for_ad):
    print("\n\n\nExperiment started, num_layers = ", num_layers, " use_location = ", use_location_for_ad)
    aprec = []
    arec = []
    for ts_len in tslens:
        print("Experiments with timeseries length", ts_len)
        training_data = SWDataset("training.csv", train_fraction=1, window_length=ts_len, use_location_for_ad=use_location_for_ad)
        test_data = SWDataset("test.csv", train_fraction=0, window_length=ts_len, use_location_for_ad=use_location_for_ad)
        prec = []
        rec = []
        for i in range(0, K):
            if num_layers == 3:
                ae = TFAutoAD(dataset=training_data, num_hidden_layers=3)
            elif num_layers == 5:
                ae = TFAutoAD(dataset=training_data, num_hidden_layers=5)

            ae.train()
            p, r, _ = compute_scores(ae, test_data)
            prec.append(p)
            rec.append(r)

        ap = sum(prec) / len(prec)
        ar = sum(rec) / len(rec)
        print("AVG(Prec)", ap, "AVG(Rec)", ar)
        aprec.append(ap)
        arec.append(ar)
    
    loc_info = "location included " if use_location_for_ad else "NO LOCATION" 
    print("\n\n\nFINAL RESULTS FOR FoGAE," + str(num_layers) + "layers, " + loc_info)
    for i in range(0, len(aprec)):
        tsl = tslens[i]
        f1 = 0
        if aprec[i] + arec[i] > 0:
            f1 = 2 * aprec[i] * arec[i] / (aprec[i] + arec[i])
        print(str(tsl) + "," + str(aprec[i]) + "," + str(arec[i]) + "," + str(f1))


# function evaluating FOG ADM with 3 hidden layers, GPS case
def eval_fog_3_ae_loc(K=20, MIN_TS=1, MAX_TS=20):
    print("K = ", K, "MIN_TS = ", MIN_TS, "MAX_TS = ", MAX_TS)
    eval_fog_ae_mm(K, MIN_TS, MAX_TS, 3, True)

# function evaluating FOG ADM with 3 hidden layers, NO-GPS case
def eval_fog_3_ae_woloc(K=20, MIN_TS=1, MAX_TS=20):
    print("K = ", K, "MIN_TS = ", MIN_TS, "MAX_TS = ", MAX_TS)
    eval_fog_ae_mm(K, MIN_TS, MAX_TS, 3, False)

# function evaluating FOG ADM with 5 hidden layers, GPS case
def eval_fog_5_ae_loc(K=20, MIN_TS=1, MAX_TS=20):
    print("K = ", K, "MIN_TS = ", MIN_TS, "MAX_TS = ", MAX_TS)
    eval_fog_ae_mm(K, MIN_TS, MAX_TS, 5, True)

# function evaluating FOG ADM with 5 hidden layers, NO-GPS case
def eval_fog_5_ae_woloc(K=20, MIN_TS=1, MAX_TS=20):
    print("K = ", K, "MIN_TS = ", MIN_TS, "MAX_TS = ", MAX_TS)
    eval_fog_ae_mm(K, MIN_TS, MAX_TS, 5, False)


if __name__ == '__main__':
    import sys

    arguments = len(sys.argv) - 1
    if arguments != 1:
        print("The script should be called with one argument")
        print("Valid arguments are:")
        print("EDGE_ADM       -- evaluating edge adm models")
        print("FOG3_ADM       -- evaluating fog adm models with 3 hidden layers")
        print("FOG5_ADM       -- evaluaring fog adm models with 5 hidden layers")
        print("EDGE_BASELINES -- evaluating edge baselines")
        print("FOG_BASELINES  -- evaluating fog baselines")
        sys.exit(1)


    antype = sys.argv[1]
    print(datetime.datetime.now())

    if antype == "EDGE_ADM":
        print("EVALUATING EDGE AE")
        eval_edge_ae_loc()
        eval_edge_ae_woloc()
    elif antype == "FOG3_ADM":
        print("EVALUATING FOG AE WITH 3 HIDDEN LAYERS")
        eval_fog_3_ae_loc()
        eval_fog_3_ae_woloc()
    elif antype == "FOG5_ADM":
        print("EVALUATING FOG AE WITH 5 HIDDEN LAYERS")
        eval_fog_5_ae_loc()
        eval_fog_5_ae_woloc()
    elif antype == "EDGE_BASELINES":
        print("EVALUATING EDGE BASELINES")
        eval_baselines_loc()
        eval_baselines_woloc()
    elif antype == "FOG_BASELINES":
        print("EVALUATING FOG BASELINES")
        eval_baselines_timeseries_loc()
        eval_baselines_timeseries_woloc()
    else:
        print("Unknown analysis type")

    print(datetime.datetime.now())