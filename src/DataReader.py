import numpy as np
import pandas as pd 
import torch
from transformers import AutoTokenizer, AutoModel


class DataReader:
    def __init__(self, filepath):
        self.df = pd.read_csv(filepath)
        self.df.columns =['Pattern', 'Topic', 'Topic', 'Template'] 
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



#Mean Pooling - Take attention mask into account for correct averaging
def mean_pooling(model_output, attention_mask):
    token_embeddings = model_output[0] #First element of model_output contains all token embeddings
    input_mask_expanded = attention_mask.unsqueeze(-1).expand(token_embeddings.size()).float()
    sum_embeddings = torch.sum(token_embeddings * input_mask_expanded, 1)
    sum_mask = torch.clamp(input_mask_expanded.sum(1), min=1e-9)
    return sum_embeddings / sum_mask



if __name__ == "__main__":
    datareader = DataReader('../data/subset_AIML_QAdataset.csv')
    # print(datareader.df.head())
    # print(datareader.df.info)

    questions = []
    answers = []
    try:
        for row in datareader:
            questions.append(row[0])
            answers.append(row[1])
    except:
        print("finished creating question/answer documents")


    #Load AutoModel from huggingface model repository
    tokenizer = AutoTokenizer.from_pretrained("sentence-transformers/bert-base-nli-mean-tokens")
    model = AutoModel.from_pretrained("sentence-transformers/bert-base-nli-mean-tokens")

    #Tokenize questions
    encoded_input = tokenizer(questions, padding=True, truncation=True, max_length=128, return_tensors='pt')

    #Compute token embeddings
    with torch.no_grad():
        model_output = model(**encoded_input)

    #Perform pooling. In this case, mean pooling
    question_embeddings = mean_pooling(model_output, encoded_input['attention_mask'])
    print(question_embeddings)