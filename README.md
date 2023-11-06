# Ippon Onboarding Cloud & DevOps

## Setup
Install [AWS CLI](https://docs.aws.amazon.com/cli/latest/userguide/getting-started-install.html ) and configure it with your credentials.

Set your team name.
```bash
export TEAMNAME=gsuquet
```

Create a Cloud9 environment in the eu-west-1 region.
```bash
aws cloudformation create-stack --stack-name cloud9-$TEAMNAME --template-body file://cloud9.yml --parameters ParameterKey=TeamName,ParameterValue=$TEAMNAME --region eu-west-1
```

Connect to the Cloud9 environment and clone this repository.
```bash
git clone https://github.com/gsuquet/ippon-tp-cloud.git
```

Install the serverless framework.
```bash
npm install -g serverless
```

## 1/ Rekognition
### 1.1/ Deploy stack
```bash
cd 1-Rekognition
serverless deploy --stage $TEAMNAME
```

### 1.2/ Update the index.html file
Download the 'index.html' file and Replace the API_GATEWAY_URL variable with the generated API gateway url from the deployed stack.

### 1.3/ Upload the index.html file to your website bucket
```bash
aws s3 cp ./index.html s3://ippon-onboarding-rekognition-website-$TEAMNAME
```

### 1.4/ Verify your static web page and find the thief
Open the website url in your browser and upload an image to find the thief.

### 1.5/ Delete the content of the bucket
```bash
aws s3 rm s3://ippon-onboarding-rekognition-website-$TEAMNAME --recursive
```

### 1.6/ Delete the stack
```bash
serverless remove --stage $TEAMNAME
```

## 2/ Textract
### 2.1/ Deploy stack
```bash
cd ../2-Textract
serverless deploy --stage $TEAMNAME
```

### 2.2/ Copy the images to the S3 bucket
```bash
aws s3 cp ./data s3://workshop-textract-images-$TEAMNAME --recursive
```

### 2.3/ Sync the S3 bucket with the data folder to get the resulting CSV files
```bash
aws s3 sync s3://workshop-textract-results-$TEAMNAME ./data
```

### 2.4/ Concatenate the CSV files
```bash
cat ./data/*.csv > ./data/suspects.csv
sed -i '/^$/d' ./data/suspects.csv
```

### 2.5/ Upload the CSV file to the S3 bucket
```bash
aws s3 sync ./data s3://workshop-textract-results-$TEAMNAME
```
