from dotenv import load_dotenv
from flask import Flask, request, jsonify
from flask_cors import CORS
from src.recherche_administratives_handicap import recherche_administratives_handicap, is_legit_question, generate_search_query
import os
from datetime import datetime
import logging

# Configuration de l'application
app = Flask(__name__)

CORS(app, resources={r"/api/*": {
    "origins": ["https://mohamed-ali-sobhi.com"],
    "methods": ["GET", "POST", "OPTIONS"],
    "allow_headers": ["Content-Type", "Authorization"]
}})

# Configuration du logging
logging.basicConfig(
    filename='app.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# Vérification de la clé API au 
load_dotenv()
if not os.getenv("OPENAI_API_KEY"):
    logging.error("Clé API OpenAI non trouvée")
    raise EnvironmentError("La clé API OpenAI doit être définie dans les variables d'environnement")

# Route principale pour la recherche
@app.route('/api/search', methods=['POST'])
def search():
    """
    Endpoint pour effectuer une recherche administrative sur le handicap
    Retourne les résultats formatés en JSON
    """
    try:
        # Vérification du content-type
        if not request.is_json:
            return jsonify({"error": "Content-Type doit être application/json"}), 415

        # Récupération des données
        data = request.get_json()
        question = data.get('question', '').strip()

        # Validation de l'entrée
        if not question:
            return jsonify({"error": "La question est requise"}), 400
        if len(question) > 1000:  # Limite arbitraire
            return jsonify({"error": "La question est trop longue"}), 400

        # Log de la recherche
        app.logger.info(f"Recherche initiée: {question}")

        # Exécution de la recherche
        if is_legit_question(question) != "legit":
            app.logger.warning(f"Question non légitime: {question}")
            return jsonify({"error": "La question posée n'est pas légitime"}), 400
        # Génération de la requête de recherche
        keywords = generate_search_query(question)
        result = recherche_administratives_handicap(question +" " + keywords)
        app.logger.info(f"Mots-clés extraits: {keywords}")

        # Vérification du résultat
        if "Une erreur s'est produite" in result:
            app.logger.error(f"Erreur dans la recherche: {result}")
            return jsonify({"error": "Erreur lors du traitement de la recherche"}), 500

        # Formatage de la réponse
        response = {
            "status": "success",
            "question": question,
            "result": result,
            "timestamp": datetime.now().isoformat()
        }

        app.logger.info(f"Recherche réussie pour: {question}")
        return jsonify(response), 200

    except Exception as e:
        app.logger.error(f"Erreur serveur: {str(e)}")
        return jsonify({"error": "Erreur interne du serveur"}), 500

# Gestion des erreurs globales
@app.errorhandler(404)
def not_found(error):
    return jsonify({"error": "Ressource non trouvée"}), 404

@app.errorhandler(405)
def method_not_allowed(error):
    return jsonify({"error": "Méthode non autorisée"}), 405

# Route de santé/test
@app.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "message": "Serveur opérationnel"
    }), 200

if __name__ == '__main__':
    # Configuration pour production
    port = int(os.getenv('PORT', 10000))
    app.run(host='0.0.0.0', port=port)