#!/usr/bin/env bash

echo Starting Linting, please wait...
echo

ansible-lint -p --project-dir "$PWD" --exclude collections --exclude ansible_collections

# for FILE in playbook_*; do
# 	if [[ $FILE == playbook_* ]]; then
# 		ansible-lint "$FILE"
# 	fi
# done

echo
echo Linting have been completed!
