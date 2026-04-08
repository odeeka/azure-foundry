# Foundry Tools

This folder contains local Python examples for service-specific tool scenarios that sit alongside the main Foundry lab deployment.

Copy `.env.example` to `.env` and fill in the values from `terraform output` before running any script:

```bash
cp .env.example .env
```

The scripts in this directory use `DefaultAzureCredential` for authentication. Run `az login` before executing any script.

## Speech

The Speech examples in this folder target a dedicated Azure AI Speech resource.

Typical scenarios:

- captioning
- voice live experiences
- call center flows
- audio content creation such as audiobooks
- speech translation
- language learning
- live captions, subtitles, and read-aloud features

## Infrastructure Dependency

If you want to run Speech examples from this folder, enable the optional Speech deployment in Terraform.

Relevant Terraform files:

- [infra/terraform/speech.tf](infra/terraform/speech.tf)
- [infra/terraform/variables.tf](infra/terraform/variables.tf)
- [infra/terraform/outputs.tf](infra/terraform/outputs.tf)
- [infra/terraform/README.md](infra/terraform/README.md)

Set the following variables in your Terraform settings before `terraform apply`:

- `enable_speech_deployment = true`
- `speech_account_name_prefix = "<unique-prefix>"`
- `speech_sku = "S0"` or `"F0"`

After deployment, use these Terraform outputs in your local `.env` or script configuration:

- `speech_endpoint`
- `speech_region`
- `speech_resource_id`

If you keep `assign_current_principal_speech_user_role = true`, the current authenticated principal also receives the `Cognitive Services Speech User` role on the Speech resource.

## 01_speech_tool.py

The script [tools/01_speech_tool.py](tools/01_speech_tool.py) is a compact end-to-end Speech SDK sample.

It demonstrates three operations in one run:

- text-to-speech from a plain text string
- SSML-based speech synthesis
- speech-to-text transcription from the generated WAV file

### Required Configuration

The script expects these environment variables in `tools/.env`:

- `SPEECH_REGION`
- `SPEECH_RESOURCE_ID`

The values should come from Terraform outputs after the optional Speech deployment is enabled.

### Authentication Model

The script uses `DefaultAzureCredential` and requests a bearer token for `https://cognitiveservices.azure.com/.default`.

The token is then converted into the authorization format expected by the Speech SDK:

```text
aad#<speech-resource-id>#<entra-token>
```

The identity that runs the script must have the `Cognitive Services Speech User` role on the Speech resource.

### Output Files

The script writes these local files in the `tools/` folder:

- `tts_output.wav`
- `ssml_output.wav`
- `transcription.txt`

### Expected Flow

1. Load local environment values.
2. Acquire an Entra ID token.
3. Synthesize audio from the `sample_text` string.
4. Synthesize a second WAV file from SSML.
5. Transcribe the generated WAV back into text.

If synthesis or transcription fails, the script prints the Speech SDK cancellation reason and error details to make authentication and configuration problems easier to diagnose.

---

## Language

The Language examples in this folder target a dedicated Azure AI Language resource.

Typical scenarios:

- language detection
- key phrase extraction
- sentiment analysis
- named entity recognition
- summarization
- question answering
- PII detection

If you want to run Language examples from this folder, enable the optional Language deployment in Terraform.

Relevant Terraform files:

- [infra/terraform/language.tf](infra/terraform/language.tf)
- [infra/terraform/variables.tf](infra/terraform/variables.tf)
- [infra/terraform/outputs.tf](infra/terraform/outputs.tf)
- [infra/terraform/README.md](infra/terraform/README.md)

Set the following variables in your Terraform settings before `terraform apply`:

- `enable_language_deployment = true`
- `language_account_name_prefix = "<unique-prefix>"`
- `language_sku = "S"` or `"F0"`

After deployment, use these Terraform outputs in your local `.env` or script configuration:

- `language_endpoint`
- `language_region`
- `language_resource_id`

If you keep `assign_current_principal_language_user_role = true`, the current authenticated principal also receives the Language role configured in Terraform. The default is `Cognitive Services Language Reader`.

If Terraform runs with a service principal but your local script runs with `az login`, also set `language_user_object_ids` in Terraform to the Entra object ID of the user who will run the script. Otherwise the Language SDK can fail with a data-plane permission error for `Microsoft.CognitiveServices/accounts/Language/analyze-text/action`.

---

## Translator

The Translator examples in this folder target a dedicated Azure AI Translator resource.

Typical scenarios:

- text translation
- translation into multiple target languages
- automatic source-language detection
- document translation
- custom translation pipelines

If you want to run Translator examples from this folder, enable the optional Translator deployment in Terraform.

Relevant Terraform files:

