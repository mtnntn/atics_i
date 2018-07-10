import pandas
import numpy as np
import tensorflow as tf
import gensim
from gensim.models import word2vec
import pandas as pd



opeds_df = pd.read_csv('flight.csv', encoding='utf-8')
pandas.set_option('mode.chained_assignment', None)
datasetcsv = pandas.read_csv("flight.csv")


num_features = 60  # Word vector dimensionality
min_word_count = 1 # Minimum word count
num_workers = 4  # Number of threads to run in parallel
context = 4  # Context window size
downsampling = 1e-3  # Downsample setting for frequent words
epochs = 10


def to_word2vec(x):
  return modello[x]

def vectorization(opeds_df):
    count=0
    lista1=[]
    while(count<len(opeds_df)):
        lista2=[]
        lista2.append(opeds_df['Source'][count])
        lista2.append(opeds_df['Object'][count])
        lista2.append(opeds_df['Property'][count])
        lista2.append(opeds_df['Value'][count])
        lista1.append(lista2)
        count+=1


    model = word2vec.Word2Vec(lista1, workers=num_workers, \
                              size=num_features, min_count=min_word_count, \
                              window=context, sample=downsampling)
    model.train(lista1, total_examples=len(lista1), epochs=epochs)

    model_name = "model"
    model.save(model_name)

#vectorization(opeds_df)
modello= gensim.models.Word2Vec.load('model')
datasetcsv_vec = pandas.DataFrame()

print("Sources in progress\n")
datasetcsv_vec['Source']   = datasetcsv['Source'].apply(to_word2vec)
print("Object in progress\n")
datasetcsv_vec['Object']   = datasetcsv['Object'].apply(to_word2vec)
print("Property in progress\n")
datasetcsv_vec['Property'] = datasetcsv['Property'].apply(to_word2vec)
print("Value in progress \n")
datasetcsv_vec['Value']    = datasetcsv['Value'].apply(to_word2vec)

#print(datasetcsv_vec)


entries = datasetcsv.groupby(['Object', 'Property'])

# NOTA: per tutte le coppie (Object, Property) devono esprimersi tutti
# fonti
source_number  = len(datasetcsv['Source'].unique())
entries_number = len(entries)
x_size = 3 * num_features

dataset_continues = np.zeros((entries_number, source_number), dtype=np.float32)
dataset_is_categorical = np.zeros((entries_number), dtype=np.bool)  # is the n-th I categorical? True/False
dataset_I = np.zeros((entries_number, source_number, x_size), dtype=np.float32)  # I


for i, entry_key in enumerate(entries.groups):
    print(entry_key)

    entry = entries.get_group(entry_key)

    entry['Object'] = entry['Object'].apply(to_word2vec)
    entry['Property'] = entry['Property'].apply(to_word2vec)

    # is categorical
    dataset_is_categorical[i] = np.bool(entry.iloc[0]['Categorical'] == 1)

    obj, prop = entry.iloc[0]['Object'], entry.iloc[0]['Property']
    for s in range(source_number):
        # cont values
        if not dataset_is_categorical[i]:
            try:
                dataset_continues[i, s] = entry.iloc[s]['Value']
                print(entry.iloc[s]['Value'])
                val = entry.iloc[s]['Value']
                #lastvalid=entry.iloc[s]['Value']
            except IndexError as e:
                dataset_continues[i, s] = '0.0'
                val = '0.0'

        # I
        else:
            try:
                print(entry.iloc[s]['Value'])
                val = entry.iloc[s]['Value']
            except:
                val = '-'
        val = to_word2vec(val)

        dataset_I[i, s] = np.concatenate([obj, prop, val])
    #print(dataset_I)

'''
print("I" + "\n")
print(dataset_I)
print("CATEGORICAL" + "\n")
print(dataset_is_categorical)
print("CONT_VALUES", "\n", dataset_continues)
'''


# distanza categorica fra truth_value e value, entrambi vettori
#
# ritorna 1 se sono diversi, 0 altrimenti
def d_cate(truth_value, value):
    equals_elementwise = tf.equal(truth_value, value)
    equals = tf.reduce_all(equals_elementwise)
    return 1 - tf.cast(equals, dtype=tf.float32)


