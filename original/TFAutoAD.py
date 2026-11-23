"""
C4IIoT BACS Anomaly Detection Component

Anomaly detection models based on tensorflow autoencoders 

author: Milos Savic, UNSPMF (svc@dmi.uns.ac.rs)
"""

import tensorflow as tf
from keras.regularizers import l2
from sklearn.preprocessing import StandardScaler
import numpy as np
import pickle
import math

from BaseAD import BaseAD

import os
os.environ["TF_CPP_MIN_LOG_LEVEL"] = "3"

class TFAutoAD(BaseAD):
    """
    Tensorflow autoencoder AD class
    """
    
    def __init__(self, model=None, dataset=None, num_hidden_layers=1, num_epochs=100):
        """
        model            - the name of the model that will be loaded from the working directory
        dataset          - the name of the file that will be used to train the model
        num_epochs       - the number of epochs when training the model
        """
        if model != None:
            inf = open(model + ".ss", "rb")
            self.ss = pickle.load(inf)
            inf.close()

            inf = open(model + ".conf", "r")
            self.num_features = int(inf.readline()[:-1])
            self.mean_training_score = float(inf.readline()[:-1])
            self.stddev_training_score = float(inf.readline()[:-1])
            self.max_training_score = float(inf.readline()[:-1])
            num_basic_features = int(inf.readline()[:-1])
            self.features = []
            for _ in range(num_basic_features):
                self.features.append(inf.readline()[:-1])
            #print("Features [", len(self.features), "]", self.features)

            inf.close()

            self.model = tf.keras.models.load_model(model + ".h5")
            print("Model loaded")
            self.model.summary()
        
        elif dataset != None:
            super().__init__("TFAuto", None, dataset)
            if self.num_features < 4:
                raise ValueError("More than 3 features required")
    
            self.num_hidden_layers = num_hidden_layers
            self.initialize_model_structure(self.num_features)
            self.num_epochs = num_epochs
            self.model.compile(optimizer = tf.keras.optimizers.Adam(0.001), loss='mse', metrics=['mse'])
            #self.model.summary()
        

    def initialize_model_structure(self, num_features):
        hidden_conf = []
        if self.num_hidden_layers == 1:
            hidden_conf = [int(num_features / 2)]
        elif self.num_hidden_layers == 3:
            h0, h1 = int(num_features / 2), int(num_features / 4)
            hidden_conf = [h0, h1, h0]
        else:
            h0, h1, h2 = int(2 * num_features / 3), int(num_features / 2), int(num_features / 4)
            hidden_conf = [h0, h1, h2, h1, h0]

        self.model = tf.keras.Sequential()
        self.model.add(tf.keras.layers.Dense(hidden_conf[0], activation='relu', input_dim=num_features))
        for i in range(1, len(hidden_conf)):
            self.model.add(tf.keras.layers.Dense(hidden_conf[i], activation='relu', input_dim=num_features))
        self.model.add(tf.keras.layers.Dense(num_features))

        
    def prepare_training_data(self):
        train_data = self.dataset.get_train_data_npmatrix()
        self.ss = StandardScaler()
        self.ss.fit(train_data)
        train_data = self.ss.transform(train_data)
        return train_data


    def train(self):
        train_data = self.prepare_training_data()
        callback = tf.keras.callbacks.EarlyStopping(monitor='loss', patience=10)
        self.model.fit(train_data, train_data, epochs = self.num_epochs, batch_size=16, verbose=0, callbacks=[callback])
        
        # evaluate the model and compute training scores
        self.MSE = self.model.evaluate(train_data, train_data, verbose = 0)[0]
        self.compute_training_scores()
        

    def __evaluate(self, test_instance):
        test_instance = self.ss.transform(test_instance)
        test_scores = self.model.evaluate(test_instance, test_instance, verbose = 0)
        score = test_scores[0]
        #score = test_scores[0].item()   -- ok in tf 1.14, error in tf 2.2.0 
        return score


    def ad_inference_raw_score(self, test_instance):
        score = self.__evaluate(test_instance)
        return score > self.MSE, score

    
    def ad_inference(self, test_instance):
        score = self.__evaluate(test_instance)
        norm_score = self.normalize_score(score)
        return score > self.max_training_score, norm_score
        

    def save(self, model_name):
        self.model.save(model_name + ".h5")
        outf = open(model_name + ".ss", 'wb')
        pickle.dump(self.ss, outf)
        outf.flush()
        outf.close()

        outf = open(model_name + ".conf", "w")
        outf.write(str(self.num_features) + "\n")
        outf.write(str(self.mean_training_score) + "\n")
        outf.write(str(self.stddev_training_score) + "\n")
        outf.write(str(self.max_training_score) + "\n")
        outf.write(str(len(self.features)) + "\n")
        for f in self.features:
            outf.write(f + "\n")
        outf.close()

        self.save_tf_lite_format(model_name)
        self.export_ino_format(model_name + "_edge.h")


    def save_tf_lite_format(self, model_name):
        converter = tf.lite.TFLiteConverter.from_keras_model(self.model)
        tflite_model = converter.convert()

        # Save the model
        with open(model_name + '.tflite', 'wb') as f:
            f.write(tflite_model)


    def export_ino_format(self, file_name):
        outf = open(file_name, "w")

        outf.write("#include \"laei.h\"\n\n")
        outf.write("// params.txt\n")
        outf.write("config_t config = {\n")
        outf.write("\t" + str(self.num_features) + ",\n")
        outf.write("\t" + str(int(self.num_features / 2)) + ",\n")
        outf.write("\t" + str(self.max_training_score) + ",\n")
        outf.write("\t" + str(self.stddev_training_score) + "\n")
        outf.write("};\n\n")

        outf.write("double f_mean[] = {\n")
        for i in range(0, self.num_features):
            outf.write("\t" + str(self.ss.mean_[i]))
            if i < self.num_features - 1:
                outf.write(",")
            outf.write("\n") 
        outf.write("};\n\n")

        outf.write("double f_std[] = {\n")
        for i in range(0, self.num_features):
            outf.write("\t" + str(math.sqrt(self.ss.var_[i])))
            if i < self.num_features - 1:
                outf.write(",")
            outf.write("\n")
        outf.write("};\n\n")

        weights = self.model.get_weights()
        inp_layer = weights[0]
        outf.write("//weights.txt\n")
        outf.write("double w_inp_hid[] = {\n")
        for i in range(0, len(inp_layer)):
            node_weights = inp_layer[i]
            w = ",".join(map(str, node_weights))
            outf.write("\t" + w)
            if i < len(inp_layer) - 1:
                outf.write(",")
            outf.write("\n")               
        outf.write("};\n\n")
        
        for i in range(1, len(weights)):
            hid_layer = weights[i]
            outf.write("double w_hid_out[] = {\n")
            for i in range(0, len(hid_layer)):
                node_weights = hid_layer[i]
                w = ",".join(map(str, node_weights))
                outf.write("\t" + w)
                if i < len(hid_layer) - 1:
                    outf.write(",")
                outf.write("\n")
            outf.write("};")

        outf.close()


