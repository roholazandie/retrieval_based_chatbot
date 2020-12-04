import pickle

from datareader.datareader import DataReader
from textembedder.textembedder import TextEmbedder
from bot.bot import Bot

if __name__ == "__main__":
    datareader = DataReader('../../data/AIML_QAdataset.csv')
    # print(datareader.df.head())
    # print(datareader.df.info)

    # questions = np.array([])
    # answers = np.array([])
    questions = []
    answers = []
    try:
        for row in datareader:
            if not isinstance(row[0], str) or not isinstance(row[1], str):
                print("row[0]: {}, {}".format(type(row[0]), row[0]))
                print("row[1]: {}, {}".format(type(row[1]), row[1]))
                exit()
            questions.append(row[0]) #= np.append(questions, row[0])
            answers.append(row[1]) #= np.append(answers, row[1])
    except Exception as e:
        if e is not "single positional indexer is out-of-bounds":
            print("finished creating question/answer documents")
            exit()

        print("Error creating file! - {}".format(e))
        

    tokenizer = "sentence-transformers/bert-base-nli-mean-tokens"
    model = "sentence-transformers/bert-base-nli-mean-tokens"

    chatbot = Bot(tokenizer, model)
    chatbot.init_embeddings(questions, answers)
    # chatbot.pickle_embeddings(questions, answers)

    # queries = ["What is your name?", "How are you today Ryan?", "You just said that.", "Can you tell me a joke?", "I love a good adventure book.", "What year is it?"]
    # print("Asking questions...")
    # for query in queries:
    #     query_embedding = chatbot.textembedder.create_sentence_embeddings(query)
    #     response_embeddings, response_indexes = chatbot.answer_query(query_embedding)
    #     print("##########")
    #     print("User: {}".format(query))
    #     print("Ryan: {}".format(answers[response_indexes[0]]))
