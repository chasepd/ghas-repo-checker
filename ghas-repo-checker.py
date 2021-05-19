import requests
import json
import math
import logging
from dotenv import dotenv_values

config = dotenv_values(".env")

GITHUB_API_URL = "https://api.github.com"
ORG_ENDPOINT = GITHUB_API_URL + "/orgs/" + config["ORGANIZATION_NAME"]
ORG_REPOS_ENDPOINT = ORG_ENDPOINT + "/repos?per_page=100&page={current_page}"
REPO_ENDPOINT = GITHUB_API_URL + "/repos/" + config["ORGANIZATION_NAME"] + "/{repo_name}"
REPO_LANGUAGES_ENDPOIINT = REPO_ENDPOINT + "/languages"
REPO_WORKFLOWS_ENDPOINT = REPO_ENDPOINT + "/contents/.github/workflows"
EXCLUDED = []

CODEQL_SUPPORTED_LANGUAGES = ["c", "c++", "go", "java", "javascript", "python"]

headers = {"Accept": "application/vnd.github.v3+json", "Authorization": "token " + config["GITHUB_ACCESS_TOKEN"]}

try:
    EXCLUDED = json.loads(config["EXCLUDED"])
except KeyError:
    pass


def repoHasSupportedLanguage(repo_name):
    response = requests.get(REPO_LANGUAGES_ENDPOIINT.format(repo_name=repo_name), headers=headers)
    repo_languages = json.loads(response.text)
    repo_is_supported = False

    for language in repo_languages.keys():
        if language.lower() in CODEQL_SUPPORTED_LANGUAGES:
            repo_is_supported = True
        if repo_is_supported:
            break;
    return repo_is_supported
        


if __name__ == "__main__":
    repos_missing_ghas = []
    logging.info("Launching scan of repositories.....")
    response = requests.get(ORG_ENDPOINT, headers=headers)
    org_info = json.loads(response.text)
    total_repos = org_info["total_private_repos"] + org_info["public_repos"]
    pages = math.ceil(total_repos / 100)
    logging.info("Total Repos for {org_name}:".format(org_name=config["ORGANIZATION_NAME"]), total_repos)
    if pages > 1:
        logging.warning("Github only allows 100 repositories per request, requests will be split into {pages} pages.....".format(pages=str(pages)))
    
    logging.warning("Listing repos missing codeql-analysis.yml....")
    current_page = 1
    while current_page <= pages:
        response = requests.get(ORG_REPOS_ENDPOINT.format(current_page=current_page), headers=headers)
        repos = json.loads(response.text)    
        for repo in repos:
            repo = repo["name"]
            response = requests.get(REPO_ENDPOINT.format(repo_name=repo), headers=headers)
            repo_info = json.loads(response.text)
            try:
                if not repo_info["fork"] and not repo_info["disabled"] and not repo_info["archived"] and not repo in EXCLUDED:
                    ghas_enabled = False
                    response = requests.get(REPO_WORKFLOWS_ENDPOINT.format(repo_name=repo), headers=headers)
                    if response.status_code == 200:
                        workflows = json.loads(response.text)
                        for workflow in workflows:
                            if workflow["name"] == "codeql-analysis.yml":
                                ghas_enabled = True
                                break;
                    is_supported = repoHasSupportedLanguage(repo_name=repo)
                    if not ghas_enabled and is_supported:
                        print(repo)
                    elif not is_supported:
                        logging.info("{repo_name} was not listed because it does not contain any supported languages.")
            except KeyError:
                logging.error("Repo not found:", repo, ", tried:", REPO_ENDPOINT.format(repo_name=repo), repo_info["message"])
                
        current_page = current_page + 1

