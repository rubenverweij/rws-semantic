"""Project to compare text requirements."""
import argparse
import os.path
import numpy as np
import pandas as pd
from sentence_transformers import SentenceTransformer


def sentence_into_embeddings(file_location: str,
                             column_name: str = "text"):
    """
    Transforms csv file into a list of texts

    Args:
        file_location: path location to file
        column_name: name of the text column

    Returns:
        List with embeddings 384 dimensional vector

    """
    if not os.path.exists(file_location):
        raise ValueError("This file does not exists, please check the path")

    # Read sentences
    sentences = pd.read_csv(file_location, sep=";")[column_name].tolist()

    # Read sentence encoder
    model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')
    embeddings = model.encode(sentences)

    return sentences, embeddings


def produce_embeddings_comparison(embeddings: np.ndarray, sentences: list):
    """
    Produce a list of embeddings and comparison

    Args:
        embeddings: numpy array with 384 values per text
        sentences: list with text sentences

    Returns:
        correlation matrix

    """
    num_compare = 2
    corr = np.inner(embeddings, embeddings)
    idx = np.argpartition(corr, -1)[:, :-num_compare - 1:-1]  # topM_ind
    out = corr[np.arange(corr.shape[0])[:, None], idx]
    return corr


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        prog='RWS semantic similarity analysis',
        description='Convert strings to embeddings')

    parser.add_argument('-f', metavar='file',
                        type=str, help='Path to the file location with texts',
                        required=True)

    args = parser.parse_args()
    list_with_sentences, embedding_vector = sentence_into_embeddings(file_location=args.f)
    produce_embeddings_comparison(embeddings=embedding_vector)
