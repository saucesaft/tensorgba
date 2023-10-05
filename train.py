import numpy as np

from keras.models import Sequential
from keras.layers import Conv2D, Dense, Dropout, Flatten
from keras import optimizers
from keras.losses import BinaryCrossentropy
from keras.callbacks import ModelCheckpoint

from livelossplot import PlotLossesKeras

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
    model.add( Conv2D( 24, kernel_size=(5,5), strides=(2,2), activation="relu", input_shape=INPUT_SHAPE ) ) 
    
    # Convolutional feature map 36@14x47
    model.add( Conv2D( 36, kernel_size=(5,5), strides=(2,2), activation="relu" ) ) 
    
    # Convolutional feature map 48@5x22
    model.add( Conv2D( 48, kernel_size=(5,5), strides=(2,2), activation="relu" ) ) 

    # Convolutional feature map 64@1x18
    model.add( Conv2D( 64, kernel_size=(3,3), activation="relu" ) )

    # Convolutional feature map 64@3x20
    model.add( Conv2D( 64, kernel_size=(3,3), activation="relu" ) )
    model.add( Flatten() ) # Convolutional feature map 64@1x18

    # Fully-connected layer
    model.add( Dense( 1164, activation="relu" ) ) 
    model.add( Dropout( drop_out ) )

    # Fully-connected layer
    model.add( Dense( 100, activation="relu" ) )
    model.add( Dropout( drop_out ) )

    # Fully-connected layer
    model.add( Dense( 50, activation="relu" ) )
    model.add( Dropout( drop_out ) )

    # Fully-connected layer 
    model.add( Dense( 10, activation="relu") )
    model.add( Dropout( drop_out ) ) 

    # Vehicle control
    model.add( Dense( OUT_SHAPE, activation="softsign") ) 

    return model

if __name__ == '__main__':
    x_train = np.load("data/X.npy")
    y_train = np.load("data/y.npy")

    print(x_train.shape[0], 'train samples')

    epochs = 100
    batch_size = 50

    m = model()

    checkpoint = ModelCheckpoint('model_weights.h5', monitor='val_loss', verbose=1, save_best_only=True, mode='min')
    callbacks_list = [checkpoint, PlotLossesKeras()]

    m.compile(loss=BinaryCrossentropy, optimizer=optimizers.legacy.Adam())
    m.fit(x_train, y_train, batch_size=batch_size, epochs=epochs, shuffle=True, validation_split=0.1, callbacks=callbacks_list)

