import json 

def dataloader(dataset_f):
    with open(dataset_f, "r") as f:
        data = json.load(f)
    
    for d in data:
        id = d["id"]
        query = d["query"]
        answer = d["answer"]

        yield(id, query, answer)
    