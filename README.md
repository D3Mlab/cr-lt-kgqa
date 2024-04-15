# cr-lt-kgqa
CR-LT KGQA Dataset Repository
# Introduction
This repository contains the CR-LT-KGQA Dataset and implementations of the baselines. CR-LT-KGQA is the first Knowledge Graph Query Answering dataset with Natural Language queries targeted on long-tail Wikidata entities, answering which requires commonsense reasoning and is submitted to SIGIR'24.
## CR-LT-KGQA: A Knowledge Graph Question Answering Dataset Requiring Commonsense Reasoning and Long-Tail Knowledge ## 
The dataset contains two subsets targetting two different tasks: (i) [**Question Answering** subset](https://github.com/D3Mlab/cr-lt-kgqa/blob/main/CR-LT-QA.json) containing 200 questions based on [StrategyQA dataset](https://github.com/eladsegal/strategyqa/tree/main) and (ii) [**Claim Verification** subset](https://github.com/D3Mlab/cr-lt-kgqa/blob/main/CR-LT-ClaimVerification.json) containing 150 claims based on [Creak dataset](https://github.com/yasumasaonoe/creak).


## Data Format

The format of the dataset is in JSON, where each entry contains a query (a question or a claim), the answer, anchor KG entities mentioned in the query and their respective Wikidata QID, an inference rule, relevant KG triples, reasoning steps and the relevant KG triples to each step, and finally the set of reasoning skills and strategies required to answer the query.
An exemplar entry of the dataset:
```json
{
    "id": "S37",
    "query": "Could you travel from Gujan to Aousserd only by car?",
    "answer": false,
    "KG Entities": {
      "Gujan": "Q5103164",
      "Aousserd": "Q2026640"
    },
    "Inference Rule": "Aousserd must be reachable from Gujan by roads to be able to travel between them by car.",
    "KG Triples": "1- (Gujan, country, Iran), 2- (Iran, continent, Asia), 3- (Aousserd, country, Western Sahara), 4- (Western Sahara, continent, Africa)",
    "Reasoning Steps": [
      {
        "Step": "Gujan is located in Iran.",
        "facts used in this step": "(Gujan, country, Iran)"
      },
      {
        "Step": "Iran is located in Asia.",
        "facts used in this step": "(Iran, continent, Asia)"
      },
      {
        "Step": "Aousserd is located in Western Sahara.",
        "facts used in this step": "(Aousserd, country, Western Sahara)"
      },
      {
        "Step": "Western Sahara is located in Africa.",
        "facts used in this step": "(Western Sahara, continent, Africa)"
      },
      {
        "Step": "Asia and Africa are different continents and not connected by roads, so it is not possible to travel from Gujan to Aousserd only by car."
      }
    ],
    "Reasoning Strategy": [
      "geographical",
      "physical"
    ]
  }
```

## Citing CR-LT-KGQA
Please see our [paper](https://arxiv.org/pdf/2403.01395.pdf) describing CR-LT-KGQA. If you found this useful, please consider citing us:
~~~
@article{guo2024cr,
  title={CR-LT-KGQA: A Knowledge Graph Question Answering Dataset Requiring Commonsense Reasoning and Long-Tail Knowledge},
  author={Guo, Willis and Toroghi, Armin and Sanner, Scott},
  journal={arXiv preprint arXiv:2403.01395},
  year={2024}
}

~~~

## Data Curation Methodology
### Query Selection
To generate CR-LT-KGQA queries, we first select questions from StrategyQA and claims from CREAK for which the required factual knowledge for answering them is present in Wikidata or that can be rewritten as such queries by targeting them on new KG entities. 
### Entity substitution
In order to ensure that queries target entities from long-tail knowledge, we replace the original famous entities of the query with entities of the same types that are of considerably less amount of popularity. We use the number of Wikidata triples as a measure of popularity of the entities and perform a Google search to ensure the new entities are in fact less famous than the original ones by comparing the amount of search results.

### Question rewriting
We follow the guidelines and schemes proposed by the ["Would you ask it that way"](https://arxiv.org/pdf/2205.12768.pdf) to improve the naturalness of the NL queries, considering aspects such as grammar (e.g., poor word ordering, non-idiomatic) and form (e.g., quizlike, imperative phrasing), and rewrite more natural formulations of the original queries. We also observe that some queries in Creak and StrategyQA are written with making implicit assumptions that are not necessarily correct, so we correct them in the CR-LT-KGQA queries.
## Baseline Methods
To run the baselines, use the following command.
```
python -m baselines.llm <TASK>
python -m baselines.llm <TASK> --few-shot
```
where `<TASK>` is either `question-answering` or `claim-verification`. Add `--few-shot` to use few-shot chain-of-thought instead of zero-shot chain-of-thought. 
