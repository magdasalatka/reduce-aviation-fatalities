# -*- coding: utf-8 -*-

import pickle
import random
from time import time
import numpy as np
import tensorflow as tf
import tensorflow.keras.layers as layers
from sklearn.metrics import accuracy_score
from snippets import get_random_parameters

def train_neural_net(train_set, test_set, label, training_time, store_intermediate_results=False):
    """ Train neural networks with randomly generated hyperparameters: learning rate, learning rate
    decay and number of layer. Model: fully connected NN for multiclass classification.

    Args:
        train_set(pandas df):                       training set
        test_set(pandas df):                        test set, same features as in training set
        label(str):                                 feature with data labels
        training_time(float):                       training time (in hours)
        store_intermediate_results(bool, optional): True for saving model at the end of training, False otherwise

    Returns:
        all_models(list of keras.model):            neural networks models
        accuracy(list of 2 (N,) np arrays):         in sample (accuracy[0]) and out of sample (accuracy[1]) accuracy
        parameters(list of 3 (N,) np arrays):       hyperparameters: learning rates (parameters[0]),
                                                                     learning rate decays (parameters[1]),
                                                                     num fo layers (parameters[2]),
    """

    PARAM_RANGE = {
        "learning_rate": (1e-1, 1e-6),
        "layers": (10, 1e3),
        "lr_decay": (0.5, 1e-8)
    }
    BATCH_NORM = False
    EPOCHS = 100
    BATCH_SIZE = 1000
    BETA_1 = 0.9
    BETA_2 = 0.999

    PARAM_FILE = "deep_net_stats"
    MODEL_FILE = "deep_net_model_"

    all_models = []
    accuracy = [[], []]
    learning_rate = []
    lr_decay = []
    deep_layers = []

    features = list(train_set)
    features.remove(label)
    num_class = len(np.unique(train_set[label]))

    i = 0
    timeout = time() + 60 * 60 * training_time

    while time() < timeout:

        learning_rate.append(get_random_parameters(PARAM_RANGE["learning_rate"], True, False))
        lr_decay.append(bool(random.getrandbits(1)) * get_random_parameters(PARAM_RANGE["lr_decay"], True, False))
        deep_layers.append(get_random_parameters(PARAM_RANGE["layers"], False, True))

        # instantiate model
        model = tf.keras.models.Sequential()

        # Input layers
        model.add(layers.Dense(10, input_dim=train_set[features].shape[1]))
        if BATCH_NORM:
            model.add(layers.BatchNormalization())
        model.add(layers.Activation('relu'))

        # Intermediary layers
        model.add(layers.Dense(deep_layers[i]))
        if BATCH_NORM:
            model.add(layers.BatchNormalization())
        model.add(layers.Activation('relu'))

        # Output layer
        model.add(layers.Dense(num_class))
        if BATCH_NORM:
            model.add(layers.BatchNormalization())
        model.add(layers.Activation('softmax'))

        adamOptimizer = tf.keras.optimizers.Adam(lr=learning_rate[i],
                                                 decay=lr_decay[i],
                                                 beta_1=BETA_1,
                                                 beta_2=BETA_2,
                                                 epsilon=None,
                                                 amsgrad=False)
        model.compile(optimizer=adamOptimizer,
                      loss='categorical_crossentropy',
                      metrics=['accuracy'])

        curr_model = model.fit(train_set[features], tf.keras.utils.to_categorical(train_set[label]), epochs=EPOCHS,
                               batch_size=BATCH_SIZE, verbose=0)
        all_models.append(curr_model)

        j = 0
        for dataset in (train_set, test_set):
            predicted = np.argmax(model.predict(dataset[features]), axis=1)
            accuracy[j] = np.append(accuracy[j], accuracy_score(dataset[label], predicted))
            j = j + 1

        if store_intermediate_results:
            with open(PARAM_FILE, "wb") as f:
                pickle.dump(4, f)
                pickle.dump(learning_rate, f)
                pickle.dump(lr_decay, f)
                pickle.dump(deep_layers, f)
                pickle.dump(accuracy[j], f)

            curr_model.model.save(MODEL_FILE + str(i) + '.h5')

        i = i + 1

    parameters = [learning_rate, lr_decay, deep_layers]
    return all_models, accuracy, parameters
