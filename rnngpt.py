# -*- coding: utf-8 -*-
"""RNNGpt.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1opf20sNShsxXcwExs0eZlQEGwF7Hhuoj
"""

import numpy as np
import tensorflow as tf
from tensorflow.keras.preprocessing.text import Tokenizer
from tensorflow.keras.preprocessing.sequence import pad_sequences

# Load the text data from a file
file_path = '/content/drive/MyDrive/dataset.txt'  # Update this with the actual file path
with open(file_path, 'r') as file:
    text_data = file.readlines()

from google.colab import drive
drive.mount('/content/drive')

# Clean up the text data (removing newline characters)
text_data = [line.strip() for line in text_data if line.strip() != '']

print(text_data)  # To verify the dataset is loaded properly

# Tokenization
tokenizer = Tokenizer()
tokenizer.fit_on_texts(text_data)
total_words = len(tokenizer.word_index) + 1

# Create input sequences using the text data
input_sequences = []
for line in text_data:
    token_list = tokenizer.texts_to_sequences([line])[0]
    for i in range(1, len(token_list)):
        n_gram_sequence = token_list[:i+1]
        input_sequences.append(n_gram_sequence)

# Pad sequences to ensure they are all the same length
max_sequence_len = max([len(seq) for seq in input_sequences])
input_sequences = np.array(pad_sequences(input_sequences, maxlen=max_sequence_len, padding='pre'))

# Split the data into input (X) and output (y)
X, y = input_sequences[:,:-1], input_sequences[:,-1]
y = tf.keras.utils.to_categorical(y, num_classes=total_words)

print(f"X shape: {X.shape}, y shape: {y.shape}")

from tensorflow.keras.models import Model
from tensorflow.keras.layers import Embedding, GRU, Dense, AdditiveAttention, Input
from tensorflow.keras.optimizers import Adam

# Model parameters
embedding_dim = 128  # Higher dimension for better token representation
gru_units = 256      # More units to handle complex reasoning and longer contexts

# Input layer
inputs = Input(shape=(max_sequence_len-1,))

# Embedding layer
embedding_layer = Embedding(total_words, embedding_dim, input_length=max_sequence_len-1)(inputs)

# GRU layer (returning sequences so that we can use attention over time steps)
gru_output = GRU(gru_units, return_sequences=True)(embedding_layer)

# Attention mechanism (Additive Attention over GRU output)
attention_output = AdditiveAttention()([gru_output, gru_output])

# Flattening the attention output for final prediction
flat_output = tf.keras.layers.Flatten()(attention_output)

# Dense output layer for next-word prediction
output_layer = Dense(total_words, activation='softmax')(flat_output)

# Defining the model
model = Model(inputs=inputs, outputs=output_layer)
model.compile(loss='categorical_crossentropy', optimizer=Adam(), metrics=['accuracy'])

# Model summary
model.summary()

# Train the model
model.fit(X, y, epochs=30,batch_size=64, verbose=1)

def generate_text(seed_text, next_words, max_sequence_len):
    for _ in range(next_words):
        token_list = tokenizer.texts_to_sequences([seed_text])[0]
        token_list = pad_sequences([token_list], maxlen=max_sequence_len-1, padding='pre')
        predicted_probs = model.predict(token_list, verbose=0)
        predicted = np.argmax(predicted_probs, axis=-1)
        output_word = tokenizer.index_word.get(predicted[0], '')
        seed_text += " " + output_word
    return seed_text

# Generate text based on a seed text
seed_text = "if it rains"
generated_text = generate_text(seed_text, next_words=20, max_sequence_len=max_sequence_len)
print(generated_text)

# Save the entire model to a file
model.save("/content/drive/MyDrive/LLM/rnn_model_with_attention.h5")

# Save only the model weights
model.save_weights("/content/drive/MyDrive/LLM/rnn.weights.h5")

from tensorflow.keras.models import load_model

# Load the model
loaded_model = load_model("/content/drive/MyDrive/LLM/rnn_model_with_attention.h5")

# The model is now ready for inference

# Define the model architecture again (same as used during training)
from tensorflow.keras.models import Model
from tensorflow.keras.layers import Embedding, GRU, Dense, AdditiveAttention, Input
from tensorflow.keras.optimizers import Adam

# Model parameters
embedding_dim = 128
gru_units = 256
total_words = 10000  # Make sure to use the correct value
max_sequence_len = 50  # Same as during training

# Define the model architecture
inputs = Input(shape=(max_sequence_len-1,))
embedding_layer = Embedding(total_words, embedding_dim, input_length=max_sequence_len-1)(inputs)
gru_output = GRU(gru_units, return_sequences=True)(embedding_layer)
attention_output = AdditiveAttention()([gru_output, gru_output])
flat_output = tf.keras.layers.Flatten()(attention_output)
output_layer = Dense(total_words, activation='softmax')(flat_output)

# Rebuild the model
loaded_model = Model(inputs=inputs, outputs=output_layer)
loaded_model.compile(loss='categorical_crossentropy', optimizer=Adam(), metrics=['accuracy'])

# Load the previously saved weights
loaded_model.load_weights("/content/drive/MyDrive/LLM/rnn.weights.h5")

# The model is now ready for inference

