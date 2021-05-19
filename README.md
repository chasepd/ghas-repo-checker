# Github Advanced Security Repo Checker

This script scans repositories in an organization to determine which repositories still need to have Github Advanced Security and CodeQL enabled on them. 

It is intended to help with initial deployment of CodeQL, as well as enable an organization to ensure they have not missed newly created repositories while maintaining CodeQL.

## Setting Options

To set options, put the corresponding variable in a .env file in the same directory as the script.

Available options:

GITHUB_ACCESS_TOKEN: (*required*) A personal access token for running the script. Can be created [here](https://github.com/settings/tokens).

ORGANIZATION_NAME: (*required*) The name of the organization to scan. The provided access token must have sufficient privileges to access information in this organization.

EXLUDED: (*optional*) A string containing an array of repository names to ignore. For example:

```
    EXCLUDED='["foo", "test", "bar"]'
```