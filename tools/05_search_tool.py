import os
import re
import time

from dotenv import load_dotenv
from azure.identity import DefaultAzureCredential, get_bearer_token_provider
from azure.search.documents import SearchClient
from azure.search.documents.indexes import SearchIndexClient
from azure.search.documents.indexes.models import (
    SearchIndex, SimpleField, SearchableField, SearchFieldDataType,
    SemanticConfiguration, SemanticSearch, SemanticField, SemanticPrioritizedFields,
)
from openai import AzureOpenAI

load_dotenv(override=True)

# Azure AI Search settings
search_endpoint = os.getenv("SEARCH_ENDPOINT")
search_index = os.getenv("SEARCH_INDEX_NAME")

# Azure OpenAI settings (for RAG)
aoai_endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
aoai_deployment = os.getenv("AZURE_OPENAI_DEPLOYMENT")

if not search_endpoint:
    raise ValueError("SEARCH_ENDPOINT must be set in tools/.env.")
if not aoai_endpoint or not aoai_deployment:
    raise ValueError("AZURE_OPENAI_ENDPOINT and AZURE_OPENAI_DEPLOYMENT must be set in tools/.env.")

# Single credential reused for all services
credential = DefaultAzureCredential()

print("Search Endpoint:", search_endpoint)
print("Index Name:", search_index)
print("OpenAI Endpoint:", aoai_endpoint)


DOCUMENTS = [
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


def create_index_and_upload(index_name: str) -> None:
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

    upload_client = SearchClient(endpoint=search_endpoint, index_name=index_name, credential=credential)
    upload_result = upload_client.upload_documents(documents=DOCUMENTS)
    succeeded = sum(1 for r in upload_result if r.succeeded)
    print(f"Uploaded {succeeded}/{len(DOCUMENTS)} documents")

    # Write the index name back to .env so subsequent runs pick it up automatically
    env_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env")
    with open(env_path, "r", encoding="utf-8") as f:
        env_content = f.read()
    env_content = re.sub(r'SEARCH_INDEX_NAME="[^"]*"', f'SEARCH_INDEX_NAME="{index_name}"', env_content)
    with open(env_path, "w", encoding="utf-8") as f:
        f.write(env_content)
    print(f'.env updated: SEARCH_INDEX_NAME="{index_name}"')

    # Allow a few seconds for the index to process the uploaded documents
    time.sleep(3)
    print("Index is ready.")


def run_search(index_name: str) -> None:
    search_client = SearchClient(endpoint=search_endpoint, index_name=index_name, credential=credential)

    # Full-text search
    query = "machine learning applications"
    results = search_client.search(search_text=query, top=5, include_total_count=True)
    print(f"\nSearch: '{query}'")
    print(f"Total matches: {results.get_count()}\n")
    for i, result in enumerate(results, start=1):
        score = result.get("@search.score", "N/A")
        print(f"  {i}. [Score: {score}]")
        for key, value in result.items():
            if not key.startswith("@"):
                print(f"     {key}: {str(value)[:120]}")
        print()

    # Filtered search
    filtered_results = search_client.search(
        search_text="cloud computing",
        filter="category eq 'Technology'",
        top=3,
    )
    print("Filtered search (category = 'Technology'):")
    for i, result in enumerate(filtered_results, start=1):
        score = result.get("@search.score", "N/A")
        print(f"  {i}. [Score: {score}]")
        for key, value in result.items():
            if not key.startswith("@"):
                print(f"     {key}: {str(value)[:120]}")
        print()


def run_rag(index_name: str) -> None:
    # RAG (Retrieval-Augmented Generation): the model queries the Search index for
    # relevant documents and uses them as grounding context for its answer.
    # The extra_body "data_sources" field is the Azure OpenAI "on your data" extension.
    token_provider = get_bearer_token_provider(credential, "https://cognitiveservices.azure.com/.default")
    openai_client = AzureOpenAI(
        api_version="2024-12-01-preview",
        azure_endpoint=aoai_endpoint,
        azure_ad_token_provider=token_provider,
    )

    # A separate bearer token is forwarded to the Search service so it can execute
    # the retrieval step on behalf of the OpenAI request.
    search_token = credential.get_token("https://search.azure.com/.default").token

    rag_config = {
        "data_sources": [
            {
                "type": "azure_search",
                "parameters": {
                    "endpoint": search_endpoint,
                    "index_name": index_name,
                    "authentication": {
                        "type": "access_token",
                        "access_token": search_token,
                    },
                },
            }
        ],
    }

    user_question = "What are the key benefits of cloud computing?"
    rag_response = openai_client.chat.completions.create(
        messages=[{"role": "user", "content": user_question}],
        max_tokens=4096,
        temperature=0.7,
        model=aoai_deployment,
        extra_body=rag_config,
    )

    print(f"Question: {user_question}\n")
    print(f"RAG Answer:\n{rag_response.choices[0].message.content}")


# Use the index name from .env; fall back to a default for first-time runs
index_name = search_index or "foundry-index"

create_index_and_upload(index_name)
run_search(index_name)
run_rag(index_name)
