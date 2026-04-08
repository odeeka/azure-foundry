# os lets us read environment variables from the system
import os

# base64 lets us decode the image data returned by the API
import base64

# requests lets us make HTTP calls to the FLUX endpoint
import requests

# load_dotenv reads your .env file and sets each line as an environment variable
from dotenv import load_dotenv

# DefaultAzureCredential automatically picks the best way to authenticate with Azure
from azure.identity import DefaultAzureCredential

# IPython.display lets us show images directly in a Jupyter notebook
from IPython.display import Image, display

# Load the .env file so os.getenv() can find our settings
load_dotenv()

# The Target URI from the FLUX deployment page (e.g. https://your-resource.cognitiveservices.azure.com)
# Important: this is NOT the project endpoint -- copy it from the deployment details page
my_endpoint = os.getenv("FOUNDRY_RESOURCE_ENDPOINT")

# The name of the FLUX.1-Kontext-pro deployment in your Foundry project
my_image_model = os.getenv("IMAGE_MODEL_DEPLOYMENT_NAME")

print(f"Endpoint: {my_endpoint}")
print(f"Image model: {my_image_model}")

# Create a credential object that automatically detects how you are logged in
credential = DefaultAzureCredential()

# Request a bearer token scoped to Azure Cognitive Services
# This is the scope required for calling Foundry model endpoints
token = credential.get_token("https://cognitiveservices.azure.com/.default")

print("Authentication successful -- bearer token acquired.")

# The API version required for image generation with FLUX models
api_version = "2025-04-01-preview"

# Build the full URL for the image generation endpoint
generation_url = (
    f"{my_endpoint}/openai/deployments/{my_image_model}"
    f"/images/generations?api-version={api_version}"
)

# These headers are sent with every request
# - Authorization: proves who we are using the bearer token
# - Content-Type: tells the API we are sending JSON
headers = {
    "Authorization": f"Bearer {token.token}",
    "Content-Type": "application/json",
}

print(f"API URL ready: .../{my_image_model}/images/generations")

# The text description of the image we want to create
first_prompt = (
    "A cozy mountain cabin at dusk in a dense pine forest, with warm light "
    "glowing through the windows, fresh snow on the roof, and a narrow path "
    "lit by small lanterns leading to the front door."
)

# Build the request body
# - prompt: the text description
# - n: how many images to generate (1 in our case)
# - size: the output resolution
# - output_format: the file format (png or jpeg)
request_body = {
    "prompt": first_prompt,
    "n": 1,
    "size": "1024x1024",
    "output_format": "png",
}

# Send the request to the FLUX endpoint
print("Generating image... (this may take a few seconds)")
response = requests.post(generation_url, headers=headers, json=request_body)

# Check if the request succeeded
response.raise_for_status()
result = response.json()

print("Image generated successfully!")

# Extract the base64-encoded image from the response
# The response format is: {"data": [{"b64_json": "..."}]}
b64_image_data = result["data"][0]["b64_json"]

# Decode the base64 string into raw image bytes
image_bytes = base64.b64decode(b64_image_data)

# Save the image to a local file
first_filename = "mountain_cabin_dusk.png"
with open(first_filename, "wb") as f:
    f.write(image_bytes)

print(f"Image saved: {os.path.abspath(first_filename)}")

# Display the image inline in the notebook
display(Image(filename=first_filename))

# A second prompt to test the model's versatility
second_prompt = (
    "A futuristic street food market in Tokyo during light rain, with neon "
    "signs reflected on wet pavement, steam rising from ramen stalls, and "
    "crowds carrying transparent umbrellas."
)

# Build the request body for the second image
second_body = {
    "prompt": second_prompt,
    "n": 1,
    "size": "1024x1024",
    "output_format": "png",
}

# Send the request
print("Generating second image...")
second_response = requests.post(generation_url, headers=headers, json=second_body)
second_response.raise_for_status()
second_result = second_response.json()

# Decode and save
second_bytes = base64.b64decode(second_result["data"][0]["b64_json"])
second_filename = "tokyo_night_market.png"
with open(second_filename, "wb") as f:
    f.write(second_bytes)

print(f"Image saved: {os.path.abspath(second_filename)}")

# Display the image
display(Image(filename=second_filename))
