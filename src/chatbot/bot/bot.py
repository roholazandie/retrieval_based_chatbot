import torch
import pickle
import numpy as np
import torch.nn as nn

from chatbot.textembedder.textembedder import TextEmbedder

class Bot:
    def __init__(self, tokenizer_filepath, model_filepath):
        self._textembedder = TextEmbedder(tokenizer_filepath, model_filepath)
        print("Finished creating model and tokenizer.")

    @property
    def textembedder(self):
        return self._textembedder

    def init_embeddings(self, questions, answers):
        try:
            self._answer_arrs = answers
            self._question_arrs = questions

            # self._answer_embeddings = self._textembedder.create_sentence_embeddings(answers)
            # self._question_embeddings = self._textembedder.create_sentence_embeddings(questions)

            answer_embeddings = self._textembedder.create_sentence_embeddings(answers)
            question_embeddings = self._textembedder.create_sentence_embeddings(questions)
            torch.save(answer_embeddings, 'models/answer_embeddings.pt')
            torch.save(question_embeddings, 'models/question_embeddings.pt')

            print("Finished created embeddings.")
        except Exception as e:
            print("Error initializing question and answer embeddings - {}".format(e))
            print("questions input: {}".format(type(questions)))
            print("answers input: {}".format(type(answers)))
            raise Exception

    def answer_query(self, query, num_responses=1):
        try:
            query_embedding = self.textembedder.create_sentence_embeddings(query)
            response_embeddings, response_indexes = self.find_embeddings(query_embedding, "softmax")
            print("response_embeddings: {}".format(response_embeddings))
            if num_responses <= 1:
                return self._answer_arrs[response_indexes[0]]
            else:
                return self.get_top_n_answers()

        except Exception as e:
            print("Error getting answer query - {}".format(e))

    def get_top_n_answers(self, n, answer_arrs, response_indexes):
        best_answers = []
        for x in range(0,n):
            best_answers.append(answer_arrs[response_indexes[x]])

        return best_answers


    def find_embeddings(self, query_embedding, method="cosine"):
        # Get similarity of query vs precomputed question embeddings
        if method is "cosine":
            print("using cosine similarity")
            canidate_response_idxs = self._compute_cosine_similarity(query_embedding) 
        elif method is "softmax":
            print("using softmax")
            canidate_response_idxs = self._compute_indicies_softmax(query_embedding) 
        
        if canidate_response_idxs is None:
            raise Exception

        try:
            best_answer_index = np.argmax(canidate_response_idxs.cpu(), axis=1)
            answer_embeddings = torch.load('models/answer_embeddings.pt')
            best_answers = answer_embeddings[best_answer_index]
        except Exception as e:
            print("Error finding embeddings - {}".format(e))
            raise Exception

        return best_answers, best_answer_index


    """Private Methods"""
    def _compute_cosine_similarity(self, query_embedding):
        try:
            print("\tcomputing similarity of query...")
            
            # numerator = torch.matmul(query_embedding, torch.transpose(self._question_embeddings, 0, 1))
            # print("\tcomputed numerator...")
            
            # denominator = torch.matmul(query_embedding, torch.transpose(self._question_embeddings, 0, 1))
            # print("\tcomputed denominator...")

            question_embeddings = torch.load('models/question_embeddings.pt')
            numerator = torch.matmul(query_embedding, torch.transpose(question_embeddings, 0, 1))
            print("\tcomputed numerator...")
            
            denominator = torch.matmul(query_embedding, torch.transpose(question_embeddings, 0, 1))
            print("\tcomputed denominator...")
            
            denominator = torch.tanh(denominator)
            print("\tnormalized denominator...")
            return numerator / denominator
        except Exception as e:
            print("Error computing similarity - {}".format(e))
            raise Exception

    def _compute_indicies_softmax(self, query_embedding):
        try:
            # input_tensor = torch.matmul(query_embedding, torch.transpose(self._question_embeddings, 0, 1))
            # # TODO: add check for if it should be on cuda or cpu
            question_embeddings = torch.load('models/question_embeddings.pt')
            input_tensor = torch.matmul(query_embedding, torch.transpose(question_embeddings, 0, 1))
            
            canidate_response_idxs = nn.Softmax(input_tensor)
            # print("tensor went through softmax layer.")
            return input_tensor
        except Exception as e:
            print("Error computing indicies via softmax - {}".format(e))
            raise Exception