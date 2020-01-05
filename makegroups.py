import os
import boto3
from utils import *
import pprint
from tqdm import tqdm
import shutil
def delete_folder(userid):
    try:
        if os.path.exists(os.path.dirname(userid)):    
            shutil.rmtree(userid)
    except Exception as e:
            print("error on line 12 makegroup.py",e)


def get_connection(bucketName="phosphene-users"):
    ACCESS_KEY_ID=os.getenv("ACCESS_KEY_ID")
    ACCESS_SECRET_KEY = os.getenv("ACCESS_SECRET_KEY_ID")
    print(ACCESS_KEY_ID,ACCESS_SECRET_KEY)
    try:
        s3_resource=boto3.resource("s3",aws_access_key_id=ACCESS_KEY_ID,aws_secret_access_key=ACCESS_SECRET_KEY)
        s3_client= boto3.client('s3',aws_access_key_id=ACCESS_KEY_ID,aws_secret_access_key=ACCESS_SECRET_KEY)
         #s3_client= boto3.client('s3', aws_access_key_id=os.getenv("AWS_ACCESS_KEY"),aws_secret_access_key=("AWS_SECRET_KEY"))
         #s3_resource = boto3.resource('s3', aws_access_key_id=os.getenv("AWS_ACCESS_KEY"),aws_secret_access_key=("AWS_SECRET_KEY"))
        bucket = s3_resource.Bucket(bucketName) 
        return s3_client,s3_resource,bucket
    except Exception as e:
         print(" error on line 21 makegroup.py",e)
         return False

def create(s3_client,id,bucketName="phosphene-users"):
    try:
        response = s3_client.put_object(Bucket=bucketName, Key=(id))
        return response
    except Exception as e:
        print("error on makegroup.py line 29",e)
        return False

def add_photo(s3_client,userid,file,filename,bucketName="phosphene-users"):
    try:
        response=s3_client.upload_fileobj(file,bucketName,userid+"/"+filename)
        return response
    except Exception as e:
        print("error in line 37 makegroup.py",e)
        return False

def do_process_create(userid):
    if not userid:
        return({"info":"userid is required"})
    userid=userid+"/"
    try:
        s3_client,s3_resource,bucket =get_connection()
        result=create(s3_client,userid)
        if result !=False:
            return {
                    "messege":userid+" created_successfully"
             }
        else:
            return {
                "error":"file cant be created"
            }
    except Exception as e:
        print(e)
        return {
                "error":str(e)
        }

def do_process_addphoto(userid,file,filename):
    try:
        s3_client,s3_resource,bucket =get_connection()
        result=add_photo(s3_client,userid,file,filename)
        if result != False:
            return {
                "messege":file.name+"created successfully"
            }
        else :
            return {
                "error":"file cant be created"
            }
    except Exception as e:
        print(e)
        return {
                "error":str(e)
        }

def downloadDirectoryFroms3(bucket,remoteDirectoryName):
    for object in tqdm(bucket.objects.filter(Prefix = remoteDirectoryName)):
        try:
            if object.key == remoteDirectoryName:
                if not os.path.exists(os.path.dirname(object.key)):
                    os.makedirs(os.getcwd()+"/"+os.path.dirname(object.key))
            else :
                bucket.download_file(object.key,os.getcwd()+"/"+object.key)
                # print(object.key,"downloaded")
        except Exception as e:
            print("error on makegroup.py line 79",e)



def do_process_group(userid):
    if not userid:
        return({"info":"userid is required"})
    userid=userid+"/"
    try:
        s3_client, s3_resource,bucket =get_connection()
        downloadDirectoryFroms3(bucket,userid)
        result = do_grouping(userid)
        delete_folder(userid)
        if result == []:
            return {}
        return result
    except Exception as e:
        print("error on makegroup.py line 94",e)
        return{
            "error":str(e)
        }

def  getAllImages(bucket,folder):
    return_arr=[]
    for object in tqdm(bucket.objects.filter(Prefix = folder)):
        if object.key != folder:
            return_arr.append(object.key)
    return return_arr


def do_process_fetch_images(folder,bucket="phosphene-users"):
    if not folder:
        return {
            "info":"user id is required"
        }
    userid=folder+"/"
    try:
        s3_client, s3_resource,bucket =get_connection()
        output= getAllImages(bucket,userid)
        return {
            "userid":folder,
            "images":output
        }
    except Exception as e:
        print("error in line 133 makegroups.py",e)
        return {
            "error":str(e)
        }
