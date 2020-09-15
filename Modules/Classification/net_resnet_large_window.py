from keras.models import Input, Model
from keras.layers import Conv2D
from keras.layers import MaxPooling2D
from keras.layers import Activation
from keras.layers import GlobalAveragePooling2D
from keras.layers import Dense
from keras.layers import Dropout, BatchNormalization
from keras import layers

'''
patch_shape: (height, width, channels)
start_ch: number of filters of the first convolutional layer
depth: number of convolutional layers
inc_rate: rate at which the convolutional channels will increase
activation: activation function after convolutions
nb_skipped: number of conv layers for the residual function
'''

def res_block(m, dim, nb_skipped, acti):
    m0 = Conv2D(dim, 3, padding = 'same')(m)
    m = m0
    for i in range(nb_skipped):
        m = BatchNormalization(axis = 1)(m)
        m = Activation(acti)(m)
        m = Conv2D(dim, 1, padding = 'same')(m)
    return layers.add([m0, m])

def level_block(m, dim, depth, inc_rate, nb_skipped, acti):
    if depth > 0:
        m = res_block(m, dim, nb_skipped, acti)
        m = MaxPooling2D()(m)
        m = level_block(m, int(inc_rate * dim), depth - 1, inc_rate, nb_skipped, acti)
    return m

def build_model(patch_shape, nb_classes = 17, start_ch = 16, depth = 4, inc_rate = 2, nb_skipped = 2, activation = 'relu'):
    i = Input(shape = patch_shape)
    o = level_block(i, start_ch, depth, inc_rate, nb_skipped, activation)
    o = GlobalAveragePooling2D()(o)
    o = Dense(1024, activation = activation)(o)
    o = Dense(nb_classes, activation = 'softmax')(o)
    return Model(inputs = i, outputs = o)
