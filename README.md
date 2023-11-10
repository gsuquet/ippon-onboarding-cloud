# Ippon Onboarding Cloud & DevOps

## Connection to the AWS account
Use the credentials provided to connect to the AWS management console.

### 1/ Reset your password
Upon first connection, you will be asked to reset your password.

### 2/ Set the region
Set the region to **eu-west-1** (Ireland) in the top right corner of the console.

### 2/ Connect to the Cloud9 environment
In the searchbar at the top of the console, search for **Cloud9** and click on the result.
On the environments page, click on **Open** on the right of the **onboarding-ippon-team-#-cloud9** environment.

### 3/ Install the necessary tools
Clone this repository.
```bash
git clone https://github.com/gsuquet/ippon-onboarding-cloud.git
```

Install the serverless framework and set your TeamName
```bash
npm install -g serverless
export TEAMNAME="<your-team-name>"
```

## 1/ Rekognition
### 1.1/ Deploy stack
```bash
cd 1-Rekognition
serverless deploy --stage $TEAMNAME
```

### 1.2/ Update the index.html file
In the 'index.html' file, replace the **API_GATEWAY_URL** variable with the generated API gateway url from the deployed stack.

### 1.3/ Upload the index.html file to your website bucket
```bash
aws s3 cp ./index.html s3://ippon-onboarding-rekognition-website-$TEAMNAME
```

### 1.4/ Verify your static web page and find the thief
Open the website url in your browser and upload an image to find the thief.
```bash
echo "https://ippon-onboarding-rekognition-website-$TEAMNAME.s3.$(aws s3api get-bucket-location --bucket ippon-onboarding-rekognition-website-$TEAMNAME --output text).amazonaws.com/index.html"
```

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
aws s3 sync s3://workshop-textract-images-$TEAMNAME ./data
```

### 2.4/ Concatenate the CSV files
```bash
./concatenate-csv-files.sh
```

### 2.5/ Upload the CSV file to the S3 bucket
```bash
aws s3 sync ./data s3://workshop-textract-images-$TEAMNAME
```

## 3/ Glue
### 3.1/ Upload the CSV file to the S3 bucket
```bash
cd ../3-Glue
aws s3 cp ./data s3://workshop-textract-images-$TEAMNAME/address --recursive
```

### 3.2/ Create the Glue job
![Glue job](./3-Glue/images/glue-job.png)

Import the csv files from the S3 bucket.
- Data Format : CSV
- Delimiter : Comma (,)
- Quote character : Double quote (")
- First line of file contains colun headers : True
- Infer schema : True

Transform the data using an SQL query.
```sql
select
cast(unbase64(trim(prenom)) as string) as prenom, cast(unhex(trim(nom)) as string) as nom, trim(telephone) as telephone, trim(id_adresse) as id_adresse
from myDataSource
```

Join the two tables using the id_adresse column.
id_adresse = id(inner join)

Export the results to the S3 bucket.
- Format : CSV
- S3 Target Location : s3://workshop-textract-images-$TEAMNAME/results/
- Create a table in the Data Catalog and on subsequent runs, update the schema and add new partitions : True
- Database : debault
- Table name : "TEAMNAME"

Set the IAM role to the GlueServiceRole role.


### 3.3/ Query the results in Athena
Search for the thief address in the results.
Athena query : 
```sql
SELECT * FROM "default"."<Your Team name>" WHERE "prenom" = '<First name of the thief>'
```
or using the cli :
```bash
aws athena start-query-execution --region=eu-west-1 --query-string "SELECT * FROM \"default\".\"$TEAMNAME\" WHERE \"prenom\" = '<First name of the thief>'" --result-configuration OutputLocation=s3://workshop-textract-images-$TEAMNAME/query-results/
```


## 4/ Clean up
### 4.1/ Delete the content of the buckets
```bash
aws s3 rm s3://workshop-textract-images-$TEAMNAME/ --recursive
```

### 4.2/ Delete the stack
```bash
cd ../2-Textract
serverless remove --stage $TEAMNAME
```
