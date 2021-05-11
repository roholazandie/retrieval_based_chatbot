import pickle

from chatbot.datareader.datareader import DataReader
from chatbot.textembedder.textembedder import TextEmbedder
from chatbot.bot.bot import Bot

def create_question_answer_arrs(datareader):
    questions = []
    answers = []
    try:
        for row in datareader:
            # Check for end of file
            if row == "End of file":
                return questions, answers


            # NOTE: This check is only for test enviornments to double check datasets.
            #       DO NOT use this check in a production enviornment.
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
        print("Error creating file! - {}".format(e))
        raise Exception

if __name__ == "__main__":
    datareader = DataReader('./data/AIML_QAdataset_knowledge.csv')
    print("Finished creating datareader.")
    questions, answers = create_question_answer_arrs(datareader)
    print("Finished created questions and answers.")
        
    tokenizer = "sentence-transformers/bert-base-nli-mean-tokens"
    model = "sentence-transformers/bert-base-nli-mean-tokens"

    # tokenizer = "sentence-transformers/distilbert-base-nli-stsb-mean-tokens"
    # model = "sentence-transformers/distilbert-base-nli-stsb-mean-tokens"

    chatbot = Bot(tokenizer, model)

    BATCHING = True
    if BATCHING:
        print("Loading data using batching.")
        chatbot.init_embeddings(questions, answers)

        queries = ["What is your name?", "How are you today Ryan?", "You just said that.", "Can you tell me a joke?", "I love a good adventure book.", "What year is it?", "Who is your father?", "Where are you Ryan?"]
        print("Asking questions...")
        for query in queries:
            print("##########")
            response = chatbot.answer_query(query, num_responses=1)
            print("User: {}".format(query))
            print("Ryan: {}".format(response))

        # for i, question in enumerate(questions):
        #     print("##########")
        #     response = chatbot.answer_query(question, num_responses=1)
        #     print("User: {}".format(question))
        #     print("Ryan: {}".format(response))
        #     print("Expected Ryan response: {}".format(answers[i]))

    else:
        print("Loading data using no batching.")
        chatbot.init_embeddings_no_batching(questions, answers)

        for i, question in enumerate(questions):
            print("##########")
            response = chatbot.answer_query_no_batching(question, num_responses=1)
            print("User: {}".format(question))
            print("Ryan: {}".format(response))
            print("Expected Ryan response: {}".format(answers[i]))