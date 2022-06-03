import re
import sys

from fastapi import FastAPI, Response, status
from random import choices
from pydantic import BaseModel

app = FastAPI()
sys.setrecursionlimit(1000000000)

# .read().splitlines() ~= .readlines() ,
# but .readlines() "\n" at the end of each item of the list ,
# and .read().splitlines() doesn't ;
words = open("words.txt", "r").read().splitlines()


# return a list of all words wich have 1 letter changed
def get_nearest_words(word, ignored_word):
    similarWords = []

    # index for all letters in word
    for i in range(len(word)):
        # create a regex object:
        # replace the letter at the I position by a .
        # in regex, . means all letters
        _word = list(word)
        _word[i] = "."
        r = re.compile("".join(_word))

        similarWords += [
            line for line in words if r.match(line) and line != word and line not in ignored_word
        ]

    return similarWords


def worker(word, source, target_list, rounds_left):
    if not rounds_left:

        return []

    else:
        words_list = get_nearest_words(word, ignored_word = source)

        word_list = set(words_list)

        result = list(word_list.intersection(target_list))

        if len(result) != 0:

            return [result[0]]

        else:

            propositions = []

            for _word in word_list:

                result = worker(_word, words_list + source, target_list, rounds_left - 1)

                if result is None or result == []:
                    continue

                result = list(result)

                result.insert(0, _word)

                propositions.append(result)

            if len(propositions) == 0:
                return None

            elif len(propositions) == 1:
                return propositions[0]

            else:
                return min(propositions, key = len)


def search(source, target):
    if source == target:
        return [source]

    else:
        max_rounds = 5

        target_list = get_nearest_words(target, [])

        data = worker(source, [], target_list, max_rounds)

        if data is not None:
            data.insert(0, source)
            data.append(target)

        return data


class PathBody(BaseModel):
    starting: str
    objective: str


class GetNearestWords(BaseModel):
    word: str


@app.get("/words")
async def root():
    return choices(words, k = 2)


@app.get("/nearest-words", status_code = 201)
async def nword_req(data: GetNearestWords):
    return get_nearest_words(data.word, [])


@app.get("/path", status_code = 201)
async def say_hello(resp: Response, data: PathBody):
    if (not re.match("([A-Z]|[a-z])", data.starting)) or (not re.match("([A-Z]|[a-z])", data.objective)):
        resp.status_code = status.HTTP_400_BAD_REQUEST
        return {
            "Error": "Statring and Objective objects must be strings"
        }

    elif len(data.starting) != len(data.objective):
        resp.status_code = status.HTTP_422_UNPROCESSABLE_ENTITY
        return {
            "Error": "Statring and Objective objects must be the same lenght"
        }

    elif data.starting not in words or data.objective not in words:
        resp.status_code = status.HTTP_422_UNPROCESSABLE_ENTITY
        return {
            "Error": "At least one of theses words is not in our dictonary"
        }

    else:
        data = search(data.starting, data.objective)

        if data is None:
            resp.status_code = status.HTTP_404_NOT_FOUND
            return {
                "Error": "Could not find any path between thooses two words"
            }

        else:
            return {
                "Path": data,
                "Count": len(data)
            }
