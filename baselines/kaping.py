import argparse
import sys
import os
import csv
from collections import Counter

from ruamel.yaml import YAML
from sentence_transformers import SentenceTransformer, util
from refined.inference.processor import Refined

from baselines.utils.wikidata import Wikidata
from baselines.prompt import Prompt
from baselines.llm import LLM
from baselines.chat import Chat
from baselines.utils.dataloader import dataloader


class Kaping:
    def __init__(self):
        self.entity_extractor = EntityExtractor()
        self.wikidata = Wikidata()
        self.knowledge_retriever = KnowledgeRetriever()

        self.prompt = Prompt("../prompts/kaping.yaml") # TODO: path 

    def __call__(self, question):
        # extract question entities
        question_entities = self.entity_extractor(question)
        print(question_entities)

        if not question_entities:
            prompt_params = {"FACTS": [], "QUESTION": question}
            return self.prompt(prompt_params)

        # retrieve wikidata triples
        wikidata_triples = []
        for entity in question_entities:
            entity_triples = self.wikidata.from_id(entity)
            if entity_triples:
                wikidata_triples += self.wikidata.from_id(entity)

        verbalized_wikidata_triples = self.wikidata.verbalize_triples(wikidata_triples)

        # get top wikidata triples
        knowledge = self.knowledge_retriever(question, verbalized_wikidata_triples)

        prompt_params = {"FACTS": knowledge, "QUESTION": question}
        return self.prompt(prompt_params)

class EntityExtractor:
    def __init__(self, model_dir):
        self.refined = Refined.from_pretrained(
            model_name="wikipedia_model",
            entity_set="wikidata",
            data_dir=f"{model_dir}/refined",
        )

    def __call__(self, s):
        spans = self.refined.process_text(s)
        return [span.predicted_entity.wikidata_entity_id for span in spans if span.predicted_entity.wikidata_entity_id is not None]

class KnowledgeRetriever:
    def __init__(self, model_dir):
        self.mpnet = SentenceTransformer(
            "sentence-transformers/all-mpnet-base-v2",
            cache_folder=f"{model_dir}/sentence_transformers",
        )

    def __call__(self, question, facts):
        question_embedding = self.encode([question])
        facts_embeddings = self.encode(facts)

        results = util.semantic_search(
            question_embedding, facts_embeddings, score_function=util.dot_score
        )[0]

        return [facts[result["corpus_id"]] for result in results]

    def encode(self, s):
        return self.mpnet.encode(s, normalize_embeddings=True, convert_to_tensor=True)



def run(dataset_f, chat_f):
    openai = LLM()
    kaping = Kaping()

    chat = Chat(chat_f)

    for id, query, answer in dataloader(dataset_f):
        prompt = kaping(query)
        
        response = openai(prompt) 

        chat.add_step(id, prompt, response)
        chat.save()




def kaping_parse_response(response):
    content = response.strip().lower()

    answer = content.split(".")[0]

    if "i don't know" in answer:
        return None
    elif "yes" in answer:
        return True
    elif "no" in answer:
        return False
    else:
        print(answer)
        return None

def eval(dataset_f, chat_f):
    result = Counter()

    with open(chat_f, "r") as f:
        chat = dict(YAML().load(f))
    
    for id, query, answer in dataloader(dataset_f):
        llm_response = chat[id][-1][-1]["assistant"]
        llm_answer = kaping_parse_response(llm_response)

        if llm_answer is None:
            result.update(["None"])
            continue

        if answer == llm_answer:
            result.update(["Correct"])
        else:
            result.update(["Incorrect"])
    
    return result




    

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('task', choices=['question-answering', 'claim-verification'])
    args = parser.parse_args()

    if args.task == "question-answering":
        dataset_f = "CR-LT-QA.json"
    else:
        dataset_f = "CR-LT-ClaimVerification.json"

    os.makedirs("baselines/chats", exist_ok=True)
    chat_f = f"baselines/chats/{args.task}-kaping.json"

    run(dataset_f, chat_f)
    result = eval(dataset_f, chat_f)

    
