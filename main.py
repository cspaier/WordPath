import json
import re
from fastapi import FastAPI, Response, status
from random import choices
from pydantic import BaseModel

import preload

app = FastAPI()

NearestWords = preload.NearestWords()

# .read().splitlines() ~= .readlines() ,
# but .readlines() "\n" at the end of each item of the list ,
# and .read().splitlines() doesn't ;
words = open("words.txt", "r").read().splitlines()

preload = False
lenght_limit = False

# preload the words in preload.json
if preload:
    NearestWords.load(words)

nearest = json.load(open("preload.json", "r"))


def worker(word, target_list, rounds_left, banned_words):
    if not rounds_left:
        return None

    word_list = set(NearestWords.get_nearest_words(word, banned_words))

    if result := list(word_list.intersection(target_list)):
        return [result[0]]

    propositions = []

    for _word in (word for word in word_list if word not in banned_words):

        result = worker(_word, target_list, rounds_left - 1, banned_words)

        if result is None:
            continue

        result.insert(0, _word)

        propositions.append(result)

    return min(propositions, key=len) if propositions else None


def search(source, target, max_rounds):
    if source == target:
        return [source]

    target_list = NearestWords.get_nearest_words(target, [])

    data = worker(source, target_list, max_rounds, [])

    if data:
        data.insert(0, source)
        data.append(target)

    return data


# represent the wanted objects in Body's request
class PathBody(BaseModel):
    starting: str
    objective: str
    maxLength: int = 7


class GetNearestWords(BaseModel):
    word: str


@app.get("/words")
async def root():
    return choices(words, k=2)


@app.get("/nearest-words", status_code=201)
async def nword_req(resp: Response, data: GetNearestWords):
    if data.word in words:
        return NearestWords.get_nearest_words(data.word, [])
    resp.status_code = status.HTTP_404_NOT_FOUND
    return {"Error": "This word is not in our dictionary"}


@app.get("/path", status_code=200)
async def say_hello(resp: Response, data: PathBody):
    if (not re.match("^([A-Za-z]){5}$", data.starting)) or (
        not re.match("^([A-Za-z]){5}$", data.objective)
    ):
        resp.status_code = status.HTTP_400_BAD_REQUEST
        return {
            "Error": "Starting and Objective objects must RegEx match ^([A-Za-z]){5}$"
        }

    if data.starting not in words or data.objective not in words:
        resp.status_code = status.HTTP_422_UNPROCESSABLE_ENTITY
        return {"Error": "At least one of theses words is not in our dictionary"}


    elif not 3 <= data.maxLenght <= 10 and lenght_limit:
        resp.status_code = status.HTTP_400_BAD_REQUEST
        return {"Error": "maxLength must be between 3 and 10 (included)"}

    data = search(data.starting, data.objective, data.maxLength - 2)

    if data is not None:
        return {"Path": data, "Count": len(data)}
    resp.status_code = status.HTTP_404_NOT_FOUND
    return {"Error": "Could not find any path between those two words"}
