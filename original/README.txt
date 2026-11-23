Data and code for experimental analyses described in 
   Deep Learning Anomaly Detection for Cellular IoT with Applications in Smart Logistics
by
   Milos Savic, Milan Lukic, Dragan Danilovic, Zarko Bodroski, Dragana Bajovic, Ivan Mezei, Dejan Vukobratovic, Srdjan Skrbic and Dusan Jakovetic
from
   University of Novi Sad, Serbia
   VIP mobile, Serbia
published in
   IEEE Access, doi: 10.1109/ACCESS.2021.3072916 

Corresponding author: Milos Savic, svc@dmi.uns.ac.rs
arxiv link: https://arxiv.org/abs/2102.08936


Files
=====
- traininig.csv        - the dataset for trainining anomaly detection models
- test.csv             - the dataset for testing anomaly detection models
- anomalies.timestamps - the list of timestamps of anomalous events in the test dataset
- Dataset.py           - BASC module for loading datasets
- BaseAD.py            - BACS module containinig base classes for anomaly detection models
- SKLAD.py             - BACS module realizing anomaly detection models based on algorithms from scikit-learn
- PyODAD.py            - BACS module realizing anomaly detection models based on algorithms from PyOD
- TFAutoAD.py          - BACS module realizing anomaly detection models based on Tensorflow autoencoders
- verify.py            - module for verifying results of anomaly detection models using information from anomalies.timestamps
- experiments.py       - module implementing experimental analyses presented in the paper


Dependencies
============
numpy                  1.18.5
pandas                 1.0.4
scikit-learn           0.23.1
scipy                  1.4.1
pyod                   0.8.7
tensorflow             2.2.0 
Keras                  2.3.1


To run experiments
==================
$ python experiments.py <arg>
Valid arguments are:
EDGE_ADM       -- evaluating edge adm models
FOG3_ADM       -- evaluating fog adm models with 3 hidden layers
FOG5_ADM       -- evaluaring fog adm models with 5 hidden layers
EDGE_BASELINES -- evaluating edge baselines
FOG_BASELINES  -- evaluating fog baselines


