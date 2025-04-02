from datetime import datetime
import os
from dotenv import load_dotenv
from openai import OpenAI


def is_legit_question(question_utilisateur):  
    """
    Vérifie si la question posée par l'utilisateur est légitime ou non.
    
    :param question_utilisateur: La question spécifique de l'utilisateur
    :return: "legit" ou "not_legit" selon la classification
    """
    load_dotenv()
    api_key = os.getenv("OPENAI_API_KEY")
    client = OpenAI(api_key=api_key)

    categories = "{\n  \"legit\": \"the user ask a legit question about disability in France\",\n  \"not_legit\": \"the user ask a not legit question about disability in France\"\n}"
    response = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[
        {"role": "system", "content": f"You will be provided with input text from a user. Classify the intent into one of these categories:\n{categories}\n\nOnly output the category name, without any additional text."},
        {"role": "user", "content": question_utilisateur}
        ]
    )  

    return response.choices[0].message.content

def generate_search_query(question_utilisateur):
    """
    Extrait les mots-clés d'une question utilisateur pour une recherche optimisée.
    
    :param question_utilisateur: La question spécifique de l'utilisateur
    :return: Liste de mots-clés extraits
    """
    load_dotenv()
    api_key = os.getenv("OPENAI_API_KEY")
    client = OpenAI(api_key=api_key)
    
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": f"You will be provided with a user query. Your goal is to extract a few keywords from the text to perform a search.\nKeep the search query to a few keywords that capture the user's intent.\nOnly output the keywords, without any additional text."},
            {"role": "user", "content": question_utilisateur + "\n\nKeywords:"}
        ]
    )  
    return response.choices[0].message.content


def recherche_administratives_handicap(question_utilisateur):
    """
    Effectue une recherche comprehensive sur les procédures administratives 
    pour les personnes en situation de handicap en France.
    
    :param question_utilisateur: La question spécifique de l'utilisateur
    :return: Le contenu de la recherche
    """
    # Préparation du prompt en français
    prompt = f"""Nous sommes le {datetime.now().strftime("%Y-%m-%d")}. Réalisez une recherche approfondie sur l'écosystème complet de soutien aux personnes en situation de handicap en France, en répondant précisément à la question suivante : "{question_utilisateur}"

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

    # Écosystème complet de soutien au handicap en France : {question_utilisateur}
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
                {"role": "user", "content": question_utilisateur,}],
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
        "Pourquoi le ciel est-il bleu ?",   
        "Comment cuisiner des pâtes ?",
    ]
    
    # Exécution de la recherche pour chaque question
    for question in questions:
        print(f"\n--- Recherche pour : {question} ---")
        # Vérification de la légitimité de la question
        if is_legit_question(question) == "legit":
            # Génération de la requête de recherche
            keywords = generate_search_query(question)
            print(f"Mots-clés extraits : {keywords}")
            
            # Recherche administrative
            resultat = recherche_administratives_handicap(keywords)
            print("Résultat de la recherche :")
            print(resultat)
        else:
            print("La question posée n'est pas légitime.")
            resultat = "La question posée n'est pas légitime."
        print(resultat)