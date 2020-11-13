import numpy as np
import pandas as pd 
import torch

from transformers import AutoTokenizer, AutoModel
from textembedder.textembedder import TextEmbedder


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

    tokenizer = "sentence-transformers/bert-base-nli-mean-tokens"
    model = "sentence-transformers/bert-base-nli-mean-tokens"
    embedder = TextEmbedder(tokenizer, model)

    answer_embeddings = embedder.create_sentence_embeddings(answers)
    question_embeddings = embedder.create_sentence_embeddings(questions)
    print(question_embeddings.shape)
    print(answer_embeddings.shape)
# class TextEmbedding:
#     def __init__(self, tokenizer_filepath, model_filepath):
#         #Load AutoModel from huggingface model repository/file path
#         self._tokenizer = AutoTokenizer.from_pretrained(tokenizer)
#         self._model = AutoModel.from_pretrained(model)

#     @property
#     def tokenizer(self):
#         return self._tokenizer

#     @property
#     def model(self):
#         return self._model

#     def create_sentence_embeddings(self, document):
#         #Tokenize questions
#         encoded_input = self.__create_encoding(document)

#         model_output = self.__compute_token_embedding(encoded_input)

#         #Perform pooling. In this case, mean pooling
#         return self.__mean_pooling(model_output, encoded_input['attention_mask'])


#     """Private Methods"""

#     def __create_encoding(self, document):
#         """
#         INPUT:
#             - document: an np array of sentences (str) to encode.
#         OUTPUT:
#             - encoded_input: a pytorch tensor of the encoded document.
#         """
#         return self._tokenizer(document, padding=True, truncation=True, max_length=128, return_tensors='pt')

#     def __compute_token_embedding(self, encoded_input):
#         with torch.no_grad():
#             return self._model(**encoded_input)

#     #Mean Pooling - Take attention mask into account for correct averaging
#     def __mean_pooling(self, model_output, attention_mask):
#         token_embeddings = model_output[0] #First element of model_output contains all token embeddings
#         input_mask_expanded = attention_mask.unsqueeze(-1).expand(token_embeddings.size()).float()
#         sum_embeddings = torch.sum(token_embeddings * input_mask_expanded, 1)
#         sum_mask = torch.clamp(input_mask_expanded.sum(1), min=1e-9)
#         return sum_embeddings / sum_mask


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

    tokenizer = "sentence-transformers/bert-base-nli-mean-tokens"
    model = "sentence-transformers/bert-base-nli-mean-tokens"
    embedder = TextEmbedder(tokenizer, model)

    answer_embeddings = embedder.create_sentence_embeddings(answers)
    question_embeddings = embedder.create_sentence_embeddings(questions)
    print(question_embeddings.shape)
    print(answer_embeddings.shape)