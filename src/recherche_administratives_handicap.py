from datetime import datetime
import os
from dotenv import load_dotenv
from openai import OpenAI

def generate_search_query(question_utilisateur):
    """
    Extrait les mots-clés d'une question utilisateur pour une recherche optimisée.
    
    :param question_utilisateur: La question spécifique de l'utilisateur
    :return: Liste de mots-clés extraits
    """
    pass

def generate_response_from_search(response):
    """
    Génère une réponse à partir des résultats de recherche.
    
    :param response: Résultats de la recherche
    :return: Réponse formatée
    """
    pass

def recherche_administratives_handicap(question_utilisateur):
    """
    Effectue une recherche comprehensive sur les procédures administratives 
    pour les personnes en situation de handicap en France.
    
    :param question_utilisateur: La question spécifique de l'utilisateur
    :return: Le contenu de la recherche
    """
    # Préparation du prompt en français
    prompt = f"""Nous sommes le {datetime.now().strftime("%Y-%m-%d")}. Réalisez une recherche approfondie sur les procédures administratives pour les personnes en situation de handicap en France, en répondant précisément à la question suivante : "{question_utilisateur}"

    Objectifs de la recherche :
    • Périmètre : Examiner le paysage administratif lié à la requête, en se concentrant sur :
        - Les processus de la MDPH (Maison Départementale des Personnes Handicapées)
        - Les mécanismes de soutien nationaux et locaux pertinents
        - Les cadres juridiques et administratifs spécifiques
        - Les associations de soutien et ressources importantes

    • Analyse détaillée : Exploration approfondie :
        - Étapes procédurales spécifiques liées à la question
        - Types de soutiens administratifs et d'assistance applicables
        - Conseils pratiques et solutions potentielles
        - Développements récents ou changements dans le domaine concerné

    • Perspectives critiques : Évaluer :
        - Forces et limites potentielles des systèmes de soutien existants
        - Défis pratiques dans le traitement de la préoccupation spécifique
        - Voies potentielles de résolution ou de soutien

    • Approche centrée sur l'utilisateur : Traduire les informations administratives complexes en conseils clairs et actionnables

    • Compilation exhaustive des ressources :
        - Coordonnées détaillées des institutions pertinentes
        - Liens vers des ressources officielles et formulaires de demande
        - Conseils pratiques pour naviguer dans le processus administratif

    • Documentation transparente :
        - Citations compréhensives
        - Références à des sources officielles
        - Informations vérifiables provenant d'institutions réputées

    # Procédures administratives pour le handicap en France : {question_utilisateur}
    """
    
    load_dotenv()
    api_key = os.getenv("OPENAI_API_KEY")
    client = OpenAI(api_key=api_key)
    
    try:
        # Création de la requête
        completion = client.chat.completions.create(
            model="gpt-4o-search-preview",
            web_search_options={
                "user_location": {
                    "type": "approximate",
                    "approximate": {
                        "country": "FR",
                    }
                },
            },
            messages=[{
                "role": "user",
                "content": prompt,
            }],
        )
        
        # Retourne le contenu de la réponse
        return completion.choices[0].message.content
    
    except Exception as e:
        return f"Une erreur s'est produite : {str(e)}"

# Exemple d'utilisation
if __name__ == "__main__":
    # Quelques exemples de questions
    questions = [
        "Comment obtenir un accompagnement administratif pour des aménagements au travail ?",
        "Quelles sont les démarches pour obtenir une reconnaissance de la qualité de travailleur handicapé ?",
        "Quels sont les droits des personnes handicapées en matière de logement ?",
        "Comment faire une demande de carte d'invalidité ?",
        "Quels sont les recours possibles en cas de refus de la MDPH ?",
        "Comment bénéficier d'une aide financière pour l'aménagement du domicile ?",
    ]
    
    # Exécution de la recherche pour chaque question
    for question in questions:
        print(f"\n--- Recherche pour : {question} ---")
        resultat = recherche_administratives_handicap(question)
        print(resultat)