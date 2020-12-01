
import numpy as np
import pandas as pd 
import torch
from transformers import AutoTokenizer, AutoModel


class TextEmbedder:
    def __init__(self, tokenizer_filepath, model_filepath):
        self._tokenizer = AutoTokenizer.from_pretrained(tokenizer_filepath)
        self._model = AutoModel.from_pretrained(model_filepath)

    @property
    def tokenizer(self):
        return self._tokenizer

    @property
    def model(self):
        return self._model

    def create_sentence_embeddings(self, document):
        try:
            #Tokenize questions
            encoded_input = self.__create_encoding(document)
            # print("Created econding - {}".format(encoded_input))
            model_output = self.__compute_token_embedding(encoded_input)

            #Perform pooling. In this case, mean pooling
            return self.__mean_pooling(model_output, encoded_input['attention_mask'])
        except Exception as e:
            print("Error creating sentence embeddings - {}".format(e))

    """Private Methods"""
    def __create_encoding(self, document):
        """
        INPUT:
            - document: an np array of sentences (str) to encode.
        OUTPUT:
            - encoded_input: a pytorch tensor of the encoded document.
        """
        return self._tokenizer(document, padding=True, truncation=True, max_length=128, return_tensors='pt')

    def __compute_token_embedding(self, encoded_input):
        with torch.no_grad():
            return self._model(**encoded_input)

    #Mean Pooling - Take attention mask into account for correct averaging
    def __mean_pooling(self, model_output, attention_mask):
        token_embeddings = model_output[0] #First element of model_output contains all token embeddings
        input_mask_expanded = attention_mask.unsqueeze(-1).expand(token_embeddings.size()).float()
        sum_embeddings = torch.sum(token_embeddings * input_mask_expanded, 1)
        sum_mask = torch.clamp(input_mask_expanded.sum(1), min=1e-9)
        return sum_embeddings / sum_mask