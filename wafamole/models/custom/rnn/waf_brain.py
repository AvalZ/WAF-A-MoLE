"""Code taken from original repository at https://github.com/BBVA/waf-brain
"""

import time
import string
import numpy as np

X_FEATURES = 5
BATCH_SIZE = 100000
EPOCHS = 200
TRAIN_PERC = 0.7
DEV_PERC = 0.25
TEST_PERC = 0.05
VOCABULARY = string.printable + '\xa0'


def row_parse(row):
    def char_parse(char):
        return VOCABULARY.index(char)

    return [char_parse(char) for char in row]


def reduce_dimension(row, x_features):
    def create_new_row(index, char):
        past_pos = x_features - 1
        new_row = [None for i in range(x_features + 1)]

        def fill_past():
            if index > past_pos:
                for i in range(past_pos * -1, 0, 1):
                    pos = index - i
                    if pos:
                        new_row[past_pos + i] = row[index + i]
            else:
                for i in range(x_features, 0, -1):
                    if (index - i) >= 0:
                        x = (index - i) + 1
                        new_row[past_pos - x] = row[index - x]

        def fill_future():
            if (index + 1) < len(row):
                new_row[-1] = row[index + 1]

        fill_past()
        new_row[past_pos] = char
        fill_future()
        return new_row

    return [create_new_row(index, char) for index, char in enumerate(row)]


def split_row(x, y, row):

    for t in row:
        x_zeros = np.zeros((X_FEATURES, 101))
        y_zeros = np.zeros((101))

        get_index = lambda index: 100 if index is None else index

        for i in range(X_FEATURES):
            x_zeros[i][get_index(t[i])] = 1

        x.append(x_zeros)
        y_zeros[get_index(t[-1])] = 1
        y.append(y_zeros)


def to_ascii(row):
    for i, elem in enumerate(row):
        if elem == 1:
            return VOCABULARY[i]


def transform_predict(y_predict):
    index = np.argmax(y_predict)
    if index == 100:
        return None
    return VOCABULARY[index]


def build_text(predict_char, predict_texts):
    if predict_char is None:
        predict_texts.append([])
    else:
        predict_texts[-1].append(predict_char)


def feature_vector(sample):
    elems = [reduce_dimension(row_parse(sample), X_FEATURES)]
    x_demo = []
    y_demo = []
    for elem in elems:
        split_row(x_demo, y_demo, elem)
    return x_demo, y_demo


def process_payload(model, param_name, payloads, check_weights=False):
    try:
        # Snapshot for time
        before_time = time.time()
        elems = [reduce_dimension(row_parse(payloads[0]), X_FEATURES)]
        x_demo = []
        y_demo = []

        # Passing a value
        for elem in elems:
            split_row(x_demo, y_demo, elem)

        nn_score = [model.evaluate(np.array(x_demo), np.array(y_demo), verbose=0)]
        nn_score = nn_score[0][1]

        # Inference time
        diff_time = time.time() - before_time

        # ---------------------------------------------------------------------
        # Check each letter influence
        # ---------------------------------------------------------------------
        weights = []
        if check_weights:

            predict_chars = [
                transform_predict(y_predict)
                for y_predict in model.predict(np.array(x_demo))
            ]
            predict_texts = [[]]

            for predict_char in predict_chars:
                build_text(predict_char, predict_texts)

            odor = [
                [
                    payloads[0][i],
                    model.evaluate(
                        np.expand_dims(x_demo[i], axis=0),
                        np.expand_dims(y_demo[i], axis=0),
                        batch_size=BATCH_SIZE,
                        verbose=0,
                    ),
                ]
                for i in range(len(payloads[0]))
            ]
            weights = [
                {"letter": o[0], "weight": o[1][0], "szie": o[1][1]} for o in odor
            ]

        return {
            "paramName": param_name,
            "score": nn_score,
            "time": diff_time,
            "weights": weights,
        }

        # with open('outputAttacks/sqlattacksOutput_feat_5_botneck-101_demo.txt', 'a') as file:
        #     file.write('{}\t{}\t{}\t{}\n'.format(nn_score[0][1], diff_time, payloads[0], odor))
    except Exception as e:
        print(e)
        # print("Exception here")


__all__ = ("process_payload",)
