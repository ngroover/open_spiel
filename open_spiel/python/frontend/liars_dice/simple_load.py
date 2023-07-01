#!/usr/bin/python3
import tensorflow as tf
import numpy as np
import pickle


#print('done fitting')
#result = model.predict(test_input)
#print(f'result {result}')
# Calling `save('my_model')` creates a SavedModel folder `my_model`.
#model.save("my_model")

f=open('input.pickle','rb')
test_input = pickle.load(f)
test_target = np.random.random((128, 1))

# It can be used to reconstruct the model identically.
reconstructed_model = tf.keras.models.load_model("my_model")
print('done loading')
result = reconstructed_model.predict(test_input)
print(f'result {result}')

# Let's check:
#np.testing.assert_allclose(
    #model.predict(test_input), reconstructed_model.predict(test_input)
#)
#
# The reconstructed model is already compiled and has retained the optimizer
# state, so training can resume:
#reconstructed_model.fit(test_input, test_target)

