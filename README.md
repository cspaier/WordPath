# WordPath

idea given by @[cspaier](https://github.com/cspaier)


* How to start the API ?
> Just run `uvicorn main:app --reload` </br>
> (you must have uvicorn installed)

### how does it work ?
The API will get all "nearest words" (L¹) of the `source` and the `objective`, in `preloaded.json`. This file has been structured with a simple regex check:
> For example, if the word is `words`, we will decompose in 5 regex checks:
> * `.ords`
> * `w.rds`
> * `wo.ds`
> * `wor.s`
> * `word.`
> In regex, `.` means "Any character", so regex will check any word which have only one letter changed

- If any word is in both list, then the api found a word in `3` step.

- Else it will retrieve all "nearest words"(L²) of the "nearest words" (L¹).


- If any word L² is in the nearest words of the objective, then the api found a way to connect those two words.

- Else, the same process will be applied with Lⁿ⁻¹ and Lⁿ until n = `maxLenght`


### Endpoints
> Get the shortest path between 2 words:
```http
GET /path HTTP/1.1
Host: 127.0.0.1:8000
Content-Type: application/json
Content-Length: 77

{
    "starting": "pomme",
    "objective": "ville",
    "maxLenght": 7
}
```

Get the nearest words of a word:
```http
GET /nearest-words HTTP/1.1
Host: 127.0.0.1:8000
Content-Type: application/json
Content-Length: 25

{
    "word": "ville"
}
```

Get two random words from the dictionary
```http
GET /words HTTP/1.1
Host: 127.0.0.1:8000
```
