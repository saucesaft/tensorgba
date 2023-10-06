import os

import numpy as np
import sklearn

from keras.models import Sequential
from keras.layers import Conv2D, Dense, Dropout, Flatten
from keras import optimizers
from keras.callbacks import ModelCheckpoint, TensorBoard
import keras.backend as K

IMG_W = 200
IMG_H = 66
IMG_D = 3

INPUT_SHAPE = (IMG_H, IMG_W, IMG_D)
OUT_SHAPE = 6

def model(keep_prob = 0.8):

    drop_out = 1 - keep_prob

    model = Sequential()

    # Input plane 3@160x240

    # Convolutional feature map 24@31x98
    model.add( Conv2D( 24, kernel_size=(5,5), strides=(2,2), activation="elu", input_shape=INPUT_SHAPE ) ) 
    
    # Convolutional feature map 36@14x47
    model.add( Conv2D( 36, kernel_size=(5,5), strides=(2,2), activation="elu" ) ) 
    
    # Convolutional feature map 48@5x22
    model.add( Conv2D( 48, kernel_size=(5,5), strides=(2,2), activation="elu" ) ) 

    # Convolutional feature map 64@1x18
    model.add( Conv2D( 64, kernel_size=(3,3), activation="elu" ) )

    # Convolutional feature map 64@3x20
    model.add( Conv2D( 64, kernel_size=(3,3), activation="elu" ) )
    model.add( Flatten() ) # Convolutional feature map 64@1x18

    # Fully-connected layer
    model.add( Dense( 1164, activation="elu" ) ) 
    model.add( Dropout( drop_out ) )

    # Fully-connected layer
    model.add( Dense( 100, activation="elu" ) )
    model.add( Dropout( drop_out ) )

    # Fully-connected layer
    model.add( Dense( 50, activation="elu" ) )
    model.add( Dropout( drop_out ) )

    # Fully-connected layer 
    model.add( Dense( 10, activation="elu") )
    model.add( Dropout( drop_out ) ) 

    # Vehicle control
    model.add( Dense( OUT_SHAPE) ) 

    return model

def euclidean_distance_loss(y_true, y_pred):
    y_true = K.cast(y_true, "float32")
    return K.sqrt(K.sum(K.square(y_pred - y_true), axis=-1))

if __name__ == '__main__':
    x_train = np.load("data/X.npy")
    y_train = np.load("data/y.npy")

    x_train, y_train = sklearn.utils.shuffle(x_train, y_train)

    print(x_train.shape[0], 'train samples')

    epochs = 70
    batch_size = 120

    m = model(0.8)

    num = 'yuv'

    dir = os.path.join("logs", "attempt_"+num)

    checkpoint = ModelCheckpoint('attempt_'+num+'.h5', monitor='val_loss', verbose=1, save_best_only=True, mode='min')

    tensorboard_callback = TensorBoard(log_dir=dir)
    callbacks_list = [checkpoint, tensorboard_callback]

    m.compile(loss='mse', optimizer=optimizers.Adam(learning_rate=0.00099537))
    m.fit(x_train, y_train, batch_size=batch_size, epochs=epochs, shuffle=True, validation_split=0.2, callbacks=callbacks_list)

