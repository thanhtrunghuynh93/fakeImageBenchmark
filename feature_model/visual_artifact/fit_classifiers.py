import os
import argparse
import numpy as np
import pandas as pd

from sklearn.linear_model import LogisticRegression
from sklearn.neural_network import MLPClassifier
from sklearn.externals import joblib


CLF_NAMES = ["mlp", "logreg"]
CLFS = [
    MLPClassifier(alpha=0.1, hidden_layer_sizes=(64, 64, 64), learning_rate_init=0.001, max_iter=300),
    LogisticRegression(),
]


def parse_args():
    """Parses input arguments."""
    parser = argparse.ArgumentParser()
    parser.add_argument('-f', '--features', dest='features',
                        help='Path to features saved as .npy.')
    parser.add_argument('-s', '--scores', dest='scores',
                        help='Path to scores saved as .csv.')
    parser.add_argument('-l', '--labels', dest='labels', help='Path to labels saved as .csv.')
    parser.add_argument('-o', '--output', dest='output',
                        help='Path to save classifers.',
                        default='./output')
    args = parser.parse_args()
    return args


def main(input_features, input_score, input_labels, output_path):
    """This script fits the mlp and logreg classifers to new data.

    Processes the feature vectors and scores as saved by process_data.py
    and a .csv file containing the filenames with according labels.
    The labels .csv file is expected to have a column 'Filename' and 'Label'.
    The script provides a basic implementation to fit the
    mlp and logreg classifiers to new data.

    Args:
        input_features: Path to feature vectors as saved by process_data.py.
        input_score: Path to scores as saved by process_data.py.
        input_labels: Path to .csv with 'Filename' and 'Label' column
        output_path: Directory to save classifiers.
    """
    # read input files
    scores_df = pd.read_csv(input_score, sep=',')
    labels_df = pd.read_csv(input_labels, sep=',')
    feature_vecs = np.load(input_features)

    # filter invalid samples
    valid_idxs = scores_df.Valid.values == 1
    valid_features = feature_vecs[valid_idxs]
    valid_filenames = scores_df.Filename.values[valid_idxs]

    # get labels for valid samples
    labels = []
    for filename in valid_filenames:
        labels_row = labels_df.loc[labels_df['Filename'] == filename]
        if labels_row.size == 0:
            print ("Missing label for: ", filename)
            exit(-1)
        labels.append(labels_row['Label'].values[0])

    # create save folder
    if not os.path.exists(output_path):
        os.makedirs(output_path)

    for name, clf in zip(CLF_NAMES, CLFS):
        clf.fit(valid_features, labels)
        joblib.dump(clf, os.path.join(output_path, name + '.pkl'))


if __name__ == '__main__':
    args = parse_args()
    main(args.features, args.scores, args.labels, args.output)
