#!/usr/bin/env python3
# coding=utf-8

import requests
import json
import argparse
import sys

VERBOSE = False

def check_res(r):
    """Test if a response object is valid"""
    # if the response status code is a failure (outside of 200 range)
    if r.status_code < 200 or r.status_code >= 300:
        # print the status code and associated response. Return false
        print("STATUS CODE: " + str(r.status_code))
        print("ERROR MESSAGE: " + r.text)
        print("REQUEST: " + str(r))
        # if error, return False
        return False
    # if successful, return True
    return True


def get_req(url, credentials):
    """
    INPUT: an API endpoint for retrieving data
    OUTPUT: the request object containing the retrieved data for successful requests. If a request fails, False is returned.
    """
    if VERBOSE:
        print("GETTING: " + url)
    r = requests.get(url=url, auth=(credentials['user_name'], credentials['token']), headers={
                     'Content-type': 'application/json'})
    return r


def post_req(url, data, credentials):
    """
    INPUT: an API endpoint for posting data
    OUTPUT: the request object containing the posted data response for successful requests. If a request fails, False is returned.
    """
    if VERBOSE:
        print("POSTING: " + url)
    r = requests.post(url=url, data=data, auth=(credentials['user_name'], credentials['token']), headers={
                      'Content-type': 'application/json', 'Accept': 'application/vnd.github.v3.html+json'})
    return r


def put_req(url, data, credentials):
    """
    INPUT: an API endpoint for posting data
    OUTPUT: the request object containing the posted data response for successful requests. If a request fails, False is returned.
    """
    if VERBOSE:
        print("PUTTING: " + url)
    r = requests.put(url=url, data=data, auth=(credentials['user_name'], credentials['token']), headers={
                      'Content-type': 'application/json', 'Accept': 'application/vnd.github.v3.html+json'})
    return r


def download_milestones(source_url, source, credentials):
    """
    INPUT:
        source_url: the root url for the GitHub API
        source: the team and repo '<team>/<repo>' to retrieve milestones from
    OUTPUT: retrieved milestones sorted by their number if request was successful. False otherwise
    """
    url = source_url + "repos/" + source + "/milestones?filter=all"
    r = get_req(url, credentials)
    status = check_res(r)
    if status:
        # if the request succeeded, sort the retrieved milestones by their number
        sorted_milestones = sorted(json.loads(
            r.text), key=lambda k: k['number'])
        return sorted_milestones
    return False


def download_collaborators(source_url, source, credentials):
    """
    INPUT:
        source_url: the root url for the GitHub API
        source: the team and repo '<team>/<repo>' to retrieve milestones from
    OUTPUT: retrieved milestones sorted by their number if request was successful. False otherwise
    """
    url = source_url + "repos/" + source + "/collaborators?filter=all"
    r = get_req(url, credentials)
    status = check_res(r)
    if status:
        # if the request succeeded, sort the retrieved collaborators by their number
        sorted_collaborators = sorted(json.loads(
            r.text), key=lambda k: k['id'])
        return sorted_collaborators
    return False


def download_issues(source_url, source, credentials):
    """
    INPUT:
        source_url: the root url for the GitHub API
        source: the team and repo '<team>/<repo>' to retrieve issues from
    OUTPUT: retrieved issues sorted by their number if request was successful. False otherwise
    """
    url = source_url + "repos/" + source + "/issues?filter=all"
    r = get_req(url, credentials)
    status = check_res(r)
    if status:
        # if the requests succeeded, sort the retireved issues by their number
        sorted_issues = sorted(json.loads(r.text), key=lambda k: k['number'])
        sorted_issues = [i for i in sorted_issues if not 'pull_request' in i.keys()]
        return sorted_issues
    return False


def download_prs(source_url, source, credentials):
    """
    INPUT:
        source_url: the root url for the GitHub API
        source: the team and repo '<team>/<repo>' to retrieve prs from
    OUTPUT: retrieved prs sorted by their number if request was successful. False otherwise
    """
    url = source_url + "repos/" + source + "/pulls?filter=all"
    r = get_req(url, credentials)
    status = check_res(r)
    if status:
        # if the requests succeeded, sort the retireved prs by their number
        sorted_prs = sorted(json.loads(r.text), key=lambda k: k['number'])
        return sorted_prs
    return False


