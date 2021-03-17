import numpy as np
import pandas as pd 
import torch
from sklearn.model_selection import train_test_split

from transformers import AutoTokenizer, AutoModel
from chatbot.textembedder.textembedder import TextEmbedder

class DataReader:
    def __init__(self, filepath):
        self.df = pd.read_csv(filepath)
        self.df.columns =['Pattern', 'Topic', 'That', 'Template']
        self.max = len(self.df.index)
        self.convert_to_str()

    def train_test_split(self):
        # Covnert values to strings
        self.df["Pattern"] = self.df["Pattern"].apply(str)
        self.df["Topic"] = self.df["Topic"].apply(str)
        self.df["That"] = self.df["That"].apply(str)
        self.df["Template"] = self.df["Template"].apply(str)

        train, test = train_test_split(self.df, stratify=self.df['Topic'])
        return train, test

    def convert_to_str(self):
        # Covnert values to strings
        self.df["Pattern"] = self.df["Pattern"].apply(str)
        self.df["Topic"] = self.df["Topic"].apply(str)
        self.df["That"] = self.df["That"].apply(str)
        self.df["Template"] = self.df["Template"].apply(str)

    def __iter__(self):
        self.index = 0
        return self

    def __next__(self):
        if self.index < self.max:
            series = self.df.iloc[self.index]
            self.index += 1
            return series['Pattern'], series['Template']
        elif self.index == self.max:
            return "End of file"
        else:
            raise StopIteration


if __name__ == "__main__":
    datareader = DataReader('data/subset_AIML_QAdataset.csv')
    datareader.convert_to_str()
    datareader.df.reset_index(drop=True, inplace=True)
    datareader.df.to_csv('data/subset_AIML_QAdataset.csv', index=False)

    # print(datareader.df.head())
    # print(datareader.df.info)

    # questions = np.array([])
    # answers = np.array([])
    
    # questions = []
    # answers = []
    # try:
    #     for row in datareader:
    #         questions.append(row[0]) #= np.append(questions, row[0])
    #         answers.append(row[1]) #= np.append(answers, row[1])
    # except:
    #     print("finished creating question/answer documents")