SHELL := /bin/bash

.PHONY: create-users create-cloud9 empty-buckets delete-stacks delete-users

TEAM_NUMBERS := $(shell seq 1 1)

create-users: create-users-$(TEAM_NUMBERS)

create-users-%:
	@mkdir -p secrets
	@user="team-$*"; \
	aws iam create-user --user-name $$user; \
	aws iam attach-user-policy --policy-arn arn:aws:iam::aws:policy/AdministratorAccess --user-name $$user; \
	aws iam create-login-profile --user-name $$user --password MyPassword_$$user --password-reset-required > secrets/console_login_$$user.json; \
	aws iam create-access-key --user-name $$user > secrets/access_key_$$user.json

create-cloud9: create-cloud9-$(TEAM_NUMBERS)

create-cloud9-%:
	@user="team-$*"; \
	aws cloudformation create-stack --stack-name cloud9-$$user --template-body file://cloud9.yml --parameters ParameterKey=TeamName,ParameterValue=$$user --region eu-west-1

empty-buckets:
	@buckets=$$(aws s3api list-buckets --query "Buckets[].Name" --output text); \
	filtered_buckets=(); \
	for bucket in $$buckets; do \
		if [[ $$bucket == *"ippon-onboarding-rekognition-website"* || $$bucket == *"workshop-textract-images"* ||  $$bucket == *"ippon-textract"* || $$bucket == *"ippon-rekognition"* ]]; then \
			filtered_buckets+=($$bucket); \
		fi; \
	done; \
	for bucket in $${filtered_buckets[@]}; do \
		echo "Emptying bucket: $$bucket"; \
		aws s3 rm s3://$$bucket --recursive; \
	done

delete-stacks:
	@stacks=$$(aws cloudformation list-stacks --region eu-west-1 --stack-status-filter CREATE_COMPLETE DELETE_FAILED --query 'StackSummaries[].StackName' --output text); \
	for stack in $$stacks; do \
		if [[ $$stack == *"ippon-textract"* || $$stack == *"ippon-rekognition"* || $$stack == *"cloud9"* ]]; then \
			echo "Deleting stack: $$stack"; \
			aws cloudformation delete-stack --region eu-west-1 --stack-name $$stack; \
		fi; \
	done

delete-users:
	@users=$$(aws iam list-users --query 'Users[].UserName' --output text); \
	for user in $$users; do \
		if [[ $$user == team-* ]]; then \
			echo "Deleting user: $$user"; \
			aws iam delete-login-profile --user-name $$user; \
			aws iam delete-access-key --user-name $$user --access-key-id $$(aws iam list-access-keys --user-name $$user --query 'AccessKeyMetadata[].AccessKeyId' --output text); \
			aws iam detach-user-policy --policy-arn arn:aws:iam::aws:policy/AdministratorAccess --user-name $$user; \
			aws iam delete-user --user-name $$user; \
		fi; \
	done