def download_labels(source_url, source, credentials):
    """
    INPUT:
        source_url: the root url for the GitHub API
        source: the team and repo ']<team>/<repo>' to retrieve labels from
    OUTPUT: retrieved labels if request was successful. False otherwise
    """
    url = source_url + "repos/" + source + "/labels?filter=all"
    r = get_req(url, credentials)
    status = check_res(r)
    if status:
        return json.loads(r.text)
    return False


def download_releases(source_url, source, credentials):
    """
    INPUT:
        source_url: the root url for the GitHub API
        source: the team and repo '<team>/<repo>' to retrieve releases from
    OUTPUT: retrieved releases if request was successful. False otherwise
    """
    url = source_url + "repos/" + source + "/releases"
    r = get_req(url, credentials)
    status = check_res(r)
    if status:
        return json.loads(r.text)
    return False

def create_collaborators(collaborators, destination_url, destination, credentials):
    """Post collaborators to GitHub
    INPUT:
        collaborators: python list of dicts containing collaborators info to be POSTED to GitHub
        destination_url: the root url for the GitHub API
        destination: the team and repo '<team>/<repo>' to post milestones to
    OUTPUT: A list of collaborators
    """
    for collaborator in collaborators:
        if collaborator['login'] == credentials['user_name']:
            continue
        url = destination_url + "repos/" + destination + "/collaborators/" + collaborator["login"]
        perm = "push"
        if collaborator["permissions"]["admin"] == True or collaborator['login'] == credentials['user_name']:
            perm = "admin"

        # create a new collaborator that includes only the attributes needed to create a new milestone
        r = put_req(url, json.dumps({"permission": perm}), credentials)
        status = check_res(r)
        print(status)
    return {"done": "true"}

def create_milestones(milestones, destination_url, destination, credentials):
    """Post milestones to GitHub
    INPUT:
        milestones: python list of dicts containing milestone info to be POSTED to GitHub
        destination_url: the root url for the GitHub API
        destination: the team and repo '<team>/<repo>' to post milestones to
    OUTPUT: A dict of milestone numbering that maps from source milestone numbers to destination milestone numbers
    """
    url = destination_url + "repos/" + destination + "/milestones"
    milestone_map = {}
    for milestone in milestones:
        # create a new milestone that includes only the attributes needed to create a new milestone
        milestone_prime = {"title": milestone["title"], "state": milestone["state"],
                           "description": milestone["description"], "due_on": milestone["due_on"]}
        r = post_req(url, json.dumps(milestone_prime), credentials)
        status = check_res(r)
        if status:
            # if the POST request succeeded, parse and store the new milestone returned from GitHub
            returned_milestone = json.loads(r.text)
            # map the original source milestone's number to the newly created milestone's number
            milestone_map[milestone['number']] = returned_milestone['number']
        else:
            print(status)
    return milestone_map


def create_labels(labels, destination_url, destination, credentials):
    """Post labels to GitHub
    INPUT:
        labels: python list of dicts containing label info to be POSTED to GitHub
        destination_url: the root url for the GitHub API
        destination: the team and repo '<team>/<repo>' to post labels to
    OUTPUT: Null
    """
    url = destination_url + "repos/" + destination + "/labels?filter=all"
    # download labels from the destination and pass them into dictionary of label names
    check_labels = download_labels(destination_url, destination, credentials) or []
    existing_labels = {}
    for existing_label in check_labels:
        existing_labels[existing_label["name"]] = existing_label
    for label in labels:
        # for every label that was downloaded from the source, check if it already exists in the source.
        # If it does, don't add it.
        if label["name"] not in existing_labels:
            label_prime = {"name": label["name"], "color": label["color"]}
            print("Migrating Label: " + label["name"])
            r = post_req(url, json.dumps(label_prime), credentials)
            check_res(r)


def create_releases(releases, destination_url, destination, credentials):
    """Post releases to GitHub
    INPUT:
        releases: python list of dicts containing release info to be POSTED to GitHub
        destination_url: the root url for the GitHub API
        destination: the team and repo '<team>/<repo>' to post releases to
    OUTPUT: Null
    """
    url = destination_url + "repos/" + destination + "/releases"
    # download releases from the destination and pass them into dictionary of
    # release names
    check_releases = download_releases(destination_url, destination, credentials) or []
    existing_releases = {}
    for existing_release in check_releases:
        existing_releases[existing_release["name"]] = existing_release
    for release in releases:
        # for every release that was downloaded from the source, check if it
        # already exists in the destination.
        # If it does, don't add it.
        if release["name"] not in existing_releases:
            release_prime = {"tag_name": release["tag_name"],
                    "target_commitish": release["target_commitish"],
                    "name": release["name"],
                    "body": release["body"],
                    "prerelease": release["prerelease"]}
            print("Migrating Release: " + release["name"])
            r = post_req(url, json.dumps(release_prime), credentials)
            check_res(r)


