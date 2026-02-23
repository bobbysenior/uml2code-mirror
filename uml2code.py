"""
Module:       uml2code
Project:      uml2code
Author:       Thomas MEZINO
AI Assistant: Gemini 3.1 Pro (Google)
License:      GPL3.0

Description:
    Point d'entrée principal en ligne de commande. Il orchestre l'analyse du 
    fichier PlantUML via le parser et génère le code en appelant la factory du langage cible.

Usage:
    python uml2code.py -l <Langage> -o <Dossier_Sortie> <Fichier_Entree.puml>

Dependencies:
    - [Aucune dépendance externe, utilise argparse de la bibliothèque standard]
"""
import argparse
import sys
import os
import importlib

# On importe le parser que nous avons créé précédemment
from core.parser import PlantUMLParser

def main():
    # 1. Configuration de l'interface en ligne de commande (CLI)
    cli_parser = argparse.ArgumentParser(
        description="Convertisseur de diagramme de classe UML (PlantUML) en code source."
    )
    
    # Argument positionnel pour le fichier d'entrée
    cli_parser.add_argument(
        "input", 
        help="Chemin vers le fichier de diagramme PlantUML (ex: diagram.puml)"
    )
    
    # Option -l / --language (Requise)
    cli_parser.add_argument(
        "-l", "--language", 
        required=True, 
        help="Le langage cible pour la génération (ex: Cpp, Java, Python)"
    )
    
    # Option -o / --output (Optionnelle, défaut: dossier courant)
    cli_parser.add_argument(
        "-o", "--output", 
        default=".", 
        help="Dossier de sortie pour les fichiers générés (défaut: dossier courant)"
    )
    
    args = cli_parser.parse_args()

    # 2. Vérification du fichier d'entrée
    if not os.path.isfile(args.input):
        print(f"Erreur : Le fichier '{args.input}' n'existe pas.")
        sys.exit(1)

    # 3. Création du dossier de sortie s'il n'existe pas
    if not os.path.exists(args.output):
        try:
            os.makedirs(args.output)
            print(f"Dossier de sortie '{args.output}' créé.")
        except OSError as e:
            print(f"Erreur lors de la création du dossier de sortie : {e}")
            sys.exit(1)

    # 4. Importation DYNAMIQUE du module de langage
    # Si args.language = "Cpp", on va chercher "CppDiagram.py" et la classe "Cpp"
    module_name = f"{args.language}ClassDiagram"
    class_name = args.language
    
    try:
        # Importe uniquement le fichier correspondant au langage
        lang_module = importlib.import_module("lib."+module_name)
        # Récupère la classe Factory (ex: la classe Cpp)
        LanguageFactory = getattr(lang_module, class_name)
        # Instancie la Factory
        language_instance = LanguageFactory()
        print(f"Module de langage '{args.language}' chargé avec succès.")
        
    except ImportError:
        print(f"Erreur : Impossible de trouver le module d'implémentation pour le langage '{args.language}'.")
        print(f"Assurez-vous qu'un fichier '{module_name}.py' existe.")
        sys.exit(1)
    except AttributeError:
        print(f"Erreur : Le module '{module_name}.py' ne contient pas de classe nommée '{class_name}'.")
        sys.exit(1)

    # 5. Parsing du diagramme
    print(f"Analyse du diagramme '{args.input}'...")
    parser = PlantUMLParser(language_instance)
    diagram = parser.parse_file(args.input)

    # 6. Génération du code
    print(f"Génération du code dans '{args.output}'...")
    
    # Parcours des éléments parsés pour générer les fichiers
    # (Logique simplifiée : on parcourt le package par défaut et on génère le code pour les classes/interfaces/enums)
    for package in diagram._packages:
        for element in package._elements:
            # On génère un fichier uniquement pour les éléments qui ont un nom (Class, Interface, Enum)
            if hasattr(element, '_name') and element._name:
                code_content = element.toCode()
                
                # Si toCode() n'est pas encore implémenté, il retournera None
                if code_content:
                    # L'extension du fichier devrait idéalement être gérée par le langage (ex: .cpp, .h, .java)
                    # Pour l'instant, on utilise une extension générique ou le nom brut si le langage ne la gère pas
                    filepath = os.path.join(args.output, f"{element._name}.{language_instance.file_extension}") 
                    
                    with open(filepath, 'w', encoding='utf-8') as f:
                        f.write(code_content)
                    print(f" -> Fichier généré : {filepath}")
                else:
                    print(f" -> (Alerte: toCode() non implémenté pour {element._name})")

    print("\nProcessus terminé avec succès !")

if __name__ == "__main__":
    main()