- [infra/terraform/translator.tf](infra/terraform/translator.tf)
- [infra/terraform/variables.tf](infra/terraform/variables.tf)
- [infra/terraform/outputs.tf](infra/terraform/outputs.tf)
- [infra/terraform/README.md](infra/terraform/README.md)

Set the following variables in your Terraform settings before `terraform apply`:

- `enable_translator_deployment = true`
- `translator_account_name_prefix = "<unique-prefix>"`
- `translator_sku = "S1"` or `"F0"`

After deployment, use these Terraform outputs in your local `.env` or script configuration:

- `translator_endpoint`
- `translator_region`
- `translator_resource_id`

Use the `translator_endpoint` output exactly as returned by Terraform. It should be the custom-domain endpoint in the form `https://<account-name>.cognitiveservices.azure.com/`, which is the value expected by the local Translator script.

If you keep `assign_current_principal_translator_user_role = true`, the current authenticated principal also receives the `Cognitive Services User` role on the Translator resource.

If Terraform runs with a service principal but your local script runs with `az login`, also set `translator_user_object_ids` in Terraform to the Entra object ID of the user who will run the script.

---

## Document Intelligence

The Document Intelligence examples in this folder target a dedicated Azure AI Document Intelligence resource.

Typical scenarios:

- OCR and text extraction from PDFs and images
- invoice field extraction
- receipt field extraction
- layout analysis
- handwritten text detection
- custom model driven document processing

If you want to run Document Intelligence examples from this folder, enable the optional Document Intelligence deployment in Terraform.

Relevant Terraform files:

- [infra/terraform/document_intelligence.tf](infra/terraform/document_intelligence.tf)
- [infra/terraform/variables.tf](infra/terraform/variables.tf)
- [infra/terraform/outputs.tf](infra/terraform/outputs.tf)
- [infra/terraform/README.md](infra/terraform/README.md)

Set the following variables in your Terraform settings before `terraform apply`:

- `enable_document_intelligence_deployment = true`
- `document_intelligence_account_name_prefix = "<unique-prefix>"`
- `document_intelligence_sku = "S0"` or `"F0"`

After deployment, use these Terraform outputs in your local `.env` or script configuration:

- `document_intelligence_endpoint`
- `document_intelligence_region`
- `document_intelligence_resource_id`

Use the `document_intelligence_endpoint` output exactly as returned by Terraform. It should be the custom-domain endpoint in the form `https://<account-name>.cognitiveservices.azure.com/`, which is the value expected by the local Document Intelligence SDK sample.

If you keep `assign_current_principal_document_intelligence_user_role = true`, the current authenticated principal also receives the `Cognitive Services User` role on the Document Intelligence resource.

If Terraform runs with a service principal but your local script runs with `az login`, also set `document_intelligence_user_object_ids` in Terraform to the Entra object ID of the user who will run the script.

The script [tools/04_document_intelligence.py](tools/04_document_intelligence.py) is the local Python working area for these scenarios, while the notebook remains reference material.

---

## Search

The Search examples in this folder target a dedicated Azure AI Search service and reuse the main Foundry OpenAI deployment for RAG scenarios.

Typical scenarios:

- full-text search across indexed documents
- filtered queries by category or metadata
- semantic ranking
- RAG with Azure AI Search plus Azure OpenAI
- index creation and document upload with Entra ID authentication

If you want to run Search examples from this folder, enable the optional Search deployment in Terraform.

Relevant Terraform files:

- [infra/terraform/search.tf](infra/terraform/search.tf)
- [infra/terraform/variables.tf](infra/terraform/variables.tf)
- [infra/terraform/outputs.tf](infra/terraform/outputs.tf)
- [infra/terraform/README.md](infra/terraform/README.md)

Set the following variables in your Terraform settings before `terraform apply`:

- `enable_search_deployment = true`
- `search_service_name_prefix = "<unique-prefix>"`
- `search_sku = "basic"` or another supported Search SKU
- `search_semantic_search_sku = "free"` or `"standard"`
- `search_local_authentication_enabled = false`

After deployment, use these Terraform outputs in your local `.env` or script configuration:

- `search_endpoint`
- `search_openai_endpoint`
- `search_openai_deployment_name`

Set `SEARCH_INDEX_NAME` empty on the first run. The notebook or local script can create the index and then write the actual index name back into `.env`.

If you keep `assign_current_principal_search_roles = true`, the current authenticated principal also receives these Search roles on the Search service:

- `Search Service Contributor`
- `Search Index Data Contributor`
- `Search Index Data Reader`

If Terraform runs with a service principal but your local script runs with `az login`, also set both `search_user_object_ids` and `openai_user_object_ids` in Terraform to the Entra object ID of the user who will run the script. The Search roles are needed for indexing and querying, and the OpenAI role is needed for the RAG call.

The script [tools/05_search_tool.py](tools/05_search_tool.py) is the local Python working area for these scenarios, while the notebook remains reference material.