def create_issues(issues, destination_url, destination, milestones, labels, milestone_map, credentials, sameInstall):
    """Post issues to GitHub
    INPUT:
        issues: python list of dicts containing issue info to be POSTED to GitHub
        destination_url: the root url for the GitHub API
        destination_urlination: the team and repo '<team>/<repo>' to post issues to
        milestones: a boolean flag indicating that milestones were included in this migration
        labels: a boolean flag indicating that labels were included in this migration
    OUTPUT: Null
    """
    url = destination_url + "repos/" + destination + "/issues"
    for issue in issues:
        # create a new issue object containing only the data necessary for the creation of a new issue
        assignee = None
        if (issue["assignee"] and sameInstall):
            assignee = issue["assignee"]["login"]
        body = issue['body']# + '\n\n' + 'Original by @' + issue['user']['login']
        issue_prime = {"title": issue["title"], "body": body,
                       "assignee": assignee, "state": issue["state"]}
        # if milestones were migrated and the issue to be posted contains milestones
        if milestones and "milestone" in issue and issue["milestone"] is not None:
            # if the milestone associated with the issue is in the milestone map
            if issue['milestone']['number'] in milestone_map:
                # set the milestone value of the new issue to the updated number of the migrated milestone
                issue_prime["milestone"] = milestone_map[issue["milestone"]["number"]]
        # if labels were migrated and the issue to be migrated contains labels
        if labels and "labels" in issue:
            issue_prime["labels"] = issue["labels"]
        r = post_req(url, json.dumps(issue_prime), credentials)


        my_data = r.json() # my_data is the response from the POST of the issue
        comment_url = issue["comments_url"] # this is the comment URL used to GET comments from the original issue/pr
        c = get_req(comment_url, credentials) # this is the response from GET of the original comment URL
        my_comments = c.json() # this is the response from GET of the original comment URL in json
        if 'comments_url' in my_data.keys():
            append_comments(my_comments, credentials, my_data["comments_url"])

        status = check_res(r)
        # if adding the issue failed
        if not status:
            # get the message from the response
            message = json.loads(r.text)
            # if the error message is for an invalid entry because of the assignee field, remove it and repost with no assignee
            if 'errors' in message and message['errors'][0]['code'] == 'invalid' and message['errors'][0]['field'] == 'assignee':
                sys.stderr.write("WARNING: Assignee " + message['errors'][0]['value'] + " on issue \"" + issue_prime['title'] +
                                 "\" does not exist in the destination repository. Issue added without assignee field.\n\n")
                issue_prime.pop('assignee')
                post_req(url, json.dumps(issue_prime), credentials)

def append_comments(comments, credentials, comment_url):
    for comment in comments:

        body = comment['body'] + '\n\n' + 'Original by @' + comment['user']['login']
        comment_prime = {'body' : body}
        r = post_req(comment_url, json.dumps(comment_prime), credentials)

        status = check_res(r)
        # if adding the issue failed
        if not status:
            # get the message from the response
            message = json.loads(r.text)
            # if the error message is for an invalid entry because of the assignee field, remove it and repost with no assignee
            if 'errors' in message and message['errors'][0]['code'] == 'invalid' and message['errors'][0]['field'] == 'assignee':
                sys.stderr.write("WARNING: Assignee " + message['errors'][0]['value'] + " on issue \"" + comment_prime['title'] +
                                 "\" does not exist in the destination repository. Issue added without assignee field.\n\n")
                issue_prime.pop('assignee')
                post_req(comment_url, json.dumps(comment_prime), credentials)



