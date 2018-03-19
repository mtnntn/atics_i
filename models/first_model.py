import numpy as np
from sklearn.model_selection import train_test_split

from keras.layers import Dense
from keras.models import Sequential
from keras.optimizers import SGD

# DEFINE CONSTANTS
random_seed = 7

# # INSTANCE'S CONSTANTS
sources_num = 8

# # MODEL'S CON STANTS
train_set_size = 0.9

learning_rate = 0.001
batch_size = 10
epochs = 50  # train iterations

# PRE-PROCESS DATA

# I will have a social sensing matrix.
# Each row represent sources and what this sources claim for each claims
# Each Column is therefore a claim

# The input of the net is a vector [S1Ci, S2Ci, ..., SmCi]
# In other word the input are the columns of the SC matrix.

# # LOAD DATASET
raw_dataset = np.loadtxt("dataset/dataset.csv", delimiter=",")

# # SPLIT IN TRAIN SET AND DATA SET.
train_set, test_set = train_test_split(raw_dataset, train_size=train_set_size, random_state=random_seed)

# # EXTRACT LABELS (Yt)
train_labels = train_set[:, 8]

# # ETRACT SAMPLES (X)
train_samples = train_set[:, 0:8]


# DEFINE THE MODEL

fhl_units = sources_num*2
shl_units = sources_num*2
thl_units = sources_num*2

model = Sequential([
    Dense(units=fhl_units, input_dim=sources_num, activation='relu'),  # input layer
    Dense(units=shl_units, activation='relu'),  # first hidden layer
    Dense(units=thl_units, activation='relu'),  # second hidden layer
    Dense(units=1, activation='sigmoid')    # output layer, 1 neurons,
])


# # COMPILE THE MODEL

# OPTIMIZER => SGD with a learning defined by the user.
# LOSS => cross-entropy

model.compile(SGD(lr=learning_rate), loss="binary_crossentropy", metrics=["accuracy"])

# # FIT THE MODEL

history = model.fit(train_samples, train_labels, batch_size=batch_size, epochs=epochs, verbose=2)

# # MAKE A PREDICTION

first = test_set[0]
yt = first[8, ]
x = first[0:8, ]

print("First sample on test set: " + str(test_set[0]))
print("yt = " + str(yt))
print("x = " + str(x))

y = model.predict(np.array([x]))

print(y)
