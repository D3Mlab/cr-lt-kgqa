import os
from collections import defaultdict

from ruamel.yaml import YAML
from ruamel.yaml.scalarstring import LiteralScalarString


class Chat:
    def __init__(self, save_file):
        self.save_file = save_file

        self.yaml = YAML()

        if os.path.isfile(save_file):
            with open(save_file, 'r') as f:
                self.chats = defaultdict(list, YAML().load(f))
        else:
            self.chats = defaultdict(list)

    def add_step(self, id, prompt, response):
        messages = prompt + [response]
        for i in range(len(messages)):
            message = dict(messages[i])
            message = {message["role"]: LiteralScalarString(message["content"])}
            messages[i] = message

        self.chats[id].append(messages)

    def save(self):
        with open(self.save_file, "w") as f:
            self.yaml.dump(dict(self.chats), f)

