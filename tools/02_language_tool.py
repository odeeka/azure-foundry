import os
from dotenv import load_dotenv
from azure.ai.textanalytics import TextAnalyticsClient
from azure.identity import DefaultAzureCredential

load_dotenv(override=True)

language_endpoint = os.getenv("LANGUAGE_ENDPOINT")

if not language_endpoint:
    raise ValueError("LANGUAGE_ENDPOINT must be set.")


def print_section(title):
    print(f"\n{title}")
    print("-" * len(title))


def show_language_detection_examples(client):
    multilingual_samples = [
        "Good morning team, the deployment finished successfully overnight.",
        "A felhasznaloi visszajelzesek alapjan egyszerubb bejelentkezesi folyamatra van szukseg.",
        "La nueva version reduce el tiempo de respuesta de la API.",
        "Bonjour, nous devons planifier la migration avant vendredi.",
    ]

    print_section("Language Detection")
    detection_results = client.detect_language(documents=multilingual_samples)

    for doc, result in zip(multilingual_samples, detection_results):
        print(f"Text: {doc}")
        print(
            f"  -> Language: {result.primary_language.name} "
            f"(confidence: {result.primary_language.confidence_score:.0%})"
        )


def show_key_phrase_examples(client):
    tech_paragraph = [
        "Our platform team migrated the order processing service to Azure Kubernetes Service, "
        "moved session state into Azure Cache for Redis, and added Application Insights dashboards "
        "to track latency, failed requests, and deployment health after each release."
    ]

    print_section("Key Phrase Extraction")
    kp_results = client.extract_key_phrases(documents=tech_paragraph)

    print("Key phrases found:")
    for phrase in kp_results[0].key_phrases:
        print(f"  - {phrase}")


def show_sentiment_examples(client):
    review_samples = [
        "The onboarding experience was excellent, and the setup guide was clear from start to finish.",
        "The dashboard looks nice, but report generation is still too slow during peak hours.",
        "The maintenance window started at 10 PM and ended exactly when the status page promised.",
    ]

    print_section("Sentiment Analysis")
    sentiment_results = client.analyze_sentiment(documents=review_samples)

    for doc, result in zip(review_samples, sentiment_results):
        print(f"Sentiment: {result.sentiment.upper():>8}  |  {doc}")


def show_entity_examples(client):
    news_snippets = [
        "On 12 March 2026, Contoso opened a new engineering office in Berlin and announced a strategic collaboration with Microsoft to expand its Azure-based analytics platform across Europe."
    ]

    print_section("Named Entity Recognition")
    ner_results = client.recognize_entities(documents=news_snippets)

    print(f"{'Entity':<25} {'Category':<18} {'Confidence'}")
    print("-" * 60)
    for entity in ner_results[0].entities:
        print(f"{entity.text:<25} {entity.category:<18} {entity.confidence_score:.0%}")

# Authenticate via Entra ID (uses az login credentials)
credential = DefaultAzureCredential()

ta_client = TextAnalyticsClient(
    endpoint=language_endpoint,
    credential=credential,
)

print("Endpoint:", language_endpoint)
print("Client ready:", ta_client is not None)

show_language_detection_examples(ta_client)
show_key_phrase_examples(ta_client)
show_sentiment_examples(ta_client)
show_entity_examples(ta_client)