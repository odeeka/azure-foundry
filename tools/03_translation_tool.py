import os
import requests
from dotenv import load_dotenv
from azure.identity import DefaultAzureCredential

load_dotenv(override=True)

translator_endpoint = os.getenv("TRANSLATOR_ENDPOINT")
translator_region = os.getenv("TRANSLATOR_REGION")

if not translator_endpoint or not translator_region:
    raise ValueError(
        "TRANSLATOR_ENDPOINT and TRANSLATOR_REGION must be set in tools/.env."
    )

translator_endpoint = translator_endpoint.rstrip("/") + "/"

if "api.cognitive.microsofttranslator.com" in translator_endpoint:
    raise ValueError(
        "TRANSLATOR_ENDPOINT is pointing to the global Translator endpoint. "
        "This script expects the custom-domain endpoint of your Azure AI Translator resource, "
        "for example https://<account-name>.cognitiveservices.azure.com/. "
        "Update tools/.env from the Terraform output translator_endpoint."
    )

# Obtain a bearer token from Entra ID
credential = DefaultAzureCredential()
token = credential.get_token("https://cognitiveservices.azure.com/.default").token

# Common headers for every Translator REST call
headers = {
    "Authorization": f"Bearer {token}",
    "Content-Type": "application/json",
    "Ocp-Apim-Subscription-Region": translator_region,
}

print("Endpoint:", translator_endpoint)
print("Region:", translator_region)
print("Token obtained:", "Yes" if token else "No")

# Build the request URL
translate_url = f"{translator_endpoint}translator/text/v3.0/translate"

# Source text in English
original_text = "Our support team resolved the production issue and restored the service within fifteen minutes."

response = requests.post(
    translate_url,
    headers=headers,
    params={"from": "en", "to": "hu", "api-version": "3.0"},
    json=[{"Text": original_text}],
)
response.raise_for_status()
result = response.json()

translated = result[0]["translations"][0]["text"]
print(f"Original (en):    {original_text}")
print(f"Translated (hu):  {translated}")

# Translate multiple languages
source_sentence = "The analytics dashboard now shows real-time inventory updates for every warehouse."

multi_response = requests.post(
    translate_url,
    headers=headers,
    params={"from": "en", "to": ["es", "de", "ja", "pt", "hu"], "api-version": "3.0"},
    json=[{"Text": source_sentence}],
)
multi_response.raise_for_status()
multi_result = multi_response.json()

print(f"Original (en):  {source_sentence}\n")
for translation in multi_result[0]["translations"]:
    print(f"  [{translation['to']}]  {translation['text']}")

# Autodetection
# A sentence in Italian -- we won't tell the API what language it is
mystery_text = "Il team ha completato la migrazione dei dati senza interrompere il servizio."

auto_response = requests.post(
    translate_url,
    headers=headers,
    params={"to": "en", "api-version": "3.0"},   # no 'from' -- auto-detect
    json=[{"Text": mystery_text}],
)
auto_response.raise_for_status()
auto_result = auto_response.json()

detected = auto_result[0]["detectedLanguage"]
translated_text = auto_result[0]["translations"][0]["text"]

print(f"Original:          {mystery_text}")
print(f"Detected language: {detected['language']} (confidence: {detected['score']:.0%})")
print(f"English:           {translated_text}")
