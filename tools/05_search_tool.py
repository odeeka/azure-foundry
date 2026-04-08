import os
from dotenv import load_dotenv
from azure.identity import DefaultAzureCredential

load_dotenv(override=True)

# Azure AI Search settings
search_endpoint = os.getenv("SEARCH_ENDPOINT")
search_index = os.getenv("SEARCH_INDEX_NAME")

# Azure OpenAI settings (for RAG)
aoai_endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
aoai_deployment = os.getenv("AZURE_OPENAI_DEPLOYMENT")

# Single credential for all services
credential = DefaultAzureCredential()

print("Search Endpoint:", search_endpoint)
print("Index Name:", search_index)
print("OpenAI Endpoint:", aoai_endpoint)

# Create search index client and define the index schema
import time
from azure.search.documents.indexes import SearchIndexClient
from azure.search.documents.indexes.models import (
    SearchIndex, SimpleField, SearchableField, SearchFieldDataType,
    SemanticConfiguration, SemanticSearch, SemanticField, SemanticPrioritizedFields,
)
from azure.search.documents import SearchClient as UploadClient

# Define the index schema
index_name = search_index
index_client = SearchIndexClient(endpoint=search_endpoint, credential=credential)

fields = [
    SimpleField(name="id", type=SearchFieldDataType.String, key=True, filterable=True),
    SearchableField(name="title", type=SearchFieldDataType.String, filterable=True, sortable=True),
    SearchableField(name="content", type=SearchFieldDataType.String),
    SimpleField(name="category", type=SearchFieldDataType.String, filterable=True, facetable=True),
]

semantic_config = SemanticConfiguration(
    name="my-semantic-config",
    prioritized_fields=SemanticPrioritizedFields(
        content_fields=[SemanticField(field_name="content")],
        title_field=SemanticField(field_name="title"),
    ),
)

index = SearchIndex(
    name=index_name,
    fields=fields,
    semantic_search=SemanticSearch(configurations=[semantic_config]),
)

result = index_client.create_or_update_index(index)
print(f"Index created: {result.name}")

# Upload sample documents
upload_client = UploadClient(endpoint=search_endpoint, index_name=index_name, credential=credential)

documents = [
    {
        "id": "1",
        "title": "Introduction to Machine Learning",
        "content": (
            "Machine learning is a subset of artificial intelligence that enables "
            "systems to learn and improve from experience. It uses algorithms to "
            "parse data, learn from it, and make decisions. Applications include "
            "image recognition, natural language processing, recommendation systems, "
            "and autonomous vehicles."
        ),
        "category": "Technology",
    },
    {
        "id": "2",
        "title": "Cloud Computing Fundamentals",
        "content": (
            "Cloud computing delivers computing services over the internet including "
            "servers, storage, databases, networking, software, and analytics. The key "
            "benefits are cost reduction, scalability, performance, reliability, and "
            "security. Major providers include Microsoft Azure, Amazon Web Services, "
            "and Google Cloud Platform."
        ),
        "category": "Technology",
    },
    {
        "id": "3",
        "title": "Sustainable Energy Solutions",
        "content": (
            "Sustainable energy encompasses solar, wind, hydroelectric, and geothermal "
            "power sources. These renewable energy technologies are crucial for reducing "
            "greenhouse gas emissions and combating climate change. Investment in clean "
            "energy has grown significantly in recent years."
        ),
        "category": "Science",
    },
    {
        "id": "4",
        "title": "Modern Software Development Practices",
        "content": (
            "Agile methodologies, DevOps, and continuous integration have transformed "
            "software development. Teams now deploy code multiple times a day using "
            "automated pipelines. Containerization with Docker and orchestration with "
            "Kubernetes enable reliable deployments across cloud environments."
        ),
        "category": "Technology",
    },
    {
        "id": "5",
        "title": "Data Privacy and Security",
        "content": (
            "Data privacy regulations like GDPR and CCPA require organizations to protect "
            "personal information. Security best practices include encryption, access "
            "controls, regular audits, and employee training. Zero-trust architecture is "
            "becoming the standard approach to enterprise security."
        ),
        "category": "Security",
    },
]

upload_result = upload_client.upload_documents(documents=documents)
succeeded = sum(1 for r in upload_result if r.succeeded)
print(f"Uploaded {succeeded}/{len(documents)} documents")