def create_prs(prs, destination_url, destination, milestones, labels, milestone_map, credentials, sameInstall):
    """Post prs to GitHub
    INPUT:
        prs: python list of dicts containing pr info to be POSTED to GitHub
        destination_url: the root url for the GitHub API
        destination_urlination: the team and repo '<team>/<repo>' to post prs to
        milestones: a boolean flag indicating that milestones were included in this migration
        labels: a boolean flag indicating that labels were included in this migration
    OUTPUT: Null
    """
    url = destination_url + "repos/" + destination + "/pulls"
    for pr in prs:
        # create a new pr object containing only the data necessary for the creation of a new pr
        assignee = None
        if (pr["assignee"] and sameInstall):
            assignee = pr["assignee"]["login"]
        body = pr['body'] + '\n\n' + 'Original by @' + pr['user']['login']
        pr_prime = {"title": pr["title"], "body": body,
                       "assignee": assignee, "state": pr["state"],
                       "head": pr["head"]["label"], "base": "master"}
        # if milestones were migrated and the pr to be posted contains milestones
        if milestones and "milestone" in pr and pr["milestone"] is not None:
            # if the milestone associated with the pr is in the milestone map
            if pr['milestone']['number'] in milestone_map:
                # set the milestone value of the new pr to the updated number of the migrated milestone
                pr_prime["milestone"] = milestone_map[pr["milestone"]["number"]]
        # if labels were migrated and the pr to be migrated contains labels
        if labels and "labels" in pr:
            pr_prime["labels"] = pr["labels"]
        r = post_req(url, json.dumps(pr_prime), credentials)
        status = check_res(r)
        # if adding the pr failed
        if not status:
            # get the message from the response
            message = json.loads(r.text)
            # if the error message is for an invalid entry because of the assignee field, remove it and repost with no assignee
            if 'errors' in message and message['errors'][0]['code'] == 'invalid' and message['errors'][0]['field'] == 'assignee':
                sys.stderr.write("WARNING: Assignee " + message['errors'][0]['value'] + " on pr \"" + pr_prime['title'] +
                                 "\" does not exist in the destination repository. pr added without assignee field.\n\n")
                pr_prime.pop('assignee')
                post_req(url, json.dumps(pr_prime), credentials)

        my_data = r.json() # my_data is the response from the POST of the issue
        comment_url = pr["comments_url"] # this is the comment URL used to GET comments from the original issue/pr
        c = get_req(comment_url, credentials) # this is the response from GET of the original comment URL
        my_comments = c.json() # this is the response from GET of the original comment URL in json
        if 'comments_url' in my_data.keys():
            append_comments(my_comments, credentials, my_data["comments_url"])

        issue_url = destination_url + "repos/" + destination + "/issues/" + str(my_data["number"])
        pr_update = {'labels': [i['name'] for i in pr['labels']], 'assignees': [i['login'] for i in pr['assignees']]}
        r = post_req(issue_url, json.dumps(pr_update), credentials)
        status = check_res(r)
        # if adding the pr failed
        if not status:
            # get the message from the response
            message = json.loads(r.text)
            # if the error message is for an invalid entry because of the assignee field, remove it and repost with no assignee
            if 'errors' in message and message['errors'][0]['code'] == 'invalid' and message['errors'][0]['field'] == 'assignee':
                sys.stderr.write("WARNING: Assignee " + message['errors'][0]['value'] + " on pr \"" + pr_prime['title'] +
                                 "\" does not exist in the destination repository. pr added without assignee field.\n\n")
                pr_prime.pop('assignee')
                post_req(url, json.dumps(pr_prime), credentials)


