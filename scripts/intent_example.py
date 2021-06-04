from transformers import AutoModelWithLMHead, AutoTokenizer

tokenizer = AutoTokenizer.from_pretrained("mrm8488/t5-base-finetuned-e2m-intent")
model = AutoModelWithLMHead.from_pretrained("mrm8488/t5-base-finetuned-e2m-intent")

def get_intent(event, max_length=16):
  input_text = "%s </s>" % event
  features = tokenizer([input_text], return_tensors='pt')

  output = model.generate(input_ids=features['input_ids'], 
                          attention_mask=features['attention_mask'],
                          max_length=max_length)

  return tokenizer.decode(output[0])

event = "Who is the president of the USA?"
print(get_intent(event))