from picamera import PiCamera
import time
import boto3
import uuid
import requests
import json
from datetime import datetime

directory = '/home/pi/python/masks' #folder name on your raspberry pi

P=PiCamera()
P.resolution= (800,600)
#P.start_preview()
P.start_preview(fullscreen=False,window=(100,200,700,700))
collectionId='mycollection' #collection name

rek_client=boto3.client('rekognition',
                        aws_access_key_id='',
                        aws_secret_access_key='',)

sms_client=boto3.client('sns',
                        aws_access_key_id='',
                        aws_secret_access_key='',)

#configuring setting for sending the mask pictures 
bucket_name = "mira-mask-pictures"
bucket_region = "us-west-2"
upload_client=boto3.client('s3',
                        aws_access_key_id='',
                        aws_secret_access_key='',)

#hardcoded phone numbers for testing
bishesh_number = "+"
mira_number = "+"
fiaz_number = "+"

#hardcoded timeslots
morning = 12
afternoon = 17
evening = 20
night = 0


while True:

        #camera warm-up time
        time.sleep(2)
        
        milli = int(round(time.time() * 1000))
        now = datetime.now()
        current_time_hour = int(now.strftime("%H"))
        current_time = now.strftime("%H:%M:%S")
        image = '{}/image_{}.jpg'.format(directory,current_time)
        P.capture(image) #capture an image
        print('captured '+image)
        with open(image, 'rb') as image:
            try: #match the captured imges against the indexed faces
                match_response = rek_client.search_faces_by_image(CollectionId=collectionId, Image={'Bytes': image.read()}, MaxFaces=1, FaceMatchThreshold=85)
                if match_response['FaceMatches']:
                    print('Hello, ',match_response['FaceMatches'][0]['Face']['ExternalImageId'])
                    print('Similarity: ',match_response['FaceMatches'][0]['Similarity'])
                    print('Confidence: ',match_response['FaceMatches'][0]['Face']['Confidence'])
                    #print(current_time_hour)
                    #print(pickText(int(current_time_hour)))
                    number = mira_number #set default number
                    print("Time: " , current_time_hour)
                    if current_time_hour <= morning and current_time_hour > 9:
                        number = bishesh_number
                    elif current_time_hour <=afternoon and current_time_hour > morning:
                        number = mira_number
                    elif current_time_hour <= evening and current_time_hour > afternoon:
                        number = fiaz_number
                    else:
                        number = mira_number
                    
                    print('******************************************************************')
                    if(match_response['FaceMatches'][0]['Face']['ExternalImageId'] == 'nomask'):
                        print('                         NO MASK')
                        sms_client.publish(PhoneNumber=number, Message="WARNING: The person outside is not wearing a mask. Proceed with caution")
                    elif(match_response['FaceMatches'][0]['Face']['ExternalImageId'] == 'masks'):
                        print('                         MASK DETECTED')
                        sms_client.publish(PhoneNumber=number, Message="Face Mask Detected! It is safe to open your door")
                    else:
                        print("invalid image")
                    print('******************************************************************')
                    
            #upload_client.upload_file('python/masks/image_1603400262950.jpg','index-faces-mira','image_1603400262950.jpg')
    
                else:
                    print('No faces matched')
            except:
                print('No face detected')
            

        time.sleep(10)       
