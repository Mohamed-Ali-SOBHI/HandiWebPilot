from datetime import datetime
import json
import os
from dotenv import load_dotenv
from openai import OpenAI


def is_legit_question(question: str) -> bool:
    """
    Vérifie si la question est légitime (liée au handicap en France)
    Args:
        question (str): La question posée
        clarifications (dict): Les précisions apportées à la question
    Returns:
        bool: True si la question est légitime, False sinon
    """
    load_dotenv()
    api_key = os.getenv("OPENAI_API_KEY")
    client = OpenAI(api_key=api_key)

    categories = "{\n  \"legit\": \"the user asks a legit question about disability in France\",\n  \"not_legit\": \"the user asks a not legit question about disability in France\"\n}"
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": f"You will be provided with input text from a user. Classify the intent into one of these categories:\n{categories}\n\nOnly output the category name, without any additional text."},
            {"role": "user", "content": question}
            ]
        )  
    response = response.choices[0].message.content


def check_clarification_needed(question_utilisateur):
    """
    Détermine si la question de l'utilisateur nécessite des précisions avant la recherche.
    
    :param question_utilisateur: La question spécifique de l'utilisateur
    :return: Un tuple (besoin_clarification, questions_précision) où besoin_clarification est un booléen
             et questions_précision est une liste de questions à poser à l'utilisateur
    """
    load_dotenv()
    api_key = os.getenv("OPENAI_API_KEY")
    client = OpenAI(api_key=api_key)
    
    prompt = """Analysez la question suivante concernant le handicap en France et déterminez si des précisions sont nécessaires pour effectuer une recherche pertinente. 
                
                Si la question est suffisamment précise, répondez avec un JSON au format:
                {"needs_clarification": false, "questions": []}

                Si la question manque de précisions, répondez avec un JSON au format:
                {"needs_clarification": true, "questions": ["Question 1?", "Question 2?", ...]}

                Les questions de précision doivent être formulées en français et de manière respectueuse. Elles doivent aider à:
                - Clarifier le type de handicap concerné si pertinent
                - Préciser la situation géographique (département/région) si nécessaire
                - Comprendre le contexte spécifique (âge, situation professionnelle, etc.)
                - Obtenir des détails sur les besoins précis de la personne
                - Identifier si la demande concerne une personne précise ou une information générale

                Limitez-vous à 2-3 questions de précision maximum, les plus importantes."""

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        response_format={"type": "json_object"},
        messages=[
            {"role": "system", "content": prompt},
            {"role": "user", "content": question_utilisateur}
        ]
    )
    
    result = json.loads(response.choices[0].message.content)
    return result["needs_clarification"], result["questions"]



def generate_search_query(question_utilisateur, clarifications=None):
    """
    Extrait les mots-clés d'une question utilisateur pour une recherche optimisée.
    
    :param question_utilisateur: La question spécifique de l'utilisateur
    :param clarifications: Dictionnaire contenant les questions de précision et les réponses
    :return: Liste de mots-clés extraits
    """
    load_dotenv()
    api_key = os.getenv("OPENAI_API_KEY")
    client = OpenAI(api_key=api_key)
    
    # Préparation du contenu avec les précisions si disponibles
    content = question_utilisateur
    if clarifications:
        content += "\n\nPrécisions apportées:\n"
        for question, reponse in clarifications.items():
            content += f"- Question: {question}\n  Réponse: {reponse}\n"
    
    content += "\n\nKeywords:"
    
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You will be provided with a user query, possibly with clarifications. Your goal is to extract a few keywords from the text to perform a search. Keep the search query to a few keywords that capture the user's intent. Only output the keywords, without any additional text."},
            {"role": "user", "content": content}
        ]
    )  
    return response.choices[0].message.content


