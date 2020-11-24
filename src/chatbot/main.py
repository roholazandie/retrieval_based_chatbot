import pickle

from datareader.datareader import DataReader
from textembedder.textembedder import TextEmbedder
from chatbot import ChatBot

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

    chatbot = ChatBot(tokenizer, model)
    chatbot.init_embeddings(questions, answers)
    chatbot.pickle_embeddings(questions, answers)

    queries = ["What is your name?", "How are you today Ryan?", "You just said that.", "Can you tell me a joke?", "Let's talk about television."]
    for query in queries:
        query_embedding = chatbot.textembedder.create_sentence_embeddings(query)
        response_embeddings, response_indexes = chatbot.answer_query(query_embedding)
        print("##########")
        print("User: {}".format(query))
        print("Ryan: {}".format(answers[response_indexes[0]]))
