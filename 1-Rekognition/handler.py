import boto3
import base64
import logging
import traceback

#logger settings
logger = logging.getLogger()
logger.setLevel(logging.INFO)

#Create a rekognition instance
rekognition = boto3.client('rekognition')

# lambda_handler function definition (main logic)
def lambda_handler(event, context):
    logger.info(f'Received event = {event}')
    
    #Since the binary data is received in the Base64 format encoded, it is decoded into bytes type.
    received_body = base64.b64decode(event['body'])
    
    #Excludes file information given by AWS (bytes character string)'\r\n'The main body information of the file uploaded by the 4th and subsequent ones)
    images  = received_body.split(b'\r\n',4)
    image   = images[4]
    
    #Pass the acquired Blob format image information to Rekognition to identify the celebrity
    response = rekognition.recognize_celebrities(
        Image={'Bytes': image}
    )
    logger.info(f'Rekognition response = {response}')
    
    try:
        #Extract the reliability of the celebrity name from the Rekognition response and respond to the API caller.
        label   = response['CelebrityFaces'][0]
        name    = label['Name']
        conf    = round(label['Face']['Confidence'])
        output  = f'He/She is {name} with {conf}% confidence.'
        logger.info(f'API response = {output}')
        # create a response
        response = {
        "statusCode": 200,
        "body": output
        }

        return response
        
    except IndexError as e:
        #If you can't get celebrity information from Rekognition's response, tell them to use another photo.
        logger.info(f"Coudn't detect celebrities in the Photo. Exception = {e}")
        logger.info(traceback.format_exc())
        return "Couldn't detect celebrities in the uploaded photo. Please upload another photo."