def main():
    parser = argparse.ArgumentParser(
        description='Migrate Milestones, Labels, and Issues between two GitHub repositories. To migrate a subset of elements (Milestones, Labels, Issues), use the element specific flags (--milestones, --lables, --issues). Providing no flags defaults to all element types being migrated.')
    parser.add_argument('user_name', type=str,
                        help='Your GitHub (public or enterprise) username: name@email.com')
    parser.add_argument(
        'token', type=str, help='Your GitHub (public or enterprise) personal access token')
    parser.add_argument('source_repo', type=str,
                        help='the team and repo to migrate from: <team_name>/<repo_name>')
    parser.add_argument('destination_repo', type=str,
                        help='the team and repo to migrate to: <team_name>/<repo_name>')
    parser.add_argument('--destinationToken', '-dt', nargs='?', type=str,
                        help='Your personal access token for the destination account, if you are migrating between GitHub installations')
    parser.add_argument('--destinationUserName', '-dun', nargs='?', type=str,
                        help='Username for destination account, if you are migrating between GitHub installations')
    parser.add_argument('--sourceRoot', '-sr', nargs='?', default='https://api.github.com', type=str,
                        help='The GitHub domain to migrate from. Defaults to https://www.github.com. For GitHub enterprise customers, enter the domain for your GitHub installation.')
    parser.add_argument('--destinationRoot', '-dr', nargs='?', default='https://api.github.com', type=str,
                        help='The GitHub domain to migrate to. Defaults to https://www.github.com. For GitHub enterprise customers, enter the domain for your GitHub installation.')
    parser.add_argument('--milestones', '-m', action="store_true",
                        help='Toggle on Milestone migration.')
    parser.add_argument('--labels', '-l', action="store_true",
                        help='Toggle on Label migration.')
    parser.add_argument('--collaborators', '-c', action="store_true",
                        help='Toggle on Collaborator migration.')
    parser.add_argument('--issues', '-i', action="store_true",
                        help='Toggle on Issue migration.')
    parser.add_argument('--prs', '-p', action="store_true",
                        help='Toggle on PR migration.')
    parser.add_argument('--releases', '-r', action="store_true",
                        help='Toggle on Release migration.')
    args = parser.parse_args()

    destination_repo = args.destination_repo
    source_repo = args.source_repo
    source_credentials = {'user_name': args.user_name, 'token': args.token}

    if (args.sourceRoot != 'https://api.github.com'):
        args.sourceRoot += '/api/v3'

    if (args.destinationRoot != 'https://api.github.com'):
        args.destinationRoot += '/api/v3'

    if (args.sourceRoot != args.destinationRoot):
        if not (args.destinationToken):
            sys.stderr.write(
                "Error: Source and Destination Roots are different but no token was supplied for the destination repo.")
            quit()

    if not (args.destinationUserName):
        print('No destination User Name provided, defaulting to source User Name: ' + args.user_name)
        args.destinationUserName = args.user_name
    if not (args.destinationToken):
        print('No destination Token provided, defaulting to source Token: ' + args.token)
        args.destinationToken = args.token

    destination_credentials = {
        'user_name': args.destinationUserName, 'token': args.destinationToken}

    source_root = args.sourceRoot + '/'
    destination_root = args.destinationRoot + '/'

    milestone_map = None

    if args.milestones is False and args.labels is False and args.issues is False and args.releases is False and args.prs is False and args.collaborators is False:
        args.milestones = True
        args.labels = True
        args.issues = True
        args.prs = True
        args.releases = True
        args.collaborators = True

    if args.milestones:
        milestones = download_milestones(
            source_root, source_repo, source_credentials)
        if milestones:
            milestone_map = create_milestones(
                milestones, destination_root, destination_repo, destination_credentials)
        elif milestones is False:
            sys.stderr.write(
                'ERROR: Milestones failed to be retrieved. Exiting...')
            quit()
        else:
            print("No milestones found. None migrated")

    if args.labels:
        labels = download_labels(source_root, source_repo, source_credentials)
        if labels:
            create_labels(labels, destination_root,
                          destination_repo, destination_credentials)
        elif labels is False:
            sys.stderr.write(
                'ERROR: Labels failed to be retrieved. Exiting...')
            quit()
        else:
            print("No Labels found. None migrated")

    if args.collaborators:
        collaborators = download_collaborators(source_root, source_repo, source_credentials)
        if collaborators:
            create_collaborators(collaborators, destination_root,
                        destination_repo, destination_credentials)
        elif collaborators is False:
            sys.stderr.write(
                'ERROR: Collaborators failed to be retrieved. Exiting...')
            quit()
        else:
            print("No Collaborators found. None migrated")

    if args.issues:
        issues = download_issues(source_root, source_repo, source_credentials)
        if issues:
            sameInstall = False
            if (args.sourceRoot == args.destinationRoot):
                sameInstall = True
            create_issues(issues, destination_root, destination_repo, args.milestones,
                          args.labels, milestone_map, destination_credentials, sameInstall)
        elif issues is False:
            sys.stderr.write(
                'ERROR: Issues failed to be retrieved. Exiting...')
            quit()
        else:
            print("No Issues found. None migrated")

    if args.prs:
        prs = download_prs(source_root, source_repo, source_credentials)
        if prs:
            sameInstall = False
            if (args.sourceRoot == args.destinationRoot):
                sameInstall = True
            create_prs(prs, destination_root, destination_repo, args.milestones,
                        args.labels, milestone_map, destination_credentials, sameInstall)
        elif prs is False:
            sys.stderr.write(
                'ERROR: PRs failed to be retrieved. Exiting...')
            quit()
        else:
            print("No PRs found. None migrated")

    if args.releases:
        releases = download_releases(source_root, source_repo, source_credentials)
        if releases:
            create_releases(releases, destination_root, destination_repo,
                    destination_credentials)
        elif releases is False:
            sys.stderr.write(
                'ERROR: Releases failed to be retrieved. Exiting...')
            quit()
        else:
            print("No releases found. None migrated")



if __name__ == "__main__":
    main()
