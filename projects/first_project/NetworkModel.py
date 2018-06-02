import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split

# KERAS LIBRARIES
from keras.layers import Dense
from keras.layers import Dropout
from keras.models import Sequential
from keras.optimizers import SGD


class NetworkModel:

    # Defining constants...
    __random_seed = 7

    # # MODEL'S CONSTANTS
    __train_set_size = 0.7
    __test_set_size = 1 - __train_set_size

    __learning_rate = 0.025
    __batch_size = 20
    __epochs = 50

    model = None
    evaluation_result = dict()
    __test_set_x = None
    __test_set_y = None

    def __init__(self, path_to_claims, path_to_groundtruth):
        # Load all the claims
        print("Loading claims ...")
        self.claims_input = pd.read_csv(path_to_claims)
        # Load the ground truth
        print("Loading ground truth ...")
        self.ground_truth = pd.read_csv(path_to_groundtruth)
        self.__build_ground_truth_vector()

    def __build_ground_truth_vector(self):
        # Build the ground_truth vector.

        # tc_indexes is a dictionary that is used as inverted index.
        # foreach claim it is able to tell us the position in which put the value (1 / 0) for a claim
        tc_indexes = dict()
        tc_labels = np.array([], dtype=int)
        sources = set()

        # Add to the ground truth claims all the claims in the ground truth file and put each value at 1
        # Add to the ground truth claims also all the claims with the same propertyID and objectID
        # but have a different PropertyValue.
        # Add also every sources that says something in a set.
        for index, row in self.ground_truth.iterrows():
            tc_id = row["PropertyID"] + "|" + row["ObjectID"] + "|" + str(row["PropertyValue"])
            if tc_id not in tc_indexes:
                tc_indexes[tc_id] = tc_labels.size
                tc_labels = np.append(tc_labels, 1)
            filtered_claims = self.claims_input[self.claims_input["PropertyID"] == row["PropertyID"]]
            filtered_claims = filtered_claims[filtered_claims["ObjectID"] == row["ObjectID"]]

            for idx, claim in filtered_claims.iterrows():
                if str(claim["PropertyValue"]) != str(row["PropertyValue"]):
                    tc_id = claim["PropertyID"] + "|" + claim["ObjectID"] + "|" + str(claim["PropertyValue"])
                    if tc_id not in tc_indexes:
                        tc_indexes[tc_id] = tc_labels.size
                        tc_labels = np.append(tc_labels, 0)
                sources.add(claim["SourceID"])

        self.num_of_sources = len(sources)
        self.num_of_claims = tc_labels.size

        print("Number of claims :", self.num_of_claims)
        print("Number of sources:", self.num_of_sources)

        # Building the sensing matrix
        print("Building sensing matrix ...")
        claims_matrix = []

        for source_num, source in enumerate(sources):  # foreach claims
            claim_vector = np.zeros(len(tc_indexes), dtype=int)  # initialize the vector with the claims

            source_claims = self.claims_input[self.claims_input["SourceID"] == source]
            for index, row in source_claims.iterrows():
                row_claim = row["PropertyID"] + "|" + row["ObjectID"] + "|" + str(row["PropertyValue"])
                if row_claim in tc_indexes:
                    claim_vector[tc_indexes[row_claim]] = 1
            claims_matrix.append(claim_vector)
            if source_num % 200 == 0:
                print("Sources processed: %i " % source_num)
        print("Done...")

        claims_matrix = np.array(claims_matrix, dtype=int)

        sensing_matrix_with_truth = claims_matrix.transpose()

        tc_labels_shaped = tc_labels.reshape(sensing_matrix_with_truth.shape[0], 1)
        self.sensing_matrix_with_truth = np.append(sensing_matrix_with_truth, tc_labels_shaped, axis=1)

    def train_and_test_model(self, shl_units, thl_units, train_set_size=__train_set_size, random_seed=__random_seed):
        print("Splitting in test set and train set...")
        self.__test_set_size = 1 - train_set_size

        train_set, test_set = train_test_split(self.sensing_matrix_with_truth, train_size=train_set_size,
                                               test_size=self.__test_set_size, random_state=random_seed)

        # # EXTRACT LABELS (Yt) and SAMPLES (X) For TRAIN-SET
        train_set_x = train_set[:, 0:train_set.shape[1] - 1]
        train_set_y = train_set[:, train_set.shape[1] - 1]

        # # EXTRACT LABELS (Yt) and SAMPLES (X) For TEST-SET
        self.__test_set_x = test_set[:, 0:test_set.shape[1]-1]
        self.__test_set_y = test_set[:, test_set.shape[1]-1]

        self.model = Sequential([
            Dense(units=self.num_of_sources, input_dim=self.num_of_sources, activation='relu'),  # input layer
            Dropout(0.2, noise_shape=None, seed=random_seed),
            Dense(units=shl_units, activation='relu'),  # first hidden layer
            Dense(units=thl_units, activation='relu'),  # second hidden layer
            Dense(units=1, activation='sigmoid')  # output layer, 1 neuron,
        ])

        # # COMPILE THE MODEL

        # OPTIMIZER => SGD with a learning defined by the user.
        # LOSS => cross-entropy
        print("Compiling model ...")
        self.model.compile(SGD(lr=self.__learning_rate), loss="binary_crossentropy", metrics=["accuracy"])

        print("Train Model...")
        history = self.model.fit(train_set_x, train_set_y, batch_size=self.__batch_size, epochs=self.__epochs, verbose=0)

        print("Evaluating model ... ")
        evaluation = self.model.evaluate(x=self.__test_set_x, y=self.__test_set_y, batch_size=self.__batch_size, verbose=0)
        self.evaluation_result["loss"] = evaluation[0] * 100
        self.evaluation_result["accuracy"] = evaluation[1] * 100

    def evaluate_model(self):
        return "\n%s: %.2f%% - %s: %.2f%%" \
               % ("loss", self.evaluation_result["loss"], "accuracy", self.evaluation_result["accuracy"])
