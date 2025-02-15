import os
import json
import base64
from dotenv import load_dotenv
from flask import Flask, request, render_template, jsonify
from openai import AzureOpenAI
from azure.identity import DefaultAzureCredential, get_bearer_token_provider  
import re
# Charger les variables d'environnement
load_dotenv()

# Initialiser Flask
app = Flask(__name__)
    
endpoint = os.getenv("ENDPOINT_URL", "https://mindlaunch-azure-openai.openai.azure.com/")  
deployment = os.getenv("DEPLOYMENT_NAME", "gpt-4")  
subscription_key = os.getenv("AZURE_OPENAI_API_KEY", "9dn00w1yqvUbpwdroiZnZyJ71EAuDWvvczslrs9y4pZkvRfg3TP1JQQJ99BBACYeBjFXJ3w3AAABACOGi26S")  

# Initialiser le client Azure OpenAI Service avec une authentification basée sur une clé    
client = AzureOpenAI(  
    azure_endpoint=endpoint,  
    api_key=subscription_key,  
    api_version="2024-05-01-preview",
)

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
            model=deployment,
            temperature=0.8,
            max_tokens=1500,
            top_p=0.95,
            frequency_penalty=0,  
            presence_penalty=0,
            stop=None,  
            stream=False,
            messages=[
                {"role": "system", "content": "you are a helpful and empathetic life coach expert in the law of attraction according to the teachings of Abraham Hicks."},
                {"role": "user", "content": user_input}
            ]
            #extra_body=extension_config
        )

        # Récupérer la réponse
        bot_response = response.choices[0].message.content
        #bot_response = re.sub(r'\[doc\d+\]', '', bot_response)
        # Retourner la réponse au format JSON
        
        # Formater la réponse pour afficher chaque point sur une nouvelle ligne
     
        return jsonify({"message": bot_response})

    except Exception as ex:
        return jsonify({"error": str(ex)}), 500

# Démarrer l'application
if __name__ == "__main__":
    app.run(debug=True)
