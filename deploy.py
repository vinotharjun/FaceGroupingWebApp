from flask import Flask, redirect, render_template, request, session, url_for
from PIL import Image
import json
from makegroups import *
import os
from flask import jsonify
app = Flask(__name__)


#create album route
@app.route("/createalbum", methods=['GET', 'POST'])
def create_album():
    id= request.form['userid']
    if not id:
        return jsonify({"info":"userid is required"})
    result = do_process_create(id)
    return jsonify(result)
#add photo route
@app.route("/addphoto",methods=["GET","POST"])
def add_photo():
    try:
        id= request.form['userid']
        if not id:
            return jsonify({"info":"userid is required"})
        if "image" not in request.files:
            return jsonify({"info" : "image is required"})
        files = request.files.getlist("image")
        for file in files:
            if file.filename=="":
                return jsonify("Please select a file")
            output = do_process_addphoto(id,file,file.filename)
        return jsonify(output)
    except Exception as e:
        print("error in app.py line 31",e)
        return jsonify({"error":"something went wrong in file uploading"})
    return jsonify({"error":"something went wrong"})

#group album route
@app.route('/groupalbum', methods=['GET', 'POST'])
def group_album():
    id= request.form['userid']
    print(id)
    if not id:
        return jsonify({"info":"userid is required"})
    result=do_process_group(id)
    return jsonify(result)
    
@app.route("/getimagedetails",methods=["GET","POST"])
def fetch_details():
    id =request.form["userid"]
    if not id:
        return jsonify({"info":"userid is required"})
    result = do_process_fetch_images(id)
    return jsonify(result)
if __name__ == '__main__':
    app.run(threaded=False)




  