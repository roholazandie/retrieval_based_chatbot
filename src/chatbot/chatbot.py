import numpy as np
import torch

from textembedder.textembedder import TextEmbedder

class ChatBot:
    def __init__(self, tokenizer_filepath, model_filepath):
        self._textembedder = TextEmbedder(tokenizer_filepath, model_filepath)
        self.init_embeddings()
        print("Finished created embeddings")

    @property
    def textembedder(self):
        return self._textembedder

    def init_embeddings(self):
        self._answer_embeddings = self._textembedder.create_sentence_embeddings(answers)
        self._question_embeddings = self._textembedder.create_sentence_embeddings(questions)

    def answer_query(self, query):
        # Get similarity of query vs precomputed question embeddings
        canidate_response_idxs = self._compute_similarity(query_embedding)

    def _compute_similarity(self, query_embedding):
        # TODO: Need to normalize the denominator
        # indexes = (query_embedding * torch.transpose(self._question_embeddings, 0, 1)) / (query_embedding * torch.transpose(self._question_embeddings, 0, 1))
        pass