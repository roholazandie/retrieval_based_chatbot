import math
import pickle
import logging

from torch.utils.data import DataLoader
from sklearn.model_selection import train_test_split
from sentence_transformers import SentenceTransformer, LoggingHandler, losses, util, InputExample
from sentence_transformers.evaluation import EmbeddingSimilarityEvaluator

from bot.bot import Bot
from datareader.datareader import DataReader
from textembedder.textembedder import TextEmbedder

if __name__ == "__main__":
    datareader = DataReader('../../data/subset_AIML_QAdataset.csv')
    # print(datareader.df.info())
    # print(datareader.df.head())

    # Training variables
    model_save_path = '../data/model_eval'
    train_batch_size = 16
    num_epochs = 4


    sorted_df = datareader.df.reset_index()

    # Covnert values to strings
    sorted_df["Pattern"] = sorted_df["Pattern"].apply(str)
    sorted_df["Topic"] = sorted_df["Topic"].apply(str)
    sorted_df["That"] = sorted_df["That"].apply(str)
    sorted_df["Template"] = sorted_df["Template"].apply(str)
    
    # Sort by topic
    sorted_df = sorted_df.sort_values(by=['Topic'])
    
    # print(sorted_df.info())
    # print(sorted_df.head())
    # print(sorted_df['Topic'].value_counts())

    train, test = train_test_split(sorted_df, stratify=sorted_df['Topic'])
    test, val = train_test_split(test, stratify=test['Topic'])

    print("Getting the bert-base-nli-mean-tokens model.")
    model = SentenceTransformer("bert-base-nli-mean-tokens")

    print("Read AIML QA dataset")
    train_dataloader = DataLoader(train, shuffle=True, batch_size=train_batch_size)
    print("Calculate loss")
    train_loss = losses.CosineSimilarityLoss(model=model)
    print("Create evaluator")
    evaluator = EmbeddingSimilarityEvaluator.from_input_examples(val)

    # Train the model
    warmup_steps = math.ceil(len(train_dataloader) * num_epochs * 0.1) #10% of train data for warm-up
    print("training the model...")
    model.fit(train_objectives=[(train_dataloader, train_loss)],
          evaluator=evaluator,
          epochs=num_epochs,
          evaluation_steps=1000,
          warmup_steps=warmup_steps,
          output_path=model_save_path)
    print("complete")


    # Development set: Measure correlation between cosine score and gold labels
    print("evaluating trained model...")
    model = SentenceTransformer(model_save_path)
    test_evaluator = EmbeddingSimilarityEvaluator.from_input_examples(test)
    test_evaluator(model, output_path=model_save_path)
    print("complete")