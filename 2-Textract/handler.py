import json
import boto3
import os

def hello(event, context):
    body = {
        "message": "Go Serverless v1.0! Your function executed successfully!",
        "input": event
    }

    print(("boto3 version:"+boto3.__version__))
    #print("botocore version:"+botocore.__version__)

    table_name = os.environ['tableName']
    bucket_name = os.environ['bucketName']

    print((json.dumps(event)))

    dynamodb_client = boto3.client("dynamodb")
    textract_client = boto3.client('textract')
    s3_client = boto3.client('s3')

    for sqs_record in event['Records']:
        print((json.dumps(sqs_record)))
        body = json.loads(sqs_record["body"])

        if "Records" in body:
            for record in body['Records']:
                key_object = record["s3"]["object"]["key"]
                bucket_name = record["s3"]["bucket"]["name"]
                if key_object[-3:]=="jpg" or key_object[-3:]=="png":
                    print("Document")
                    response = textract_client.analyze_document(Document={'S3Object': {'Bucket': bucket_name,'Name': key_object}}, FeatureTypes=['TABLES'])
                    print((json.dumps(response)))

                    #Process results
                    blocks = response['Blocks']
                    table_csv = get_table_csv_results(blocks)
                    output_file = key_object + "-results.csv"

                    #Send results to S3
                    # s3_client.put_object(Body=json.dumps(response), Bucket=bucket_name, Key=key_object+'.json')
                    s3_client.put_object(Body=table_csv, Bucket=bucket_name, Key='textract/'+output_file)

                    response = dynamodb_client.put_item(
                        TableName=table_name,
                        Item={
                            'key_object': {
                                'S': key_object
                            },
                            'bucket_name': {
                                'S': bucket_name
                            },
                            'size_object': {
                                'N': str(record["s3"]["object"]["size"]),
                            }
                        }
                    )

    response = {
        "statusCode": 200,
        "body": json.dumps(body)
    }

    return response


def get_rows_columns_map(table_result, blocks_map):
    rows = {}
    for relationship in table_result['Relationships']:
        if relationship['Type'] == 'CHILD':
            for child_id in relationship['Ids']:
                try:
                    cell = blocks_map[child_id]
                    if cell['BlockType'] == 'CELL':
                        row_index = cell['RowIndex']
                        col_index = cell['ColumnIndex']
                        if row_index not in rows:
                            # create new row
                            rows[row_index] = {}

                        # get the text value
                        rows[row_index][col_index] = get_text(cell, blocks_map)
                except KeyError:
                    print("Error extracting Table data - {}:".format(KeyError))
                    pass
    return rows

def get_text(result, blocks_map):
    text = ''
    if 'Relationships' in result:
        for relationship in result['Relationships']:
            if relationship['Type'] == 'CHILD':
                for child_id in relationship['Ids']:
                    try:
                        word = blocks_map[child_id]
                        if word['BlockType'] == 'WORD':
                            text += word['Text'] + ' '
                        if word['BlockType'] == 'SELECTION_ELEMENT':
                            if word['SelectionStatus'] == 'SELECTED':
                                text += 'X '
                    except KeyError:
                        print("Error extracting Table data - {}:".format(KeyError))

    return text

def get_table_csv_results(blocks):

    blocks_map = {}
    table_blocks = []
    for block in blocks:
        blocks_map[block['Id']] = block
        if block['BlockType'] == "TABLE":
            table_blocks.append(block)

    if len(table_blocks) <= 0:
        return "<b> NO Table FOUND </b>"

    csv = ''
    for index, table in enumerate(table_blocks):
        csv += generate_table_csv(table, blocks_map, index + 1)
        csv += '\n\n'
        # In order to generate separate CSV file for every table, uncomment code below
        #inner_csv = ''
        #inner_csv += generate_table_csv(table, blocks_map, index + 1)
        #inner_csv += '\n\n'
        #output_file = file_name + "___" + str(index) + ".csv"
        # replace content
        #with open(output_file, "at") as fout:
        #    fout.write(inner_csv)

    return csv


def generate_table_csv(table_result, blocks_map, table_index):
    rows = get_rows_columns_map(table_result, blocks_map)

    csv = ""

    for row_index, cols in rows.items():

        for col_index, text in cols.items():
            csv += '{}'.format(text) + ","
        csv += '\n'

    csv += '\n\n\n'
    return csv
