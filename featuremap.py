# plot feature map of first conv layer for given image
from keras.applications.vgg16 import preprocess_input
from keras.models import Model
from matplotlib import pyplot
from train import model

import cv2
import numpy as np

# load the model
m = model()
m.load_weights('attempt_yuv.h5')
m.summary()

# redefine model to output right after the first hidden layer
m = Model(inputs=m.inputs, outputs=m.layers[0].output)

# image = cv2.imread( 'test.png' )
image = cv2.imread('data/cheese_2/pics/1696488126_5.png')
image = cv2.cvtColor(image, cv2.COLOR_BGR2YUV)
image = image[30:108, 30:195]
image = cv2.resize(image, (200, 66), interpolation=cv2.INTER_LINEAR)
image = np.expand_dims(image, axis=0)

# get feature map for first hidden layer
feature_maps = m.predict(image)
# plot all 64 maps in an 8x8 squares
square = 4
ix = 1
for _ in range(square):
	for _ in range(square):
		# specify subplot and turn of axis
		ax = pyplot.subplot(square, square, ix)
		ax.set_xticks([])
		ax.set_yticks([])
		# plot filter channel in grayscale
		pyplot.imshow(feature_maps[0, :, :, ix-1], cmap='gray')
		ix += 1

pyplot.show()
