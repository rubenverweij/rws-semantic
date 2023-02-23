"""Project to compare text requirements."""
import argparse
import datetime
import os.path

import numpy as np
import pandas as pd
from sentence_transformers import SentenceTransformer


def clean_input_file(file_location: str):
    """
    Clean the input file if necessary

    Args:
        file_location:

    Returns:
        pandas dataframe with multiple columns and texts

    """
    dataframe = pd.read_excel(file_location)
    return dataframe


def sentence_into_embeddings(sentences: list):
    """
    Transforms csv file into a list of texts

    Args:
        sentences
            list with str sentences

    Returns:
        embeddings: np.ndarray with 384 values per text

    """

    # Read sentence encoder
    model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')
    embeddings = model.encode(sentences)

    return embeddings


def produce_embeddings_comparison(dataframe: pd.DataFrame,
                                  column_name="Eistekst",
                                  top: int = 5):
    """
    Produce a list of embeddings and comparison

    Args:
        dataframe: pd.DataFrame with text sentences
        top: int with number compare top n requirements
        column_name: string with name of the column containing the text

    Returns:
        pd.Dataframe result_table, pd.Dataframe correlation matrix

    """
    # Create embeddings and inner product for euclidian distance
    embeddings = sentence_into_embeddings(sentences=dataframe[column_name])
    corr = np.inner(embeddings, embeddings)

    # create a big comparison matrix
    comparison_matrix = pd.DataFrame(corr)
    comparison_matrix.columns = dataframe["ID"]
    comparison_matrix.insert(loc=0, column='Eistekst', value=dataframe["Eistekst"])
    comparison_matrix.insert(loc=1, column='ID', value=dataframe["ID"])
    comparison_matrix = comparison_matrix.round(2)

    # sort scores from high to low
    scores = -np.sort(-corr)[:, 1:top+1]
    indices = np.argsort(-corr)[:, 1:top+1]

    # get the number of the requirement
    requirement_index = dataframe.ID
    list_most_similar = []

    for index in indices:
        list_most_similar.append([requirement_index[i] for i in index])

    final_result = pd.concat(
        [pd.DataFrame(scores).assign(ID=dataframe["ID"]).melt(value_name="Score", id_vars="ID", var_name="Volgorde"),
         pd.DataFrame(list_most_similar).assign(ID=dataframe["ID"]).melt(value_name="Vergelijking",
                                                                         id_vars="ID").drop(
             ["variable", "ID"], axis=1)], axis=1)
    final_result = final_result.merge(dataframe)
    final_result = final_result[['ID', 'Eissoort', 'Bron ID', 'Eistitel', 'Eistekst', 'Volgorde', 'Score', 'Vergelijking']]
    final_result.Volgorde = final_result.Volgorde + 1
    final_result = final_result.round(2)
    return final_result, comparison_matrix


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        prog='RWS semantic similarity analysis',
        description='Convert strings to embeddings')

    parser.add_argument('-file', metavar='file',
                        type=str, help='Path to the file location with texts',
                        required=True)

    parser.add_argument('-top', metavar='top',
                        type=int, help='Top n most similar requirements',
                        required=True)

    args = parser.parse_args()

    # clean data and get dataframe with results
    df = clean_input_file(args.file)
    result, comparison = produce_embeddings_comparison(dataframe=df, top=args.top)

    # get date stamp and write result
    date_stamp = datetime.datetime.now().strftime("%Y_%m_%d")
    result_dir = f"results/{date_stamp}"
    if not os.path.exists(result_dir):
        os.mkdir(result_dir)

    file_name = f"{result_dir}/{date_stamp}_result_similarity_analysis.xlsx"
    file_name_comparison = f"{result_dir}/{date_stamp}_result_comparison_matrix.xlsx"

    comparison.to_excel(file_name_comparison, index=False)
    result.to_excel(file_name, index=False)
