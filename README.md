## A repository for all retrieval based chatbot models
Steps that needs to be taken for this project

First idea (this needs more revision as we do more loops over it):

1. Collect a small toy dataset of question/responses pairs.

2. Run a transformer based model on them to find their embeddings

3. Find the relevant answers for each query using a cosine similarity.

```
i = argmax Cos(Emb_question, Emp_answer) over All answers
```

### Data Reader
Implement a reader with ```__iter__``` method to get at least a pair of (question, response)



## Running the query_example script
This script reads in a CSV file containing 4 columns, pattern, topic, that, and template (derived from a dataset of AIML files). The script loads a pretrained Bert model used for sentence embedding. The model is used by creating a sentence embedding of the query and then finding the closest match in the dataset, using semantic similarity calculated my a softmax layer, and returns the matched response.

Follow these steps to run the script.
- Make sure you have a python virtual environment set up.
```
virtualenv -p python3 env
```

- Activate the environment.
```
source env/bin/activate
```

- Install requirements.
```
pip install -r requirements.txt
```

- Export src folder to PYTHONPATH or add below line to .bashrc
```
export PYTHONPATH="${PYTHONPATH}:/home/jarid/retrieval_based_chatbot/src"
```

- Run the python script.
```
python src/chatbot/query_example.py
```