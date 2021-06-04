import pickle
from sklearn.model_selection import train_test_split

from datareader.datareader import DataReader
from textembedder.textembedder import TextEmbedder
from bot.bot import Bot

if __name__ == "__main__":
    datareader = DataReader('../../data/AIML_QAdataset.csv')
    # print(datareader.df.info())
    # print(datareader.df.head())


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
    print(sorted_df['Topic'].value_counts())

    train, test = train_test_split(sorted_df, stratify=sorted_df['Topic'])
    print("##################################")
    print("Train set")
    print(train.head())
    print(train.info())
    print(train['Topic'].value_counts())

    print("##################################")
    print("Test set")
    print(test.head())
    print(test.info())
    print(test['Topic'].value_counts())