import lightgbm as lgb
from sklearn.metrics import accuracy_score
import numpy as np
from time import time


def train_lgb_model(train_set, test_set, label, training_time):

    PARAM_RANGE = {
        "learning_rate": (1e-1, 1e-6),
        "max_bin": (10, 1e3),
        "num_leaves": (10, 10*train_set.shape[1]-1)
    }
    MIN_CHILD_WEIGHT = 50
    BAGGING_FRACTION = 0.7
    FEATURE_FRACTION = 0.7
    EARLY_STOPPING_ROUND= 50
    NUM_BOOST_ROUND = 10000

    accuracy = [[], []]
    all_models = []
    learning_rate = []
    max_bin = []
    num_leaves = []

    features = list(train_set)
    features.remove(label)
    num_class = 4

    params = {"objective": "multiclass",
              "num_class": num_class,
              "metric": "multi_error",
              "min_child_weight": MIN_CHILD_WEIGHT,
              "bagging_fraction": BAGGING_FRACTION,
              "feature_fraction": FEATURE_FRACTION,
              "num_leaves": [],
              "max_bin": [],
              "learning_rate": [],
              "bagging_seed": 420,
              "verbosity": -1
              }

    i = 0
    timeout = time() + 60*60*training_time

    while time() < timeout:

        learning_rate.append(10 ** (np.random.uniform(*np.log10(PARAM_RANGE["learning_rate"]))))
        max_bin.append(int(10 ** (np.random.uniform(*np.log10(PARAM_RANGE["max_bin"])))))
        num_leaves.append(int(np.random.uniform(*PARAM_RANGE["num_leaves"])))

        params["learning_rate"] = learning_rate[i]
        params["max_bin"] = max_bin[i]
        params["num_leaves"] = num_leaves[i]

        lgb_train = lgb.Dataset(train_set[features], train_set[label])
        lgb_test = lgb.Dataset(test_set[features], test_set[label])

        curr_model = lgb.train(params, lgb_train, valid_sets=lgb_test,
                               num_boost_round=NUM_BOOST_ROUND,
                               early_stopping_rounds=EARLY_STOPPING_ROUND,
                               verbose_eval=False)
        all_models.append(curr_model)

        j = 0
        for dataset in (train_set, test_set):

            probabilities = curr_model.predict(dataset[features], num_iteration=curr_model.best_iteration)
            predicted = np.argmax(probabilities, axis=1)
            accuracy[j] = np.append(accuracy[j], accuracy_score(dataset[label], predicted))
            j = j+1

    parameters = [learning_rate, max_bin, num_leaves]
    return all_models, accuracy, parameters