# plot feature map of first conv layer for given image
from keras.applications.vgg16 import preprocess_input
from keras.models import Model
from matplotlib import pyplot
from numpy import expand_dims
from train import model

from skimage.io import imread
from skimage.transform import resize

# load the model
m = model()
m.load_weights('attempt_repo.h5')
m.summary()

# redefine model to output right after the first hidden layer
m = Model(inputs=m.inputs, outputs=m.layers[0].output)

image = imread( 'test2.png' )
# image = imread('data/cheese_2/pics/1696488126_5.png')

image = image[30:108, 30:195]
image_array = resize(image, (66, 200, 3))

image_array = expand_dims(image_array, axis=0)
image_array = preprocess_input(image_array)

# get feature map for first hidden layer
feature_maps = m.predict(image_array)
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
