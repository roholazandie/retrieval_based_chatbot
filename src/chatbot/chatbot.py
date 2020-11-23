import torch
import numpy as np
# from sklearn.preprocessing import normalize
from textembedder.textembedder import TextEmbedder

class ChatBot:
    def __init__(self, tokenizer_filepath, model_filepath):
        self._textembedder = TextEmbedder(tokenizer_filepath, model_filepath)
        # self.init_embeddings()
        print("Finished created embeddings")

    @property
    def textembedder(self):
        return self._textembedder

    def init_embeddings(self, questions, answers):
        self._answer_embeddings = self._textembedder.create_sentence_embeddings(answers)
        self._question_embeddings = self._textembedder.create_sentence_embeddings(questions)

    def answer_query(self, query_embedding):
        # Get similarity of query vs precomputed question embeddings
        canidate_response_idxs = self.__compute_similarity(query_embedding)
        if canidate_response_idxs is None:
            raise Exception
        print("similarity matrix:\n{}".format(canidate_response_idxs))

        best_answer_index = np.argmax(canidate_response_idxs, axis=1)
        best_answers = self._answer_embeddings[best_answer_index]
        return best_answers

    def __compute_similarity(self, query_embedding):
        try:
            print("computing similarity of query...")
            numerator = np.dot(query_embedding, torch.transpose(self._question_embeddings, 0, 1))
            print("computed numerator...")
            denominator = np.dot(query_embedding, torch.transpose(self._question_embeddings, 0, 1))
            print("computed denominator...")
            denominator = torch.tanh(torch.from_numpy(denominator))
            print("normalized denominator...")
            return numerator / denominator
        except Exception as e:
            print("Error computing similarity - {}".format(e))