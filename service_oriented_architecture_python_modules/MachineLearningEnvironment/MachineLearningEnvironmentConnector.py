# !DOCUMENTATION SPHINX STYLE

# -*- PingMyHealth -*-
# Rik Wachner - 1720651 - PingMyHealth Project 2020 - IIT

"""
PingMyHealth machine learning environment
----------------------------------------------------------------------------

Simple machine learning environment to use a model and save the result

"""
from datetime import datetime, timezone
from influxdb import InfluxDBClient
from sklearn.model_selection import train_test_split
from sklearn.neighbors import KNeighborsClassifier
from sklearn.preprocessing import StandardScaler
import pandas as pd
import time

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
version = "1.0.0"
model_version = "1.0.0"
influxdb_server_host, influxdb_server_port = "localhost", 8086
write_database_name = "ml_environment_db"
read_database_name = "modbus_i_o_db"
model_classifier = "sklearn_KNeighborsClassifier"
measurement_name = "hearth_disease_prediction"
data_sampling_rate = 30
health_data = {
    "fitnessband_input_register": ["Age", "Sex", "Pulse", "Systolic blood pressure value"],
    "cholesterin_fastchecker_input_register": ["Cholesterin"]
}
health_data_field = 'valueScaled'


def initialize_model():
    """ Initialize the sklearn kneighborsclassifier model with hearth disease dataset
    """
    log.info('LOAD CSV DATA...')
    df = pd.read_csv("heart.csv")
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
    return model, model.score(X_Y_N_test, Z_test)


def database_connection():
    """ Connect to the database
    """
    client = InfluxDBClient(influxdb_server_host, influxdb_server_port)
    client.create_database(write_database_name)
    return client


def run_server():
    """Start the machine learning environment server
    """
    try:
        log.info('CONNECTING TO THE DATABASE SERVER...')
        influxdb_client = database_connection()
        log.info('CONNECTING TO THE DATABASE SERVER SUCCESSFULLY')

        log.info('USE KNEIGHBORSCLASSIFIER MODEL...')
        model, model_score = initialize_model()
        log.info('USE KNEIGHBORSCLASSIFIER MODEL SUCCESSFULLY')

        while True:
            log.info('READ DATABASE DATA..')
            influxdb_client.switch_database(read_database_name)
            values = []
            for measurement in health_data:
                for description in health_data[measurement]:
                    python_generator_iterator = influxdb_client.query(
                        "SELECT * FROM " + measurement + " GROUP BY * ORDER BY DESC LIMIT 1").get_points(
                        tags={'description': description})
                    for value in python_generator_iterator:
                        values.append(value[health_data_field])
            log.info('READ DATABASE DATA SUCCESSFULLY')
            log.debug(values)
            prediction = bool(model.predict([values]))
            log.debug("PREDICTION: POSSIBLE HEARTH DISEASE = %r  WITH %s %% PREDICTION" % (prediction, model_score))
            log.info('STARTING TO FORMAT COLLECTED DATA FOR THE DATABASE...')
            timestamp = datetime.now(timezone.utc)
            formated_data = [{
                'measurement': measurement_name,
                'time': timestamp,
                'tags': {
                    'scriptVersion': version,
                    'classifiere': model_classifier,
                    'modelVersion': model_version
                },
                'fields': {
                    'prediction': prediction,
                    'percentage': model_score
                }
            }]
            log.debug(formated_data)
            log.info('WRITE FORMATED DATA TO THE DATABASE...')
            influxdb_client.switch_database(write_database_name)
            influxdb_client.write_points(formated_data)
            log.info('WRITING TO THE DATABASE SERVER SUCCESSFULLY')
            time.sleep(data_sampling_rate)
    except Exception as e:
        log.error('SERVER FATAL ERROR: ' + str(e))


if __name__ == "__main__":
    run_server()
