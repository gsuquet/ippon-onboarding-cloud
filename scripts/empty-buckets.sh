#!/bin/bash

# Get the list of all S3 buckets in the region
buckets=$(aws s3api list-buckets --query "Buckets[].Name" --output text)

# Filter the list of bucket names
filtered_buckets=()
for bucket in $buckets
do
    if [[ $bucket == *"ippon-onboarding-rekognition-website"* || $bucket == *"workshop-textract-images"* ||  $bucket == *"ippon-textract"* || $bucket == *"ippon-rekognition"* ]]; then
        filtered_buckets+=($bucket)
    fi
done

# Iterate over the filtered list of bucket names
for bucket in "${filtered_buckets[@]}"
do
    # Use the AWS CLI command to delete all objects in the bucket
    echo "Emptying bucket: $bucket"
    aws s3 rm s3://$bucket --recursive

done
