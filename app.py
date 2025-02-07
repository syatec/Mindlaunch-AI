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
extension_config = {
    "dataSources": [
        {
            "type": "AzureCognitiveSearch",
            "parameters": {
                "endpoint": azure_search_endpoint,
                "key": azure_search_key,
                "indexName": azure_search_index,
            }
        }
    ]
}
# Route pour la page d'accueil
@app.route("/")
def home():
    return render_template("index.html")

# Route pour gérer les questions de l'utilisateur
@app.route("/ask", methods=["POST"])
def ask():
    try:
        # Récupérer la question de l'utilisateur
        user_input = request.json.get("message")

        # Envoyer la requête à Azure OpenAI
        response = client.chat.completions.create(
            model=azure_oai_deployment,
            temperature=0.7,
            max_tokens=1000,
            top_p=0.5,
            messages=[
                {"role": "system", "content": "You are a helpful and empathetic agent."},
                {"role": "user", "content": user_input}
            ],
            extra_body=extension_config
        )

        # Récupérer la réponse
        bot_response = response.choices[0].message.content
        bot_response = re.sub(r'\[doc\d+\]', '', bot_response)
        # Retourner la réponse au format JSON
        return jsonify({"message": bot_response})

    except Exception as ex:
        return jsonify({"error": str(ex)}), 500

# Démarrer l'application
if __name__ == "__main__":
    app.run(debug=True)
