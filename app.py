import os
import json
import re
from dotenv import load_dotenv
from flask import Flask, request, render_template, jsonify
from openai import AzureOpenAI
from azure.identity import DefaultAzureCredential
from azure.keyvault.secrets import SecretClient

# Charger les variables d'environnement
load_dotenv()

# Initialiser Flask
app = Flask(__name__)

# Fonction pour interagir avec Azure OpenAI
# Configuration Azure Key Vault
key_vault_name = "maclescrete"
key_vault_uri = f"https://{key_vault_name}.vault.azure.net"

# Initialiser le client Azure Key Vault
credential = DefaultAzureCredential()
secret_client = SecretClient(vault_url=key_vault_uri, credential=credential)

# Fonction pour interagir avec Azure OpenAI
def ask_azure_openai(question):
    try:
        # Récupérer les secrets depuis Azure Key Vault
        azure_oai_endpoint = secret_client.get_secret("AZURE-OAI-ENDPOINT").value
        azure_oai_key = secret_client.get_secret("AZURE-OAI-KEY").value
        azure_oai_deployment = secret_client.get_secret("AZURE-OAI-DEPLOYMENT").value
        azure_search_endpoint = secret_client.get_secret("AZURE-SEARCH-ENDPOINT").value
        azure_search_key = secret_client.get_secret("AZURE-SEARCH-KEY").value
        azure_search_index = secret_client.get_secret("AZURE-SEARCH-INDEX").value

        # Initialiser le client Azure OpenAI
        client = AzureOpenAI(
            base_url=f"{azure_oai_endpoint}/openai/deployments/{azure_oai_deployment}/extensions",
            api_key=azure_oai_key,
            api_version="2023-09-01-preview"
        )

        # Configuration de la source de données
        extension_config = dict(dataSources=[  
            { 
                "type": "AzureCognitiveSearch", 
                "parameters": { 
                    "endpoint": azure_search_endpoint, 
                    "key": azure_search_key, 
                    "indexName": azure_search_index,
                }
            }]
        )

        # Envoyer la requête à Azure OpenAI
        response = client.chat.completions.create(
            model=azure_oai_deployment,
            temperature=0.7,
            max_tokens=1500,
            messages=[
                {"role": "system", "content": "You are a helpful and empathetic agent."},
                {"role": "user", "content": question}
            ],
            extra_body=extension_config
        )

        # Nettoyer la réponse
        response_text = response.choices[0].message.content
        cleaned_response = re.sub(r'\[doc\d+\]', '', response_text)

        return cleaned_response

    except Exception as ex:
        return str(ex)

# Route pour l'API
@app.route('/ask', methods=['POST'])
def ask():
    data = request.json
    question = data.get('question')
    if not question:
        return jsonify({"error": "Question is required"}), 400

    response = ask_azure_openai(question)
    return jsonify({"response": response})

# Démarrer l'application Flask
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
