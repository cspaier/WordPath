import re
from fastapi import FastAPI, Response, status
from random import choices
from pydantic import BaseModel

app = FastAPI()

# .read().splitlines() ~= .readlines() ,
# but .readlines() "\n" at the end of each item of the list ,
# and .read().splitlines() doesn't ;
words = open("words.txt", "r").read().splitlines()


# return a list of all words wich have 1 letter different
def get_nearest_words(word, word_list):
    similarWords = []

    # index for all letters in word
    for i in range(len(word)):
        # create a regex object:
        # replace the letter at the I position by a .
        # in regex, . means all letters

        r = re.compile(word[:i] + "." + word[i+1:])

        similarWords += [
            line for line in word_list if r.match(line) and line != word
        ]

    return similarWords


def worker(word, target_list, rounds_left, _words):

    if not rounds_left:

        return None

    else:
        word_list = set(get_nearest_words(word, _words))

        result = list(word_list.intersection(target_list))

        if result:

            return [result[0]]

        else:

            _words = [acceptable_word for acceptable_word in _words if acceptable_word not in word_list]

            propositions = []

            for _word in word_list:

                result = worker(_word, target_list, rounds_left - 1, _words)

                if result is None:

                    continue

                result.insert(0, _word)

                propositions.append(result)

            if not propositions:
                return None

            else:
                return min(propositions, key = len)


def search(source, target, max_rounds):
    if source == target:
        return [source]

    else:

        words_list = words.copy()

        target_list = get_nearest_words(target, words_list)

        data = worker(source, target_list, max_rounds, words_list)

        if data:
            data.insert(0, source)
            data.append(target)

        return data


# represent the wanted objects in Body's request
class PathBody(BaseModel):
    starting: str
    objective: str
    maxLenght: int = 7


class GetNearestWords(BaseModel):
    word: str


@app.get("/words")
async def root():
    return choices(words, k = 2)


@app.get("/nearest-words", status_code = 201)
async def nword_req(data: GetNearestWords):
    return get_nearest_words(data.word, words)


@app.get("/path", status_code = 200)
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

    elif not 3 <= data.maxLenght <= 8:
        resp.status_code = status.HTTP_400_BAD_REQUEST
        return {
            "Error": "maxLenght must be between 3 and 8 (included)"
        }

    else:

        data = search(data.starting, data.objective, data.maxLenght - 2)

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
