from os import listdir
import os
import time
import numpy as np
import tensorflow as tf
import pandas as pd
import logging


print("Attempting to load in training data...")
right_frames = []
left_frames = []
for f in listdir('data/'):
    df = pd.read_csv('data/'+f,header = None)
    if 'right' in f:
        right_frames.append(df)
    else:
        left_frames.append(df)
right_data = pd.concat(right_frames)
left_data = pd.concat(left_frames)
print('Found ' + str(right_data.shape[0]/200) + ' seconds of right data, ' + str(left_data.shape[0]/200) + ' seconds of left data.')

right_data['label']=0 #These labels can be changed later, just make sure they're consistent
left_data['label']=1 #Right =0,left=1

overall_data = pd.concat([right_data,left_data])
overall_data = overall_data.reset_index(drop=True)
labels = overall_data.pop('label')
labels = np.asarray(labels).astype('float32').reshape(-1,1)
dataset = tf.data.Dataset.from_tensor_slices((np.asarray(overall_data.values),labels))
dataset = dataset.shuffle(len(labels))

for feat,val in dataset.take(5):
    print(str(feat)+str(val))

#Split into training and testing
train_data = dataset.take(int(.8*len(labels)))
val_data = dataset.skip(int(.8*len(labels)))

print('Data successfully loaded')

model = tf.keras.models.Sequential([
    tf.keras.layers.Dense(128,activation='relu',input_shape=(4,1)),
    tf.keras.layers.Dropout(.2),
    tf.keras.layers.Dense(256,activation='relu'),
    tf.keras.layers.Dropout(.2),
    tf.keras.layers.Dense(1,activation='softmax')
])
model.compile(optimizer='adam',loss='binary_crossentropy',metrics=['accuracy'])
model.fit(train_data,validation_data=val_data,epochs=2)

print('Example prediction: ')
print(model.predict(np.array([-100,100,50,-10])))

print("Save model to disk? Y/N")
save_action = str(input())
if save_action.lower()=='y':
    print("Model name?")
    name = input()
    if name == '':
        name = str(time.time())
    model.save('models/saved_model-' + name + '.h5')
    print('Model saved')






# #This model architecure is taken from https://arxiv.org/pdf/1611.08024.pdf
# #I trust that they're much smarter than I am in determining architecture.
#
# #Setting up constants:
# nb_classes = 2
# Chans = ???
# Samples = ???
# dropoutRate = 0.2
# kernLength = 32
# F1 = 8 #Temporal filter count
# F2 =
# #TODO: fix model input shape
#     block1 = tf.keras.layers.Conv2D(F1, (1, kernLength), padding='same',
#                     input_shape=(1, Chans, Samples),
#                     use_bias=False)(input1)
#     block1 = tf.keras.layers.BatchNormalization(axis=1)(block1)
#     block1 = tf.keras.layers.DepthwiseConv2D((Chans, 1), use_bias=False,
#                          depth_multiplier=D,
#                          depthwise_constraint=max_norm(1.))(block1)
#     block1 = tf.keras.layers.BatchNormalization(axis=1)(block1)
#     block1 = tf.keras.layers.Activation('elu')(block1)
#     block1 = tf.keras.layers.AveragePooling2D((1, 4))(block1)
#     block1 = tf.keras.layers.dropoutType(dropoutRate)(block1)
#
#     block2 = tf.keras.layers.SeparableConv2D(F2, (1, 16),
#                          use_bias=False, padding='same')(block1)
#     block2 = tf.keras.layers.BatchNormalization(axis=1)(block2)
#     block2 = tf.keras.layers.Activation('elu')(block2)
#     block2 = tf.keras.layers.AveragePooling2D((1, 8))(block2)
#     block2 = tf.keras.layers.dropoutType(dropoutRate)(block2)
#
#     flatten = tf.keras.layers.Flatten(name='flatten')(block2)
#
#     dense = tf.keras.layers.Dense(nb_classes, name='dense',
#               kernel_constraint=max_norm(norm_rate))(flatten)