# distanza continua fra truth_value e value
def d_con(truth_value, value, values):
    abs_diff = tf.abs(truth_value - value)

    mean = tf.reduce_mean(values)
    den = tf.sqrt(tf.reduce_sum((values - mean) ** 2))

    # if den == 0 and abs_diff == 0, then we have 0/0
    # and tensorflow returns nan. We know that 0/0 means
    # that the distance is 0
    d_zero = tf.logical_and(tf.equal(abs_diff, 0.0), tf.equal(den, 0.0))

    d = tf.cond(d_zero, lambda: tf.constant(0.0), lambda: abs_diff / den)
    return d


def get_majority(values):
    values_tensor = tf.stack(values)
    counts = []

    for value in values:
        one_if_equal = lambda v: tf.cast(tf.equal(value, v), dtype=tf.float32)
        one_where_equal = tf.map_fn(one_if_equal, values_tensor)
        count = tf.reduce_sum(one_where_equal)

        counts.append(count)

    index_max = tf.argmax(tf.stack(counts))

    return values_tensor[index_max]


def weighted_median(values, weights):
    # We have to find Wi in W satisfy:
    #     - the sum of the elements on its  left are <  sum(weight)/2
    #     - the sum of the elements on its right are <= sum(weight)/2
    # then return values[i], working with a sorted weights based on values

    half = tf.reduce_sum(weights) / 2.0

    sorted_values, sorted_index = tf.nn.top_k(values, values.shape[-1], sorted=False)
    sorted_weights = tf.gather(weights, sorted_index)

    satisfy_at_index = []

    for i in range(values.shape[-1]):
        left_sum = tf.reduce_sum(sorted_weights[0:i])
        right_sum = tf.reduce_sum(sorted_weights[i + 1:])

        satisfy = tf.logical_and(tf.less(left_sum, half),
                                 tf.less_equal(right_sum, half))

        satisfy_at_index.append(tf.cast(satisfy, dtype=tf.int32))

    where_satisfy = tf.argmax(satisfy_at_index)

    return sorted_values[where_satisfy]


def loss_cate(R, I):
    xes = tf.unstack(I)

    values = []
    for x in xes:
        obj, property, value = tf.split(x, 3)
        values.append(value)

    # the truth is is the majority
    truth_value = get_majority(values)

    l = 0.0
    for s, value in enumerate(values):
        l += R[s] * d_cate(truth_value, value)

    return l


def loss_cont(R, cont_values):
    truth_value = weighted_median(cont_values, R)

    l = 0.0

    values = tf.unstack(cont_values)
    for s, value in enumerate(values):
        l += R[s] * d_con(truth_value, value, cont_values)

    return l


def loss(i_batch, R, continues_placeholder, is_categorical_batch):
    l = 0.0

    for i, is_categorical in enumerate(tf.unstack(is_categorical_batch, axis=0)):
        l += tf.cond(is_categorical,
                     lambda: loss_cate(R[i], i_batch[i]),
                     lambda: loss_cont(R[i], continues_batch[i]))
    return l

def FFMN(K, statement_size):
  with tf.variable_scope("FFMN", reuse=tf.AUTO_REUSE):
    I = tf.placeholder(tf.float32, shape=(None,
                                        k,
                                        statement_size))

    M = tf.get_variable("M", [k, statement_size], dtype=tf.float32, initializer=tf.truncated_normal_initializer(stddev=1.0))
    O = tf.reduce_sum(tf.multiply(I, M), axis=2)
    R = tf.nn.softmax(O, axis=1)
  return I, R


k = source_number
batch_size = entries_number
continues_batch = tf.placeholder(tf.float32, shape=(batch_size, k))
is_categorical_batch = tf.placeholder(tf.bool, shape=(batch_size))

input_batch, R = FFMN(k, 3*num_features)
l = loss(input_batch, R, continues_batch, is_categorical_batch)


ADA = tf.train.AdamOptimizer()

with tf.variable_scope("opt", reuse=tf.AUTO_REUSE):
  minimization_op = ADA.minimize(l)


with tf.Session() as s:
  s.run(tf.global_variables_initializer())

  for i in range(1000):

    _, lo = s.run([minimization_op, l], feed_dict={
        input_batch: dataset_I,
        continues_batch: dataset_continues,
        is_categorical_batch: dataset_is_categorical
      })

    if i % 100 == 0:
        print(lo)

  print("")

  np.set_printoptions(suppress=True)

  print(s.run([R], feed_dict={
      input_batch: dataset_I
  }))



