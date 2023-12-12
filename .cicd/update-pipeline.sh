#!/bin/bash
gitlab_token=""
github_token=""

if [ -z "$GITLAB_ACCESS_TOKEN" ]; then
  read -s -p "GitLab Access Token: " gitlab_token
else
  gitlab_token="$GITLAB_ACCESS_TOKEN"
fi
echo
if [ -z "$GITHUB_ACCESS_TOKEN" ]; then
  read -s -p "GitHub Access Token: " github_token
else
  github_token="$GITHUB_ACCESS_TOKEN"
fi
echo

fly -t dev sp \
  -p cpe.robot-project-mirror \
  -c .cicd/main-pipeline.yaml \
  -v gitlab-access-token="$gitlab_token" \
  -v github-access-token="$github_token"