# Automatically update .env with the index name so Step 4 picks it up
env_path = os.path.join(os.path.dirname(os.path.abspath("__file__")), ".env")
with open(env_path, "r", encoding="utf-8") as f:
    env_content = f.read()

if 'SEARCH_INDEX_NAME=""' in env_content:
    env_content = env_content.replace('SEARCH_INDEX_NAME=""', f'SEARCH_INDEX_NAME="{index_name}"')
elif "SEARCH_INDEX_NAME=" in env_content:
    import re
    env_content = re.sub(r'SEARCH_INDEX_NAME="[^"]*"', f'SEARCH_INDEX_NAME="{index_name}"', env_content)
else:
    env_content += f'\nSEARCH_INDEX_NAME="{index_name}"\n'

with open(env_path, "w", encoding="utf-8") as f:
    f.write(env_content)

print(f"\n.env updated: SEARCH_INDEX_NAME=\"{index_name}\"")

# Allow a few seconds for the index to process the documents
time.sleep(3)
print("Index is ready — proceed to Step 4.")

# Search client example: run a simple search query to verify everything is working
from azure.search.documents import SearchClient

# Reload .env to pick up SEARCH_INDEX_NAME written by Step 3
load_dotenv(override=True)
search_index = os.getenv("SEARCH_INDEX_NAME")

# Fallback: if the .env value is still empty, use the variable from Step 3
if not search_index:
    search_index = index_name  # defined in Step 3
    print(f"(Using index_name from Step 3: '{search_index}')")

search_client = SearchClient(
    endpoint=search_endpoint,
    index_name=search_index,
    credential=credential,
)
print(f"Search client connected to index '{search_index}'")

# Run a full-text search query
query = "machine learning applications"

results = search_client.search(
    search_text=query,
    top=5,                       # Return the top 5 results
    include_total_count=True,    # Include the total number of matches
)

print(f"\nSearch: '{query}'")
print(f"Total matches: {results.get_count()}\n")

for i, result in enumerate(results, start=1):
    score = result.get("@search.score", "N/A")
    print(f"  {i}. [Score: {score}]")
    for key, value in result.items():
        if not key.startswith("@"):
            display_val = str(value)[:120]
            print(f"     {key}: {display_val}")
    print()

# Filtered search
# Filter to only Technology articles
filter_expression = "category eq 'Technology'"

filtered_results = search_client.search(
    search_text="cloud computing",
    filter=filter_expression,
    top=3,
)

print(f"Filtered search (category = 'Technology'):")
for i, result in enumerate(filtered_results, start=1):
    score = result.get("@search.score", "N/A")
    print(f"  {i}. [Score: {score}]")
    for key, value in result.items():
        if not key.startswith("@"):
            display_val = str(value)[:120]
            print(f"     {key}: {display_val}")
    print()

# Retrievel Augmented Generation (RAG) example: use search results to generate a response with OpenAI
from openai import AzureOpenAI
from azure.identity import DefaultAzureCredential, get_bearer_token_provider

# Create a token provider for the OpenAI client
token_provider = get_bearer_token_provider(
    DefaultAzureCredential(),
    "https://cognitiveservices.azure.com/.default",
)

# Create the Azure OpenAI client using Entra ID
openai_client = AzureOpenAI(
    api_version="2024-12-01-preview",
    azure_endpoint=aoai_endpoint,
    azure_ad_token_provider=token_provider,
)

# For the data source, we also need a bearer token for the search service
search_token = credential.get_token("https://search.azure.com/.default").token

# Configure the search index as a data source for RAG
rag_config = {
    "data_sources": [
        {
            "type": "azure_search",
            "parameters": {
                "endpoint": search_endpoint,
                "index_name": search_index,
                "authentication": {
                    "type": "access_token",
                    "access_token": search_token,
                },
            },
        }
    ],
}

# Ask a question -- the model will search the index for relevant
# documents and use them to formulate its answer
user_question = "What are the key benefits of cloud computing?"

rag_response = openai_client.chat.completions.create(
    messages=[
        {"role": "user", "content": user_question},
    ],
    max_tokens=4096,
    temperature=0.7,
    model=aoai_deployment,
    extra_body=rag_config,
)

print(f"Question: {user_question}\n")
print(f"RAG Answer:\n{rag_response.choices[0].message.content}")
