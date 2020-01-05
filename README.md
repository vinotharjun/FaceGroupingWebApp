#                    CLUSTER IMAGES


### INITIAL SETUP:
* Start the API through cd API FOLDER. 
``` 
py deploy.py
```
* Now after starting the API cd to DJANGO PROJECT.
* pip install requirements.txt.
* After installing the needed dependencies run the command.
```
py manage.py runserver or python manage.py runserver
```
* Now go to localhost:8000.
#### Navlinks And Their Functionalities:
1. ##### Folder Creation
    * Type the name of the folder name inside the Create Album. Card
    * Click create to a folder inside the Phosphene-Users Bucket.
2. ##### Image Upload
    * Type the foldername[existing folder inside bucket] to which you want to push the image.
    * Click the browse button and select the required image.
    * Now press the Create Button to store the image to folder specified inside the bucket.
3. ##### Grouping Images
    * Inside the Grouping Images Card Enter the name of the existing cluster name.
    * Click the Show Group Button to view the Clusters.
    * Clicking on the thumbnails will display the cluster for the particular group.
4. #### Get Image Details
    * Inside the Get Images Card enter the name to view all the images inside it.
    * Click Get Files Button.
    * All the images inside specified folder will be displayed.    
