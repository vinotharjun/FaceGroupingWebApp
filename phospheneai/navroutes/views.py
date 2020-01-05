from django.shortcuts import render
from django.views import View
import boto3
import boto
import requests,json,os
import base64
from PIL import Image
from django.shortcuts import render_to_response
from smart_open import smart_open
from django.conf import settings
from botocore.client import Config
from django.core.files.storage import FileSystemStorage
from boto.s3.key import Key
from tqdm import tqdm

def get_connection(bucketName="phosphene-users"):
    ACCESS_KEY_ID=os.getenv("ACCESS_KEY_ID")
    ACCESS_SECRET_KEY=os.getenv("ACCESS_SECRET_KEY")
    try:
        s3_resource=boto3.resource("s3",aws_access_key_id=ACCESS_KEY_ID,aws_secret_access_key=ACCESS_SECRET_KEY)
        s3_client= boto3.client('s3',aws_access_key_id=ACCESS_KEY_ID,aws_secret_access_key=ACCESS_SECRET_KEY)
        bucket = s3_resource.Bucket(bucketName) 
        return s3_client,s3_resource,bucket
    except Exception as e:
         print(" error on line 21 makegroup.py",e)
         return False

def downloads3getimages(bucket,remoteDirectoryName,finalpath):
    print(finalpath)
    for object in tqdm(bucket.objects.filter(Prefix = remoteDirectoryName)):
        try:
            if not os.path.exists(finalpath):
                os.makedirs(finalpath+object.key)
            else:
                bucket.download_file(object.key,finalpath+object.key)
        except Exception as e:
            print("error on makegroup.py line 79",e)

def downloadDirectoryFroms3(bucket,remoteDirectoryName,final_path,filename):
    final_path+=filename
    filename = remoteDirectoryName+filename
    for object in tqdm(bucket.objects.filter(Prefix = remoteDirectoryName)):
        try:
            if object.key == filename:
                bucket.download_file(object.key,final_path)
        except Exception as e:
            print("error on makegroup.py line 79",e)        

def createfolder(request):
    if request.method == 'POST':
        album_name = request.POST['foldername']
        files = {
        'userid': (None, album_name),
        }
        response = requests.post('http://127.0.0.1:5000/createalbum', files=files)
        api_values = response.json()
    return render(request,'createfolder.html')

def getimages(request):
    if request.method == 'POST':
        temp = {}
        album_name = str(request.POST['foldername'])
        files = {
        'userid': (None, album_name),
        }
        response = requests.post('http://127.0.0.1:5000/getimagedetails', files=files)
        api_values = response.json()
        s3_client, s3_resource,bucket = get_connection()
        final_path='temp/getimages/'
        os.makedirs(final_path+album_name, exist_ok=True)        
        allimages = getAllImages(bucket,album_name)
        downloads3getimages(bucket,album_name,final_path)
        img_list =os.listdir(final_path+album_name+'/')
        frontend_images = []
        for images in img_list:
            image_url = final_path+album_name+'/'
            final_url = image_url+str(images)                    
            frontend_images.append(final_url)
        if album_name in temp:
            temp[album_name].append(frontend_images)
        else:
            temp[album_name]=frontend_images
        print(temp)             
        return render(request,'images.html',{'images':temp})

    return render(request,'getimagedetails.html')

def  getAllImages(bucket,folder):
    return_arr=[]
    for object in tqdm(bucket.objects.filter(Prefix = folder)):
        if object.key != folder:
            return_arr.append(object.key)
    return return_arr

def groupimages(request):
    temp = {}
    temp['id'] = []
    frontend_images = []
    folder='temp/'
    if request.method == 'POST':
        album_name = str(request.POST['foldername'])
        folder+=album_name
        folder+='/cluster'
        cluster = 1
        files = {
        'userid': (None, album_name),
        }
        userid=album_name+'/'
        response = requests.post('http://127.0.0.1:5000/groupalbum',files=files)
        api_values = response.json()
        s3_client, s3_resource,bucket = get_connection()
        for value in api_values:
            folder_path = folder
            folder_path+=str(cluster)
            imgdata = base64.b64decode(value['identity'])
            filename = value['cluster']
            identity_image_name = 'id'+str(cluster)+'.jpg'
            length = len(filename)
            identity_path = folder_path+'/'
            for index in range(length):
                final_path = identity_path
                id_path = folder_path+'/'+identity_image_name
                if not os.path.exists(os.path.dirname(final_path)):
                    os.makedirs(os.path.dirname(final_path))
                userid=album_name+"/"
                print(final_path)
                downloadDirectoryFroms3(bucket,userid,final_path,filename[index])  
                frontend_images = []
                with open(id_path, "wb") as f:
                    f.write(imgdata)
                img_list = os.listdir(final_path)
                for images in img_list:
                    if 'id' in str(images):
                        image_url = '127.0.0.1/8000/temp/'+userid+'cluster'+str(cluster)+'/'
                        final_url = image_url+str(images)
                        frontend_path = final_path+str(images)
                        temp['id'].append(frontend_path)
                temp['id'] = (list(set(temp['id'])))        
                frontend_images = []

                for images in img_list:
                    if 'id' not in str(images):
                        image_url = '127.0.0.1/8000/temp/'+userid+'cluster'+str(cluster)+'/'
                        final_url = image_url+str(images)
                        frontend_path = final_path+str(images)                    
                        frontend_images.append(frontend_path)
                cluster_key = 'cluster'+str(cluster)
            if cluster_key in temp:
                temp[cluster_key].append(frontend_images)
            else:
                temp[cluster_key]=frontend_images    
            cluster+=1 
        print(temp)        
        return render(request,'images.html',{'temp':temp})                   
    return render(request,'groupingimages.html' )

def imageupload(request):
    if request.method == 'POST':
        album_name = request.POST['foldername']
        image = request.FILES['images']
        title = image.name
        files = {
        'userid': (None, album_name),
        'image': (image)
        }
        response = requests.post('http://127.0.0.1:5000/addphoto', files=files)
        
    return render(request,'imageupload.html')
def cluster(request):
    return render(request,'cluster.html')    
