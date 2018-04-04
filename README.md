# AWS-tools

Some personal tools to make working with AWS easier.
All tools require AWS CLI and ECS CLI configured

## clean-ecr-repo

ECR per default has max 1000 images allowed, this script queries AWS and then
deletes all images older than the number of days specified
