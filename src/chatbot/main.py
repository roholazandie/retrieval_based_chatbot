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
    
    embedder = TextEmbedder(tokenizer, model)
    answer_embeddings = embedder.create_sentence_embeddings(answers)
    question_embeddings = embedder.create_sentence_embeddings(questions)
    print(type(question_embeddings))
    print(type(answer_embeddings))

    # chatbot = ChatBot(tokenizer, model)

    # query = "How are you today Ryan?"

    # query_embedding = chatbot.textembedder.create_sentence_embeddings(query)

    # response = chatbot.answer_query(query_embedding)
    # print(response)