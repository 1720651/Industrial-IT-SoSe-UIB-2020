# !DOCUMENTATION SPHINX STYLE

# -*- PingMyHealth -*-
# Rik Wachner - 1720651 - PingMyHealth Project 2020 - IIT

"""
PingMyHealth Train Model
----------------------------------------------------------------------------

Simple machine learning environment to train a model and save it as pickle

"""
from sklearn.model_selection import train_test_split
from sklearn.neighbors import KNeighborsClassifier
from sklearn.preprocessing import StandardScaler
import pandas as pd
import time
import joblib

# ----------------------------------------------------------------------- #
# LOGGING                                                                 #
# ----------------------------------------------------------------------- #
import logging

logging.basicConfig()
log = logging.getLogger()
log.setLevel(logging.DEBUG)

# ----------------------------------------------------------------------- #
# PARAMS                                                                  #
# ----------------------------------------------------------------------- #
# NONE

def initialize_model():
    """ Initialize the sklearn kneighborsclassifier model with hearth disease dataset
    """
    try:
        log.info('LOAD CSV DATA...')
        df = pd.read_csv("hearth.csv")
        log.info('DATA SOURCE: https://www.kaggle.com/johnsmith88/heart-disease-dataset/data')
        log.info('LOAD CSV DATA SUCCESSFULLY')

        log.info('TRANSFORM X_Y_N and Z FROM DATAFRAME...')
        X_Y_N = df[["age", "sex", "trestbps", "chol", "thalach"]].values
        Z = df["target"].values
        log.info('TRANSFORM X_Y_N and Z FROM SUCCESSFULLY...')

        log.info('SPLIT TRAIN AND TEST DATA...')
        X_Y_N_train, X_Y_N_test, Z_train, Z_test = train_test_split(X_Y_N, Z, test_size=0.25)
        log.info('SPLIT TRAIN AND TEST DATA SUCCESSFULLY')

        log.info('SCALE DATA...')
        scaler = StandardScaler()
        scaler.fit(X_Y_N_train)
        X_Y_N_train = scaler.transform(X_Y_N_train)
        X_Y_N_test = scaler.transform(X_Y_N_test)
        log.info('SCALE DATA SUCCESSFULLY')

        log.info('BUILD AND TRAIN MODEL...')
        model = KNeighborsClassifier(n_neighbors=4)
        model.fit(X_Y_N_train, Z_train)
        log.info('BUILD AND TRAIN MODEL SUCCESSFULLY')
        joblib.dump(model, 'trained_model.pkl', compress=9)
        return
    except Exception as e:
        log.error('INITIALISATION ERROR: ' + str(e))


if __name__ == "__main__":
    initialize_model()
