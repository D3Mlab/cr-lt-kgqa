import argparse
import os
import csv
import sys

from collections import defaultdict, Counter
from ruamel.yaml import YAML

from baselines.utils.prompt import Prompt
from baselines.utils.llm import LLM
from baselines.utils.chat import Chat
from baselines.utils.dataloader import dataloader


def run(dataset_f, chat_f, few_shot=False):
    openai = LLM()

    chat = Chat(chat_f)

    if few_shot:
        prompt_template = Prompt("")  # TODO: path
    else:
        prompt_template = Prompt("")

    for id, query, answer in dataloader(dataset_f):
        prompt_params = {"QUESTION": query}
        prompt = prompt_template(prompt_params, few_shot=few_shot)

        response = openai(prompt)

        chat.add_step(id, prompt, response)
        chat.save()


def cot_parse_response(response):
    response = response.strip().lower()

    sentences = response.split('.')

    if sentences[-1]:
        last = sentences[-1].strip()
    else:
        last = sentences[-2].strip()

    if "i don't know" in last:
        return None
    if "yes" in last:
        return True
    elif "no" in last:
        return False
    else:
        return None

def eval(dataset_f, chat_f):
    result = Counter()

    with open(chat_f, "r") as f:
        chat = dict(YAML().load(f))
    
    for id, query, answer in dataloader(dataset_f):
        llm_response = chat[id][-1][-1]["assistant"]
        llm_answer = cot_parse_response(llm_response)

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
    parser.add_argument("--few_shot", action="store_true")
    args = parser.parse_args()

    if args.task == "question-answering":
        dataset_f = "CR-LT-QA.json"
    else:
        dataset_f = "CR-LT-ClaimVerification.json"

    os.makedirs("baselines/chats", exist_ok=True)
    chat_f = f"baselines/chats/{args.task}-kaping.json"

    run(dataset_f, chat_f, few_shot=args.few_shot)
    result = eval(dataset_f, chat_f)