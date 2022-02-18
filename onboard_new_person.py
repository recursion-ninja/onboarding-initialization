#!/bin/python3

# GitHub Parameters,
# Required for authentication and duplication
GITHUB_ACCOUNTNAME = "ACCOUNTNAME" # GitHub User Name of the account which will be performing the duplication
GITHUB_ACCESSTOKEN = "ACCESSTOKEN" # Personal Access Token from granting the user the required permissions.
GITHUB_TEMPLETNAME = "TEMPLETPATH" # The name of the repository to be duplicated, from user's repositories.

import github_duplication
import os
import subprocess
import sys

# Check command line arguments
if len(sys.argv) < 2:
    exit("\n".join(
        [ ""
        , "Error:"
        , "\tYou must supply a new staff member name via the command line!"
        , ""
        , "Example:"
        , "\t" + sys.argv[0] + " NAME"
        , ""
        ]))

if len(sys.argv) > 2:
    exit("\n".join(
        [ ""
        , "Error:"
        , "\tThe staff member's name must NOT contain spaces!"
        , ""
        , "Example:"
        , "\t" + sys.argv[0] + " " + "-".join(sys.argv[1:])
        , ""
        ]))

# New staff member name retreived from command line.
ONBOARD_STAFF_NAME = sys.argv[1]

# Repository Name Definitions
ONBOARD_REPOSITORY = GITHUB_ACCOUNTNAME + "/onboarding-" + ONBOARD_STAFF_NAME
TEMPLET_REPOSITORY = GITHUB_ACCOUNTNAME + "/" + GITHUB_TEMPLETNAME

# 1st create the repository, copying over all the code and commit history.
# To do so, we must export the authentication token to the local environment.
# This is required for `gh` to interact with GitHub.
os.environ['GITHUB_TOKEN'] = GITHUB_ACCESSTOKEN
subprocess.call(
    [ "gh", "repo", "create", ONBOARD_REPOSITORY, "--private", "--template", TEMPLET_REPOSITORY ]
    , stdout=subprocess.DEVNULL
    , stderr=subprocess.STDOUT)

# 2nd copy over all the issues, labels, and milestones with `git_mover.py`.
with open(os.devnull, "w") as devnull:
        # Supress the output of the sub-script, far too noisy.
        old_stdout = sys.stdout
        sys.stdout = devnull
        # Overwrite the command line arguments to control the sub-script parameters.
        progname = sys.argv[0]
        sys.argv = [ progname, GITHUB_ACCOUNTNAME, GITHUB_ACCESSTOKEN, TEMPLET_REPOSITORY, ONBOARD_REPOSITORY ]
        # Finally, call the sub-script.
        github_duplication.main()
        # Restore STDOUT for final reporting.
        sys.stdout = old_stdout

# Print out the result of the duplication!
print("\n".join(
        [ ""
        , "Duplicated repository:"
        , "\t" + "github.com/" + TEMPLET_REPOSITORY
        , ""
        , "Onboarding repository:" 
        , "\t" + "github.com/" + ONBOARD_REPOSITORY
        , ""
        , "Now " + ONBOARD_STAFF_NAME + " is ready to start the onboarding tasks!"
        , ""
        ]))
