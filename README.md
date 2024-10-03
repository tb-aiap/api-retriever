# api-retriever

This is a repository for testing API integration and data analysis from API results, with [Github's API](https://docs.github.com/en/rest?apiVersion=2022-11-28)

# 1. Environment and Setup

This repo uses the following python version within a virtual environment.

```bash
$ python --version
Python 3.11.9
```

## 1.1 - .env file setup

This repo also uses `.env` file to manage its settings. Most settings has their default values, but personal access token for Github is required for higher rate limit as compared to [default rate limit of 60](https://docs.github.com/en/rest/rate-limit/rate-limit?apiVersion=2022-11-28).

```bash
# .env file in the same folder level as src. (outside of src)
ACCESS_TOKEN=your_access_token

# other settings
TIMEOUT=20
MAX_RETRY=5

# enum values, reflects the key value in github api
STAR_COLUMNS=stargazers_count
```
## Running the script

Run the command with `src/main.py` followed by a `organization` argument. Below shows the example to retrieve `fastapi` repository. The organization name is the same as the website https://github.com/fastapi. 

```bash
# run the command to retrieve api
$ python src/main.py repo_name

# example
$ python src/main.py fastapi
```

### Expected output

```bash
$ python src/main.py fastapi
# sample output
{"asctime": "2024-10-03T14:54:43+0800", "process": 8372, "name": "__main__", "levelname": "INFO", "message": "Connecting to fastapi GitHub repositories"}
{"asctime": "2024-10-03T14:54:43+0800", "process": 8372, "name": "api_retriever", "levelname": "INFO", "message": "Retrieving from API https://api.github.com/orgs/fastapi/repos?page=1&per_page=100"}
{"asctime": "2024-10-03T14:54:43+0800", "process": 8372, "name": "__main__", "levelname": "INFO", "message": "Analyzing repository data."}
{'most_popular_language': 'Python',
 'top_5_repositories': [{'name': 'fastapi', 'stars': 76201},
                        {'name': 'full-stack-fastapi-template', 'stars': 26596},
                        {'name': 'typer', 'stars': 15513},
                        {'name': 'sqlmodel', 'stars': 14189},
                        {'name': 'asyncer', 'stars': 1635}],
 'total_repositories': 6,
 'total_stars': 134462}

```

### With pagination

For organization with large repositories count, the script will loop through `request.link.next` key to identify the next page url for parsing. Then returning the response with FULL repositories information.

```bash
$ src/main.py google 
# sample outout
{"asctime": "2024-10-03T14:57:41+0800", "process": 22848, "name": "__main__", "levelname": "INFO", "message": "Connecting to google GitHub repositories"}
{"asctime": "2024-10-03T14:57:41+0800", "process": 22848, "name": "api_retriever", "levelname": "INFO", "message": "Retrieving from API https://api.github.com/orgs/google/repos?page=1&per_page=100"}

# log statement to show all api calls across various pages.
{"asctime": "2024-10-03T14:58:10+0800", "process": 22848, "name": "api_retriever", "levelname": "INFO", "message": "Retrieving from API https://api.github.com/organizations/1342004/repos?page=14&per_page=100"}
{"asctime": "2024-10-03T14:58:12+0800", "process": 22848, "name": "api_retriever", "levelname": "INFO", "message": "Retrieving from API https://api.github.com/organizations/1342004/repos?page=15&per_page=100"}

# final output after 27 pages
{"asctime": "2024-10-03T14:58:39+0800", "process": 22848, "name": "api_retriever", "levelname": "INFO", "message": "Retrieving from API https://api.github.com/organizations/1342004/repos?page=27&per_page=100"}
{"asctime": "2024-10-03T14:58:41+0800", "process": 22848, "name": "__main__", "levelname": "INFO", "message": "Analyzing repository data."}
{'most_popular_language': 'Python',
 'top_5_repositories': [{'name': 'material-design-icons', 'stars': 50473},
                        {'name': 'guava', 'stars': 50071},
                        {'name': 'zx', 'stars': 42923},
                        {'name': 'styleguide', 'stars': 37303},
                        {'name': 'leveldb', 'stars': 36291}],
 'total_repositories': 2675,
 'total_stars': 1847849}
```

### Rate Limit and Retries

Description of rate limit and retries being implemented.

For single api call, there is `timeout` and `retries` logic as follows.
- Retry for 5 times in event of TimeOut or Connection Error.
- For each API call, set a TimeOut of 20 seconds.

Currently there are 2 rate limiter logic in this script.
- if `call_remaining` is less than 30, throttle the API call to 10 secs per call.
- if `call_remaining` is less than 1, raise `ValueError` and exit the program.