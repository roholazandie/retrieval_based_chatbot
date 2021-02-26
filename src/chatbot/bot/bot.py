import torch
import pickle
import numpy as np
import torch.nn as nn

from textembedder.textembedder import TextEmbedder

class Bot:
    def __init__(self, tokenizer_filepath, model_filepath):
        self._textembedder = TextEmbedder(tokenizer_filepath, model_filepath)
        # self.init_embeddings()
        print("Finished creating model and tokenizer.")

    @property
    def textembedder(self):
        return self._textembedder

    def init_embeddings(self, questions, answers):
        try:
            self._answer_arrs = answers
            self._question_arrs = questions
            self._answer_embeddings = self._textembedder.create_sentence_embeddings(answers)
            self._question_embeddings = self._textembedder.create_sentence_embeddings(questions)
            print("Finished created embeddings.")
        except Exception as e:
            print("Error initializing question and answer embeddings - {}".format(e))
            print("questions input: {}".format(type(questions)))
            print("answers input: {}".format(type(answers)))
            raise Exception

    def answer_query(self, query):
        try:
            query_embedding = self.textembedder.create_sentence_embeddings(query)
            response_embeddings, response_indexes = self.find_embeddings(query_embedding, "softmax")
            return self._answer_arrs[response_indexes[0]]
        except Exception as e:
            print("Error getting answer query - {}".format(e))

    def pickle_embeddings(self, question_sentences, answer_sentences, filepath="../pickled_embeddings/qa_sentences_embeddings.pkl"):
        try:
            print("Storing file on disc...")
            with open(filepath, "wb") as fOut:
                pickle.dump({'question_sentences': question_sentences, 
                        'answer_sentences': answer_sentences, 
                        'question_embeddings': self._question_embeddings, 
                        'answer_embeddings': self._answer_embeddings}, fOut)
            print("Completed pickling embeddings to disk...")
        except Exception as e:
            print("Error pickling embeddings! - {}".format(e))

    def find_embeddings(self, query_embedding, method="cosine"):
        # Get similarity of query vs precomputed question embeddings
        if method is "cosine":
            print("using cosine similarity")
            canidate_response_idxs = self.__compute_cosine_similarity(query_embedding) 
        elif method is "softmax":
            print("using softmax")
            canidate_response_idxs = self.__compute_indicies_softmax(query_embedding) 
        
        if canidate_response_idxs is None:
            raise Exception

        best_answer_index = np.argmax(canidate_response_idxs, axis=1)
        best_answers = self._answer_embeddings[best_answer_index]
        return best_answers, best_answer_index


    """Private Methods"""
    def __compute_cosine_similarity(self, query_embedding):
        try:
            print("\tcomputing similarity of query...")
            
            numerator = torch.matmul(query_embedding, torch.transpose(self._question_embeddings, 0, 1))
            print("\tcomputed numerator...")
            
            denominator = torch.matmul(query_embedding, torch.transpose(self._question_embeddings, 0, 1))
            print("\tcomputed denominator...")
            
            denominator = torch.tanh(denominator)
            print("\tnormalized denominator...")
            return numerator / denominator
        except Exception as e:
            print("Error computing similarity - {}".format(e))
            raise Exception

    def __compute_indicies_softmax(self, query_embedding):
        try:
            input_tensor = torch.matmul(query_embedding, torch.transpose(self._question_embeddings, 0, 1))
            print("input_tensor: {}".format(type(input_tensor)))
            canidate_response_idxs = nn.Softmax(input_tensor)
            print("tensor went through softmax layer.")
            return input_tensor
        except Exception as e:
            print("Error computing indicies via softmax - {}".format(e))
            raise Exception