"""
Voice to text to poem to speech
Credits: Michel, Lauren, Thomas
"""
import os
import numpy as np

import re
from textblob import TextBlob
import random
from BitLit_model_param import (
    parameters_rhymes,
    parameters_poems,
    char2idx_poems,
    units_poems,
    gru_weights_poems,
    fc_weights_poems,
    embedding_weights_poems,
    embedding_weights_rhymes,
    word2idx_rhymes,
    fc_weights_rhymes,
    gru_weights_rhymes,
    units_rhymes,
    idx2word_rhymes,
    idx2char_poems,
    vocab_size_poems,
    vocab_size_rhymes,
    units_poems,
    units_rhymes,
    embedding_dim_poems,
    embedding_dim_rhymes,
    BATCH_SIZE_poems,
    BATCH_SIZE_rhymes
)

# To try without cuda
os.environ["CUDA_VISIBLE_DEVICES"] = ""
import tensorflow as tf
tf.enable_eager_execution()
from tensorflow.keras.layers import Embedding, GRU, Dense

# Architechture of the GRU


class Model(tf.keras.Model):
    def __init__(self, vocab_size, embedding_dim, units, batch_size):
        super(Model, self).__init__()
        self.units = units
        self.batch_sz = batch_size
        self.embedding = Embedding(vocab_size, embedding_dim)
        self.gru = GRU(
            self.units,
            return_sequences=True,
            return_state=True,
            recurrent_activation="sigmoid",
            recurrent_initializer="glorot_uniform",
        )
        self.fc = Dense(vocab_size)

    def call(self, x, hidden):
        x = self.embedding(x)
        output, states = self.gru(x, initial_state=hidden)
        output = tf.reshape(output, (-1, output.shape[2]))
        x = self.fc(output)
        return x, states


# Creation of the poem models and rhymes model
model_poems = Model(vocab_size_poems, embedding_dim_poems, units_poems, BATCH_SIZE_poems)
model_rhymes = Model(vocab_size_rhymes, embedding_dim_rhymes, units_rhymes, BATCH_SIZE_rhymes)



# Set the weights for the poems model
num_generate = 1
start_string = "child"[::-1]
input_eval = [char2idx_poems[s] for s in start_string]
input_eval = tf.expand_dims(input_eval, 0)
hidden = [tf.zeros((1, units_poems))]
predictions, hidden = model_poems(input_eval, hidden)

model_poems.embedding.set_weights(np.asarray(embedding_weights_poems))
model_poems.gru.set_weights(gru_weights_poems)
model_poems.fc.set_weights(fc_weights_poems)


# Set the weights for the rhymes model
num_generate = 1  # number of characters to generate
start_string = ["fell"]  # beginning of the generated text. TODO: try start_string = ' '
input_eval = [
    word2idx_rhymes[s] for s in start_string
]  # converts start_string to numbers the model understands
input_eval = tf.expand_dims(input_eval, 0)
hidden = [tf.zeros((1, units_rhymes))]
predictions, hidden = model_rhymes(input_eval, hidden)

model_rhymes.embedding.set_weights(np.asarray(embedding_weights_rhymes))
model_rhymes.gru.set_weights(gru_weights_rhymes)
model_rhymes.fc.set_weights(fc_weights_rhymes)


def poem(USER_INPUT):
    ### ML POEM PREDICTOR

    ###########################
    #  USER INPUT a line      #
    ###########################
    USER_INPUT = USER_INPUT.lower()
    USER_INPUT = re.sub("[^a-z\n]", " ", USER_INPUT)
    text_generated = USER_INPUT[::-1]
    first_rhyme = USER_INPUT.split(" ")[-1]  # Michel's magic

    ######################
    #  RHYMES GENERATION #
    ######################
    temperature = 0.09

    num_generate = 5  # number of characters to generate
    if first_rhyme in idx2word_rhymes.values():
        start_string = [first_rhyme]
    else:
        start_string = [random.choice(list(word2idx_rhymes.keys()))]
        print("The word {} is not in our corpus of rhymes yet.".format(first_rhyme))
    input_eval = [
        word2idx_rhymes[s] for s in start_string
    ]  # converts start_string to numbers the model understands
    input_eval = tf.expand_dims(input_eval, 0)

    rhymes = []

    hidden = [tf.zeros((1, units_rhymes))]
    for i in range(num_generate):
        predictions, hidden = model_rhymes(
            input_eval, hidden
        )  # predictions holds the probabily for each character to be most adequate continuation

        predictions = (
            predictions / temperature
        )  # alters characters' probabilities to be picked (but keeps the order)
        predicted_id = tf.multinomial(tf.exp(predictions), num_samples=1)[0][
            0
        ].numpy()  # picks the next character for the generated text
        input_eval = tf.expand_dims([predicted_id], 0)
        rhymes += [idx2word_rhymes[predicted_id]]

    print("rhymes:", rhymes)

    ####################
    #  POEM GENERATION #
    ####################

    temperature = 0.8
    text_generated = USER_INPUT
    text_generated = text_generated[::-1] + "\n"
    num_generate = 150
    for rhyme in rhymes:
        start_string = text_generated + rhyme[::-1]
        input_eval = [char2idx_poems[s] for s in start_string]
        input_eval = tf.expand_dims(input_eval, 0)
        hidden = [tf.zeros((1, units_poems))]

        b = True
        c = 1
        added_text = " "
        while b == True:

            predictions, hidden = model_poems(input_eval, hidden)
            predictions = predictions / temperature
            predicted_id = tf.multinomial(tf.exp(predictions), num_samples=1)[0][
                0
            ].numpy()
            input_eval = tf.expand_dims([predicted_id], 0)
            added_text += idx2char_poems[predicted_id]
            c += 1
            if idx2char_poems[predicted_id] == "\n" or c > num_generate:
                text_generated = rhyme[::-1] + added_text + text_generated
                b = False

    text_generated = text_generated[
        ::-1
    ]  # That's the poem to return to the user in voice format

    text_generated = re.sub(" +", " ", text_generated)
    text_generated = str(TextBlob(text_generated).correct())
    return text_generated
