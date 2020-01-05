#imports 
from PIL import Image
import numpy as np
import matplotlib.pyplot as plt
from mtcnn.mtcnn import MTCNN
import os
import base64
from sklearn.preprocessing import scale
from tqdm import tqdm
from numpy import dot
from numpy.linalg import norm
import time
import tensorflow as tf
import pprint
import uuid
from keras.models import load_model
import boto3
import os

# def init(PATH="./keras-facenet/model/weigths/facenet_keras_weights.h5"):
#     global models
#     models = {}
#     for idx, model_path in enumerate(model_paths):
#         with open(model_path, "r") as fp:
#             model = model_from_json(json.load(fp))
#             model.compile(loss='mean_absolute_error', optimizer='adam')
#             model.load_weights(PATH)
#             models[idx] = model
#     global graph
#     graph = tf.get_default_graph()
#loading the model from keras-facenet folder
#graph = tf.get_default_graph()
graph=tf.Graph()
model = load_model('./keras-facenet/model/facenet_keras.h5')
#MTCNN loading 
detector = MTCNN()
#function to extract all faces from the single photograph
def extract_faces(filename, required_size=(160, 160)):
    global detector
    faces=[]
    image = Image.open(filename)
    image = image.convert('RGB')
    pixels = np.asarray(image)
    results = detector.detect_faces(pixels)
    if len(results)==0:
        return faces
    for i in range(len(results)):
        x1, y1, width, height = results[i]['box']
        x1, y1 = abs(x1), abs(y1)
        x2, y2 = x1 + width, y1 + height
        face = pixels[y1:y2, x1:x2]
        image = Image.fromarray(face)
        image = image.resize(required_size)
        faces.append(np.asarray(image))
    return faces
#function to get 128 dimentional embedding for single face image
def get_embedding(model, face_pixels):
    try:
        face_pixels = face_pixels.astype('float32')
        mean, std = face_pixels.mean(axis=(1,2),keepdims=True),face_pixels.std(axis=(0,1),keepdims=True)
        face_pixels = (face_pixels - mean) / std
        yhat = model.predict(face_pixels)
        return yhat
    except Exception as e:
        print("error in line 66 utils.py",e)
#function to load all data from the given folder
def load_data(folder):
    global model
    global graph
    print(graph)
    all_faces=[]
    
    for filename in tqdm(os.listdir(folder)):
        path = folder+"/" + filename
        try:
            # with graph.as_default() as graph:
                faces = extract_faces(path)
                if len(faces)>0:
                    y_hat=get_embedding(model,np.asarray(faces))
                else:
                    y_hat= []
                all_faces.append({"id":filename,"face_list":faces,"face_embeddings":y_hat,"count":len(faces)})
        except Exception as e:
                 print("error in reading files",str(e))

    return all_faces

def get_cosine_distance(a,b):
    if type(a) == list or type(b)== list:
        return -1
    else:
        return dot(a, b)/(norm(a)*norm(b))

def do_cluster(all_faces):
    group_list=[]
    for image in all_faces:
        if len(group_list)==0:
            for embedding in image["face_embeddings"]:
                i,j= np.where(image["face_embeddings"]==embedding)      
                group_list.append({
                "images":[image["id"]],
                "center":embedding,
                "identity":image["face_list"][i[0]]
                   })
        else:
            if len(image["face_embeddings"])==0:
                group_list.append({
                    "images":[image["id"]],
                    "center":[],
                    "identity":None
                })
            else: 
                for embedding in image["face_embeddings"]:
                    i,j= np.where(image["face_embeddings"]==embedding)     
                    it=0
                    length=len(group_list)
                    matched=False
                    while it<length:
                        distance=get_cosine_distance(embedding,group_list[it]["center"])
                        if distance>0.7:
                           # group_list[it]["center"]=embedding
                            matched=True
                            group_list[it]["images"].append(image["id"])
                        it=it+1
                    if matched==False:  
                           group_list.append({
                             "images":[image["id"]],
                                  "center":embedding,
                               "identity":image["face_list"][i[0]]
                            })
    return group_list

        
def convert_base64(imagefile):
    try:
        with open(imagefile, "rb") as image_file:
            encoded_string = base64.b64encode(image_file.read())
            encoded_string=str(encoded_string, "utf-8")
        return encoded_string
    except Exception as e:
        print(e)
        return "404"

def do_grouping(folder="./temp/"):
    res=[]
    all_faces=load_data(folder)
    result = do_cluster(all_faces)
    for i in range(len(result)):
        arr = result[i]["identity"]
        if arr is not None:
            img = Image.fromarray(arr.astype('uint8'))
            name=folder+str(i)+str(uuid.uuid1())+".png"
            img.save(name)
            encoded_string= convert_base64(name)
            # result[i]["images"].insert(0,encoded_string)
            res.append({"cluster":result[i]["images"],"identity":encoded_string})
    # print(len(res))
    return res


# pprint.pprint(do_grouping("./temp4/"))
