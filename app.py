from flask import Flask, render_template, request
from azure.cognitiveservices.vision.computervision import ComputerVisionClient
from azure.cognitiveservices.vision.computervision.models import OperationStatusCodes
from msrest.authentication import CognitiveServicesCredentials
import time
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

# Variables
subscription_key = os.getenv('subscription_key')
endpoint = os.getenv('endpoint')

computervision_client = ComputerVisionClient(endpoint, CognitiveServicesCredentials(subscription_key))

def extractTextFromImage(read_image_url):
	read_response  = computervision_client.read(read_image_url ,  raw=True)

	result = ''
	# Get the operation location (URL with an ID at the end) from the response
	read_operation_location = read_response.headers["Operation-Location"]
	# Grab the ID from the URL
	operation_id = read_operation_location.split("/")[-1]
	
	# Call the "GET" API and wait for it to retrieve the results 
	while True:
		read_result = computervision_client.get_read_result(operation_id)
		if read_result.status not in ['notStarted', 'running']:
			break
		time.sleep(1)

	# Add the detected text to result, line by line
	if read_result.status == OperationStatusCodes.succeeded:
		for text_result in read_result.analyze_result.read_results:
			for line in text_result.lines:
				result = result + " " + line.text
	return result

# routes
@app.route("/", methods=['GET', 'POST'])
def main():
	return render_template("index.html")


@app.route("/submit", methods = ['GET', 'POST'])
def get_output():
	if request.method == 'POST':
		image_url = request.form.get('image_url')

	result = extractTextFromImage(image_url)

	return render_template("index.html", prediction = result, img_path = image_url)

