#!/usr/bin/python3
import tensorflow as tf
import numpy as np
import pickle

def get_model():
    # Create a simple model.
    inputs = tf.keras.Input(shape=(32,))
    outputs = tf.keras.layers.Dense(1)(inputs)
    model = tf.keras.Model(inputs, outputs)
    model.compile(optimizer="adam", loss="mean_squared_error")
    return model


model = get_model()

# Train the model.
test_input = np.random.random((64, 32))
print(f'test_input {test_input}')
with open('input.pickle', 'wb') as f:
    pickle.dump(test_input, f, pickle.HIGHEST_PROTOCOL)
test_target = np.random.random((64, 1))
model.fit(test_input, test_target)

print('done fitting')
result = model.predict(test_input)
print(f'result {result}')
result2 = model.predict(test_input)
print(f'result {result2}')

# Calling `save('my_model')` creates a SavedModel folder `my_model`.
model.save("my_model")
print('done saving')

# It can be used to reconstruct the model identically.
#reconstructed_model = keras.models.load_model("my_model")

# Let's check:
#np.testing.assert_allclose(
    #model.predict(test_input), reconstructed_model.predict(test_input)
#)
#
# The reconstructed model is already compiled and has retained the optimizer
# state, so training can resume:
#reconstructed_model.fit(test_input, test_target)