def recherche_administratives_handicap(question_utilisateur, clarifications=None):
    """
    Effectue une recherche comprehensive sur les procédures administratives 
    pour les personnes en situation de handicap en France.
    
    :param question_utilisateur: La question spécifique de l'utilisateur
    :param clarifications: Dictionnaire contenant les questions de précision et les réponses
    :return: Le contenu de la recherche
    """
    # Préparation du prompt en français avec les précisions si disponibles
    question_complete = question_utilisateur
    if clarifications:
        question_complete += "\n\nPrécisions supplémentaires :"
        for question, reponse in clarifications.items():
            question_complete += f"\n- {question}: {reponse}"
    
    prompt = f"""Nous sommes le {datetime.now().strftime("%Y-%m-%d")}. Réalisez une recherche approfondie sur l'écosystème complet de soutien aux personnes en situation de handicap en France, en répondant précisément à la question suivante : "{question_complete}"

    Objectifs de la recherche :
    - Périmètre élargi : Examiner l'ensemble des ressources disponibles liées à la requête, incluant :
        - Les processus administratifs (MDPH, CAF, CPAM, etc.)
        - Les associations spécialisées (nationales et locales)
        - Les entreprises proposant des services ou produits adaptés
        - Les dispositifs d'aide privés et publics
        - Les plateformes numériques et applications dédiées
        - Les réseaux d'entraide et communautés en ligne

    - Analyse multidimensionnelle :
        - Solutions administratives officielles
        - Alternatives associatives et privées
        - Innovations technologiques et services émergents
        - Témoignages et retours d'expérience pertinents
        - Astuces pratiques issues du terrain

    - Perspectives holistiques :
        - Complémentarité entre les différents types de soutien
        - Approches innovantes et bonnes pratiques
        - Solutions de contournement face aux obstacles courants
        - Comparaison des options disponibles (avantages/inconvénients)

    - Orientation concrète :
        - Contacts directs et personnes ressources
        - Numéros d'urgence ou d'assistance spécialisés
        - Groupes de soutien et forums recommandés
        - Événements, salons ou rencontres à connaître
        - Formations et ateliers pertinents

    - Compilation exhaustive :
        - Coordonnées détaillées de tous les acteurs pertinents
        - Liens vers plateformes et outils numériques utiles
        - Exemples de parcours réussis
        - Documentation à consulter (guides, tutoriels, vidéos explicatives)

    - Documentation transparente :
        - Diversité des sources (officielles, associatives, témoignages)
        - Indications sur la fiabilité et l'actualité des informations
        - Mention des controverses ou débats existants
        - Alternatives en cas d'impasse

    # Écosystème complet de soutien au handicap en France : {question_complete}
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
            messages=[
                {"role": "system", "content": prompt},
                {"role": "user", "content": question_complete,}],
        )
        
        # Retourne le contenu de la réponse
        return completion.choices[0].message.content
    
    except Exception as e:
        return f"Une erreur s'est produite : {str(e)}"


def process_user_query(question_utilisateur):
    """
    Traite une question utilisateur avec le processus complet : vérification de légitimité,
    demande de précisions si nécessaire, puis recherche.
    
    :param question_utilisateur: La question spécifique de l'utilisateur
    :return: Le résultat de la recherche ou un message d'erreur
    """
    print(f"\n--- Traitement de la question : {question_utilisateur} ---")
    
    # Détection de la nécessité de clarifications
    needs_clarification, clarification_questions = check_clarification_needed(question_utilisateur)
        
    clarifications = {}
    if needs_clarification:
        print("Des précisions sont nécessaires pour mieux répondre à votre question :")
        for i, question in enumerate(clarification_questions, 1):
            print(f"{i}. {question}")
            # Dans un environnement réel, vous récupéreriez la réponse de l'utilisateur
            # Simulation pour cet exemple
            reponse = input(f"Votre réponse à la question {i}: ")
            clarifications[question] = reponse
    
    # Génération de la requête de recherche optimisée
    keywords = generate_search_query(question_utilisateur, clarifications)
    print(f"Mots-clés extraits pour la recherche : {keywords}")
    
    # Vérification de la légitimité de la question
    combined_text = question_utilisateur
    if clarifications:
        combined_text += " " + " ".join([f"{q}: {r}" for q, r in clarifications.items()])
    combined_text += " " + keywords
    
    print(f"Texte combiné pour vérification : {combined_text}")
    if is_legit_question(combined_text) == "not_legit":
        return "La question posée n'est pas liée au handicap en France."
    
    # Recherche avec les précisions
    return recherche_administratives_handicap(question_utilisateur, clarifications)


# Exemple d'utilisation
if __name__ == "__main__":
    # Quelques exemples de questions
    questions = [
        "Transport à Paris ?",
    ]
    
    # Exécution interactive avec une seule question pour démonstration
    question = input("Entrez votre question sur le handicap en France : ")
    resultat = process_user_query(question)
    print("\nRésultat de la recherche :")
    print(resultat)