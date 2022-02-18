# Onboard New Staff Template
A Python script to migrate milestones, collaborators, comments, labels, issues, pull requests, and releases between repositories.
The script is a fork of GitMover.


## System Dependencies
You must have the GitHub command line tool [`gh`][0] installed.


## Python Dependencies
You'll need a few Python modules installed. Install them with `pip`:

```
pip3 install -r requirements.txt
```


## Configuration
The top of the `onboard_new_person.py` contains three variables which must be manually hardcoded:

```python
GITHUB_ACCOUNTNAME = "ACCOUNTNAME" # GitHub User Name of the account which will be performing the duplication.
GITHUB_ACCESSTOKEN = "ACCESSTOKEN" # Personal Access Token from granting the user the required permissions.
GITHUB_TEMPLETNAME = "TEMPLETPATH" # The name of the repository to be duplicated, from user's repositories.
```

  - `GITHUB_ACCOUNTNAME`: The GitHub user name of the GitHub account which will be performing the repository duplication via the GitHub API. Both the source templet repository and the destination duplicate repository must be owned by the GitHub user.

  - `GITHUB_ACCESSTOKEN`: The GitHub "Personal Access Token" for the GitHub account which will be interacting with the GitHub API. The token must grant the GitHub account the requisite permissions to duplicate the repository. You can create a GitHub Personal Access Token by following [these instructions][1].

  - `GITHUB_TEMPLETNAME`: The GitHub repository name which will be used as the source of the duplication. The templet repository must be ownded by the GitHub user interacting with the GitHub API.


## Usage


**No arguments**, *error*:
```bash
$ ./onboard_new_person.py

Error:
	You must supply a new staff member name via the command line!

Example:
	./onboard_new_person.py NAME

```

**One argument**, *success*:
```bash
$ ./onboard-new-person.py David

Duplicated repository:
	github.com/GITHUB_ACCOUNTNAME/GITHUB_TEMPLETNAME

Onboarding repository:
	github.com/GITHUB_ACCOUNTNAME/David

Now David is ready to start the onboarding tasks!

```


**Two arguments** (or more), *error*:
```bash
$ ./onboard_new_person.py David Bowe

Error:
	The staff member's name must NOT contain spaces!

Example:
	./onboard_new_person.py David-Bowe

```

**One argument** (compound), *success*:
```bash
$ ./onboard-new-person.py David-Bowe

Duplicated repository:
	github.com/GITHUB_ACCOUNTNAME/GITHUB_TEMPLETNAME

Onboarding repository:
	github.com/GITHUB_ACCOUNTNAME/David-Bowe

Now David-Bowe is ready to start the onboarding tasks!

```




[0]: https://github.com/cli/cli#installation
[1]: https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/creating-a-personal-access-token