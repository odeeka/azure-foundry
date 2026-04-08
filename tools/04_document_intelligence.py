import os
from dotenv import load_dotenv
from azure.ai.documentintelligence import DocumentIntelligenceClient
from azure.identity import DefaultAzureCredential
from azure.ai.documentintelligence.models import AnalyzeDocumentRequest, AnalyzeResult

load_dotenv(override=True)

doc_endpoint = os.getenv("DOCUMENT_INTELLIGENCE_ENDPOINT")

# Authenticate via Entra ID (uses az login credentials)
credential = DefaultAzureCredential()

doc_client = DocumentIntelligenceClient(
    endpoint=doc_endpoint,
    credential=credential,
)

print("Endpoint:", doc_endpoint)
print("Client ready:", doc_client is not None)

# Extract text from image
# A publicly available sample image from Azure documentation
pdf_url = "https://raw.githubusercontent.com/Azure-Samples/cognitive-services-REST-api-samples/master/curl/form-recognizer/rest-api/read.png"

# Send the document for analysis
poller = doc_client.begin_analyze_document(
    "prebuilt-read",
    AnalyzeDocumentRequest(url_source=pdf_url),
)
read_result: AnalyzeResult = poller.result()

# Print each paragraph the service found
print(f"Found {len(read_result.paragraphs)} paragraph(s):\n")
for i, para in enumerate(read_result.paragraphs, start=1):
    print(f"Paragraph {i}: {para.content}\n")

# Extract invoice data from a sample document
# Sample invoice from Azure documentation
invoice_url = "https://raw.githubusercontent.com/Azure-Samples/cognitive-services-REST-api-samples/master/curl/form-recognizer/sample-invoice.pdf"

invoice_poller = doc_client.begin_analyze_document(
    "prebuilt-invoice",
    AnalyzeDocumentRequest(url_source=invoice_url),
)
invoice_result = invoice_poller.result()

for invoice in invoice_result.documents:
    fields = invoice.fields

    # Safely extract common invoice fields
    vendor = fields.get("VendorName", {})
    inv_id = fields.get("InvoiceId", {})
    total  = fields.get("InvoiceTotal", {})
    date   = fields.get("InvoiceDate", {})

    print(f"Vendor:       {vendor.get('content', 'N/A')}")
    print(f"Invoice ID:   {inv_id.get('content', 'N/A')}")
    print(f"Total:        {total.get('content', 'N/A')}")
    print(f"Date:         {date.get('content', 'N/A')}")

# Extract receipt data from a sample document
# Sample receipt from Azure documentation
receipt_url = "https://raw.githubusercontent.com/Azure-Samples/cognitive-services-REST-api-samples/master/curl/form-recognizer/contoso-receipt.png"

receipt_poller = doc_client.begin_analyze_document(
    "prebuilt-receipt",
    AnalyzeDocumentRequest(url_source=receipt_url),
)
receipt_result = receipt_poller.result()

for receipt in receipt_result.documents:
    fields = receipt.fields

    merchant = fields.get("MerchantName", {})
    total    = fields.get("Total", {})
    txn_date = fields.get("TransactionDate", {})

    print(f"Merchant:         {merchant.get('content', 'N/A')}")
    print(f"Total:            {total.get('content', 'N/A')}")
    print(f"Transaction Date: {txn_date.get('content', 'N/A')}")

# Detect handwritten text
# A sample form containing handwritten text (from the Azure SDK test suite)
handwritten_url = "https://raw.githubusercontent.com/Azure/azure-sdk-for-python/main/sdk/formrecognizer/azure-ai-formrecognizer/tests/sample_forms/forms/Form_1.jpg"

hw_poller = doc_client.begin_analyze_document(
    "prebuilt-read",
    AnalyzeDocumentRequest(url_source=handwritten_url),
)
hw_result: AnalyzeResult = hw_poller.result()

# Check style information for handwriting detection
if hw_result.styles:
    for style in hw_result.styles:
        if style.is_handwritten:
            print(f"Handwritten text detected (confidence: {style.confidence:.0%})")
else:
    print("No style information returned.")

# Print the extracted paragraphs regardless
print("\nExtracted text:")
for i, para in enumerate(hw_result.paragraphs, start=1):
    print(f"  {i}. {para.content}")
