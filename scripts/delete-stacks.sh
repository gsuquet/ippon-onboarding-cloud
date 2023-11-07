#!/bin/bash

# Get the list of all CloudFormation stacks
stacks=$(aws cloudformation list-stacks --region eu-west-1 --stack-status-filter CREATE_COMPLETE DELETE_FAILED --query 'StackSummaries[].StackName' --output text)

# Filter the list of stack names
filtered_stacks=()
for stack in $stacks
do
    if [[ $stack == *"ippon-textract"* || $stack == *"ippon-rekognition"* || $stack == *"cloud9"* ]]; then
        filtered_stacks+=($stack)
    fi
done

# Iterate over the filtered list of stack names
for stack in "${filtered_stacks[@]}"
do
    # Use the AWS CLI command to delete the stack
    echo "Deleting stack: $stack"
    aws cloudformation delete-stack --region eu-west-1 --stack-name $stack
done
