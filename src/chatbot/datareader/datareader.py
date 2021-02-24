import numpy as np
import pandas as pd 
import torch

from transformers import AutoTokenizer, AutoModel
from textembedder.textembedder import TextEmbedder


class DataReader:
    def __init__(self, filepath):
        self.df = pd.read_csv(filepath)
        self.df.columns =['Pattern', 'Topic', 'That', 'Template'] 
        self.max = len(self.df.index)

    def __iter__(self):
        self.index = 0
        return self

    def __next__(self):
        if self.index <= self.max:
            self.index += 1
            series = self.df.iloc[self.index]
            return series['Pattern'], series['Template']
        else:
            raise StopIteration


if __name__ == "__main__":
    datareader = DataReader('../../data/subset_AIML_QAdataset.csv')
    # print(datareader.df.head())
    # print(datareader.df.info)

    # questions = np.array([])
    # answers = np.array([])
    questions = []
    answers = []
    try:
        for row in datareader:
            questions.append(row[0]) #= np.append(questions, row[0])
            answers.append(row[1]) #= np.append(answers, row[1])
    except:
        print("finished creating question/answer documents")