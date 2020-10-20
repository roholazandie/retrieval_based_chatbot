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



