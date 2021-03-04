import pickle

from chatbot.datareader.datareader import DataReader
from chatbot.textembedder.textembedder import TextEmbedder
from chatbot.bot.bot import Bot

def create_question_answer_arrs(datareader):
    #TODO Jarid, this method needs refactoring, don't use exit()
    questions = []
    answers = []
    try:
        for row in datareader:
            # This checks to make sure only strings will be added to our documents.
            # If we find that one of the rows does not contain a string we exit.
            # (Helps for finding bad data)
            if not isinstance(row[0], str) or not isinstance(row[1], str):
                print("row[0]: {}, {}".format(type(row[0]), row[0]))
                print("row[1]: {}, {}".format(type(row[1]), row[1]))
                exit()

            questions.append(row[0]) #= np.append(questions, row[0])
            answers.append(row[1]) #= np.append(answers, row[1])
    except Exception as e:
        # TODO Jarid: you should always raise the exception, this is not safe
        if e is not "single positional indexer is out-of-bounds":
            print("Finished creating question/answer documents")
            # exit()
        else: 
            print("Error creating file! - {}".format(e))

    return questions, answers

if __name__ == "__main__":
    datareader = DataReader('../../data/AIML_QAdataset.csv')
    questions, answers = create_question_answer_arrs(datareader)
        
    tokenizer = "sentence-transformers/bert-base-nli-mean-tokens"
    model = "sentence-transformers/bert-base-nli-mean-tokens"

    # tokenizer = "sentence-transformers/distilbert-base-nli-stsb-mean-tokens"
    # model = "sentence-transformers/distilbert-base-nli-stsb-mean-tokens"

    chatbot = Bot(tokenizer, model)
    chatbot.init_embeddings(questions, answers)
    # chatbot.pickle_embeddings(questions, answers)

    queries = ["What is your name?", "How are you today Ryan?", "You just said that.", "Can you tell me a joke?", "I love a good adventure book.", "What year is it?"]
    print("Asking questions...")
    for query in queries:
        print("##########")
        response = chatbot.answer_query(query)
        print("User: {}".format(query))
        print("Ryan: {}".format(response))
