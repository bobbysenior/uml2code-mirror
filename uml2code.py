### uml2code.py
import argparse
import sys
import os

# Ajout du dossier courant au path pour les imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from core.core import ModelFactory, Class, Interface, Enum, Attribute, Method, AccessSpecifier
from core.parser import PlantUMLParser

# Import des implémentations spécifiques (lib)
# Note: On assume que CppClassDiagram.py est dans le dossier lib/
from lib.CppClassDiagram import CppClass, CppInterface, CppEnum, CppAttribute, CppMethod

# --- FACTORIES CONCRÈTES ---

class CppFactory(ModelFactory):
    def create_class(self, name: str, is_abstract: bool = False) -> Class:
        return CppClass(name=name, is_abstract=is_abstract)
    
    def create_interface(self, name: str) -> Interface:
        return CppInterface(name=name)
    
    def create_enum(self, name: str) -> Enum:
        return CppEnum(name=name)
    
    def create_attribute(self, name: str, type_name: str, visibility: AccessSpecifier) -> Attribute:
        return CppAttribute(name, type_name, visibility)
    
    def create_method(self, name: str, visibility: AccessSpecifier, return_type: str) -> Method:
        return CppMethod(name, visibility, return_type=return_type)

class PythonFactory(ModelFactory):
    # Stub pour Python (à implémenter plus tard dans lib/PythonClassDiagram.py)
    def create_class(self, name: str, is_abstract: bool = False) -> Class:
        return Class(name=name, is_abstract=is_abstract) # Retourne générique pour l'instant
    def create_interface(self, name: str) -> Interface: return Interface(name=name)
    def create_enum(self, name: str) -> Enum: return Enum(name=name)
    def create_attribute(self, name: str, type_name: str, visibility: AccessSpecifier) -> Attribute:
        return Attribute(name, type_name, visibility)
    def create_method(self, name: str, visibility: AccessSpecifier, return_type: str) -> Method:
        return Method(name, visibility, return_type=return_type)

class JavaFactory(ModelFactory):
    # Stub pour Java
    def create_class(self, name: str, is_abstract: bool = False) -> Class: return Class(name=name)
    def create_interface(self, name: str) -> Interface: return Interface(name=name)
    def create_enum(self, name: str) -> Enum: return Enum(name=name)
    def create_attribute(self, name: str, type_name: str, visibility: AccessSpecifier) -> Attribute: return Attribute(name, type_name, visibility)
    def create_method(self, name: str, visibility: AccessSpecifier, return_type: str) -> Method: return Method(name, visibility, return_type=return_type)

# --- MAIN CLI ---

def main():
    parser = argparse.ArgumentParser(description="Transform PlantUML class diagrams to Source Code.")
    parser.add_argument("input_file", help="Path to the .puml file")
    parser.add_argument("--language", "-l", choices=["Cpp", "Java", "Python"], required=True, help="Target language")
    parser.add_argument("--output", "-o", default="output", help="Output directory")

    args = parser.parse_args()

    # 1. Sélection de la Factory
    factory = None
    if args.language == "Cpp":
        factory = CppFactory()
    elif args.language == "Python":
        factory = PythonFactory()
    elif args.language == "Java":
        factory = JavaFactory()
    
    if not factory:
        print("Erreur: Langage non supporté.")
        sys.exit(1)

    print(f"--- Parsing {args.input_file} pour générer du {args.language} ---")

    # 2. Parsing
    uml_parser = PlantUMLParser(factory)
    try:
        diagram = uml_parser.parse_file(args.input_file)
    except FileNotFoundError:
        print(f"Erreur: Le fichier {args.input_file} est introuvable.")
        sys.exit(1)
    except Exception as e:
        print(f"Erreur lors du parsing: {e}")
        sys.exit(1)

    # 3. Génération
    if not os.path.exists(args.output):
        os.makedirs(args.output)

    print(f"--- Génération des fichiers dans ./{args.output}/ ---")
    
    for element in diagram.elements:
        # On vérifie que l'élément peut générer du code
        # Les CppClass, CppEnum, etc. ont implémenté to_code()
        code = element.to_code()
        
        if code:
            # Détermination du nom de fichier (ex: ClassName.h pour C++)
            filename = "unknown"
            if hasattr(element, "_name"):
                if args.language == "Cpp":
                    filename = f"{element._name}.h"
                elif args.language == "Java":
                    filename = f"{element._name}.java"
                elif args.language == "Python":
                    filename = f"{element._name}.py"
            
            filepath = os.path.join(args.output, filename)
            
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(code)
            
            print(f"-> Créé : {filename}")

    print("Terminé.")

if __name__ == "__main__":
    main()