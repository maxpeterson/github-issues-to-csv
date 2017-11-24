# github-issues-to-csv

Utilities to export GitHub issues to CSV.

# Usage

Install `pipenv` - https://docs.pipenv.org/


Install dependencies

```
pipenv install
```


Export a repositories issues to a CSV

```
pipenv run python issues2csv.py <username>/<repo> -t <your_gihub_oauth_token> -o <output-file.csv>
```


Export projects to a CSV

```
pipenv run python projects2csv.py <username>/<repo> -t <your_gihub_oauth_token> -o <output-file.csv>
```


Export issues from a projects cards to a CSV

```
pipenv run python cards2csv.py <project_id> -t <your_gihub_oauth_token> -o <output-file.csv>
```
