import os
import json
from dotenv import load_dotenv
from flask import Flask, request, render_template, jsonify
from openai import AzureOpenAI

# Charger les variables d'environnement
load_dotenv()

# Initialiser Flask
app = Flask(__name__)

# Configuration Azure OpenAI
azure_oai_endpoint = os.getenv("AZURE_OAI_ENDPOINT")
azure_oai_key = os.getenv("AZURE_OAI_KEY")
azure_oai_deployment = os.getenv("AZURE_OAI_DEPLOYMENT")
azure_search_endpoint = os.getenv("AZURE_SEARCH_ENDPOINT")
azure_search_key = os.getenv("AZURE_SEARCH_KEY")
azure_search_index = os.getenv("AZURE_SEARCH_INDEX")

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
            max_tokens=1500,
            messages=[
                {"role": "system", "content": "You are a helpful and empathetic agent."},
                {"role": "user", "content": user_input}
            ],
            extra_body=extension_config
        )

        # Récupérer la réponse
        bot_response = response.choices[0].message.content

        # Retourner la réponse au format JSON
        return jsonify({"message": bot_response})

    except Exception as ex:
        return jsonify({"error": str(ex)}), 500

# Démarrer l'application
if __name__ == "__main__":
    app.run(debug=True)
