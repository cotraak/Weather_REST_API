# WEATHER REST API

List of commands used are:

Forecast:
GET request: /forecast/{DATE}
Input: DATE (string)
Output: Json containing list of seven days data with status code
Status code: 200 OK is returned

GET request: /historical/{DATE}
Input: DATE (string)
Output: json containing {DATE, TMAX, TMIN} 
Status code: 202 OK is returned along with json if DATE is found or else 404 is returned.

GET request for retreiving the whole data information: /historical/
Input: No input is given
Output: provides a list of all dates
status code: 200 OK is returned

DELETE request: /historical/{DATE}
Input: DATE (string)
Output: status code 
status code: 204 is returned

POST request /historical
Input: Json which contains DATE, TMAX, TMIN
Output: Json along with status code
Status code: 201

# Plotting the forecast

Forecasted the plot by creating a dynamic web page which consists of a form that takes date as an input. 

Output: Displays the plot for the next 6 days including the given date.

# Docker

Also, a docker image is built for this application in the following manner

The Web Service is ported into a docker container instance which is done on an Amazon AWS Ubuntu instance.

Installation:
sudo apt-get install docker.io

Created a docker hub account and then logged into docker with the docker hub account
Commands to login to docker:
sudo docker login -u alekhya315
And then the prompt asks for the user to enter the account password.
And then the login is succeeded if the password is given correctly.

Created a Dockerfile and requirements.txt file in the root directory.
 
Dockerfile is the one which is used for creating the images.

requirements.txt file contains all the packages that need to be installed while building the image.

Built the docker container using:
sudo docker build -t wf_img . 

Command for testing the image built:
sudo docker run -d --name wf_image -p 80:80 wf_img

Commit:
sudo docker commit d3b4683ee75d alekhya315/d3b4683ee75d

Once the commit is done, the user needs to login to the docker once again so as to push back the image to the repository for future use.
Command for pushing the image:
sudo docker push alekhya315/d3b4683ee75d

