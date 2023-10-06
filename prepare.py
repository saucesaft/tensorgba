from skimage.transform import resize
from skimage.io import imread

import csv
import numpy as np

def main():
    # will search for this folders inside of the data folder
    datasets = ['peach_circuit_1', 'peach_circuit_2', 'peach_circuit_3', 'peach_circuit_4', 'park_1', 'park_2', 'cheese_1', 'cheese_2']
    
    X = np.empty(shape=(0, 66, 200, 3), dtype=np.uint8)
    Y = []

    for dataset in datasets:

        file =  open( 'data/' + dataset + '/info.csv', 'r', newline='' )
        csv_file = csv.reader(file)
        num_samples = sum(1 for row in csv_file) - 1 # dont count the header row

        print(dataset + "... ", num_samples)

        x = np.empty(shape=(num_samples, 66, 200, 3), dtype=np.uint8)
        y = []

        file.seek(0)
        for idx, row in enumerate(csv_file):
            if row[0] == 'timestamp':
                continue

            image = imread( 'data/' + dataset + '/pics/' + row[0] + '.png' )
            image = image[30:108, 30:195]
            resized_image = resize(image, (66, 200, 3))
            image_array = resized_image.reshape((66, 200, 3))
            
            x[idx-1] = image_array

            controller = [eval(i) for i in row[1:]]
            y.append(controller)

        X = np.concatenate((X, x))
        Y.extend(y)

        file.close()

    X = np.array(X)
    Y = np.array(Y)

    np.save("data/X", X)
    np.save("data/Y", Y)

    print("\ndone :)")
    print(X.shape)
    print(Y.shape)

if __name__ == '__main__':
    main()
