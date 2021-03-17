import numpy as np
import pandas as pd
import torch
from torch.utils.data.dataset import TensorDataset
from transformers import AutoTokenizer, AutoModel
from torch.utils.data import DataLoader
from tqdm import tqdm


class TextEmbedder:
    def __init__(self, tokenizer_filepath, model_filepath):
        self._tokenizer = AutoTokenizer.from_pretrained(tokenizer_filepath)
        self._model = AutoModel.from_pretrained(model_filepath)
        if torch.cuda.is_available():
            print("Cuda is available, putting the pretrained model on the GPU.")
            self._model.to('cuda')

    @property
    def tokenizer(self):
        return self._tokenizer

    @property
    def model(self):
        return self._model

    def create_sentence_embeddings(self, document):
        try:
            # Tokenize questions
            encoded_input = self._tokenizer(document, padding=True, truncation=True, max_length=128,
                                            return_tensors='pt')

            if torch.cuda.is_available():
                print("Putting encoded_input onto cuda.")
                encoded_input = encoded_input.to('cuda')

            dataloader = DataLoader(TensorDataset(encoded_input['input_ids'],
                                                  encoded_input['token_type_ids'],
                                                  encoded_input['attention_mask']),
                                    batch_size=100,
                                    shuffle=False, num_workers=0)


            all_pooled_embeddings = self._compute_token_embedding(dataloader)

            return all_pooled_embeddings
            # print("Model output - {}".format(type(model_output)))
            # print("Model output 1- {}".format(type(model_output[0])))
            # print("Model output 2 - {}".format(type(model_output[1])))

            # if torch.cuda.is_available():
            #     # encoded_input = encoded_input.to('cuda')
            #     print("Cuda available")
            #     model_output[0] = model_output[0].to('cuda')
            #     model_output[1] = model_output[1].to('cuda')

            # Perform pooling. In this case, mean pooling
            #return self.__mean_pooling(model_output, encoded_input['attention_mask'])
        except Exception as e:
            print("Error creating sentence embeddings - {}".format(e))
            raise Exception

    def _compute_token_embedding(self, dataloader):
        all_pooled_embeddings = []
        with torch.no_grad():
            for i, data in tqdm(enumerate(dataloader)):
                embedded_batch = self._model(input_ids=data[0], token_type_ids=data[1], attention_mask=data[2])
                all_pooled_embeddings.append(embedded_batch['pooler_output'])

        all_pooled_embeddings = torch.cat(all_pooled_embeddings, dim=0)
        return all_pooled_embeddings

    # Mean Pooling - Take attention mask into account for correct averaging
    def _mean_pooling(self, model_output, attention_mask):
        token_embeddings = model_output[0]  # First element of model_output contains all token embeddings
        input_mask_expanded = attention_mask.unsqueeze(-1).expand(token_embeddings.size()).float()
        sum_embeddings = torch.sum(token_embeddings * input_mask_expanded, 1)
        sum_mask = torch.clamp(input_mask_expanded.sum(1), min=1e-9)
        return sum_embeddings / sum_mask
