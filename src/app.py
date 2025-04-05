from dotenv import load_dotenv
from flask import Flask, request, jsonify
from flask_cors import CORS
from src.recherche_administratives_handicap import (
    is_legit_question, check_clarification_needed, generate_search_query, 
    recherche_administratives_handicap
)
import os
from datetime import datetime
import logging

# Configuration de l'application
app = Flask(__name__)
CORS(app, resources={r"/api/*": {
    "origins": ["https://mohamed-ali-sobhi.com",],
    "methods": ["GET", "POST", "OPTIONS"],
    "allow_headers": ["Content-Type", "Authorization"]
}})

# Configuration du logging
logging.basicConfig(
    filename='app.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# Vérification de la clé API
load_dotenv()
if not os.getenv("OPENAI_API_KEY"):
    logging.error("Clé API OpenAI non trouvée")
    raise EnvironmentError("La clé API OpenAI doit être définie dans les variables d'environnement")

# Route pour vérifier si une question nécessite des précisions
@app.route('/api/check-clarification', methods=['POST'])
def check_clarification():
    """
    Endpoint pour vérifier si une question nécessite des précisions
    Retourne les questions de précision si nécessaire
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
        
        # Vérification du besoin de précisions
        needs_clarification, clarification_questions = check_clarification_needed(question)
        
        response = {
            "status": "success",
            "needs_clarification": needs_clarification,
            "questions": clarification_questions if needs_clarification else [],
            "timestamp": datetime.now().isoformat()
        }
        
        app.logger.info(f"Vérification de clarification pour: {question}, résultat: {needs_clarification}")
        return jsonify(response), 200
        
    except Exception as e:
        app.logger.error(f"Erreur serveur lors de la vérification de clarification: {str(e)}")
        return jsonify({"error": "Erreur interne du serveur"}), 500

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
        clarifications = data.get('clarifications', {})
        
        # Validation de l'entrée
        if not question:
            return jsonify({"error": "La question est requise"}), 400
            
        # Log de la recherche
        app.logger.info(f"Recherche initiée: {question}")
        if clarifications:
            app.logger.info(f"Avec précisions: {clarifications}")
        
        # Exécution de la recherche
        if is_legit_question(question, clarifications):
            # Génération de la requête de recherche avec les précisions
            keywords = generate_search_query(question, clarifications)
            app.logger.info(f"Mots-clés extraits: {keywords}")
        else:
            app.logger.warning(f"Question non légitime: {question}")
            return jsonify({"error": "La question posée n'est pas liée au handicap en France"}), 400
            
        # Génération de la requête de recherche avec les précisions
        app.logger.info(f"Mots-clés extraits: {keywords}")
        
        # Recherche avec précisions
        result = recherche_administratives_handicap(question, clarifications)
        
        # Vérification du résultat
        if "Une erreur s'est produite" in result:
            app.logger.error(f"Erreur dans la recherche: {result}")
            return jsonify({"error": "Erreur lors du traitement de la recherche"}), 500
            
        # Formatage de la réponse
        response = {
            "status": "success",
            "question": question,
            "clarifications": clarifications,
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