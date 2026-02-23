"""
Module:       core.parser
Project:      uml2code
Author:       Thomas MEZINO
AI Assistant: Gemini 3.1 Pro (Google)
License:      GPL3.0

Description:
    Analyseur lexical et syntaxique pour les fichiers PlantUML. Il lit le diagramme, 
    identifie les éléments UML et les instancie dans le modèle abstrait en utilisant la factory du langage choisi.

Dependencies:
    - core.core
"""
import re
from typing import Dict, List, Optional
from core.core import Language, ClassDiagram, Package, accessSpecifier, Class

class PlantUMLParser:
    """
    Analyse un fichier PlantUML et construit l'arbre syntaxique abstrait (AST)
    en utilisant les implémentations spécifiques au langage fourni.
    """
    def __init__(self, language: Language):
        self.language = language
        self.diagram = ClassDiagram()
        # Par défaut, on place tout dans un package (comme indiqué dans la note de ton diagramme)
        self.default_package = Package()
        self.diagram._packages.append(self.default_package)
        
        # Dictionnaire pour garder une trace des classes/interfaces par leur nom 
        # afin de lier les relations (source/destination) plus tard.
        self.elements_map: Dict[str, Class] = {}
        
        # État du parser
        self.current_class: Optional[Class] = None
        self.rel_counter = 0
        self.in_note = False

    def parse_file(self, filepath: str) -> ClassDiagram:
        with open(filepath, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            
        for line in lines:
            self._parse_line(line.strip())
            
        return self.diagram

    def _parse_line(self, line: str) -> None:
        # Ignorer les lignes vides ou les commentaires PlantUML
        if not line or line.startswith("'") or line == "@startuml" or line == "@enduml":
            return

        # --- GESTION DES NOTES ---
        if line.startswith("note "):
            self.in_note = True
            return
        if line == "end note":
            self.in_note = False
            return
        if self.in_note:
            return  # On ignore tout le contenu à l'intérieur d'une note

        # 1. Détection des Classes (gère "class" ET "abstract class")
        class_match = re.match(r"^(?:abstract\s+)?class\s+(\w+)", line)
        if class_match:
            class_name = class_match.group(1)
            new_class = self.language.Class() 
            new_class.setName(class_name)
            
            # Optionnel : marquer la classe comme abstraite dans l'AST
            if line.startswith("abstract"):
                new_class.is_abstract = True
                
            self.elements_map[class_name] = new_class
            self.default_package._elements.append(new_class)
            self.current_class = new_class
            return

        # 2. Détection des Interfaces (gère les éventuels espaces ou mots clés avant)
        interface_match = re.match(r"^(?:abstract\s+)?interface\s+(\w+)", line)
        if interface_match:
            interface_name = interface_match.group(1)
            new_interface = self.language.Interface()
            new_interface.setName(interface_name)
            self.elements_map[interface_name] = new_interface
            self.default_package._elements.append(new_interface)
            self.current_class = new_interface
            return

        # 3. Détection de la fin d'un bloc
        if line == "}":
            self.current_class = None
            return

        # 3. Détection de la fin d'un bloc (ex: fin d'une classe)
        if line == "}":
            self.current_class = None
            return

        # 4. Attributs et Méthodes (si on est à l'intérieur d'une classe)
        if self.current_class:
            self._parse_members(line)
            return

        # 5. Détection des Relations (Approche séparée et claire)
        
        # --- Étape A : Nettoyage de la ligne ---
        clean_line = line.split(':')[0]                 # 1. Retire la description à la fin (ex: : "linked card")
        clean_line = re.sub(r'"[^"]*"', '', clean_line) # 2. Retire les cardinalités (ex: "1", "*")
        
        # --- Étape B : Extraction basique (Mot Flèche Mot) ---
        # On cherche uniquement les caractères autorisés dans une flèche UML : < > * o | - .
        # Et on autorise des mots au milieu pour les directions (ex: -up-)
        match = re.search(r"(\w+)\s+([<>*o|\-.]+(?:[a-zA-Z]+[<>*o|\-.]+)?)\s+(\w+)", clean_line)
        
        if not match:
            return # Ce n'est pas une relation
            
        source_name = match.group(1)
        raw_arrow = match.group(2)
        dest_name = match.group(3)
        
        # --- Étape C : Nettoyage de la flèche ---
        # On supprime les éventuelles directions (ex: -up-|> devient --|>)
        clean_arrow = re.sub(r'[a-zA-Z]+', '', raw_arrow)
        relation_type = None
        
        # --- Étape D : Aiguillage explicite ---
        if clean_arrow in ("--|>", "..|>"):
            relation_type = clean_arrow
            
        elif clean_arrow in ("<|--", "<|.."): # Généralisation inversée
            relation_type = "--|>" if "-" in clean_arrow else "..|>"
            source_name, dest_name = dest_name, source_name
            
        elif clean_arrow == "*--":
            relation_type = "*--"
            
        elif clean_arrow == "--*": # Composition inversée
            relation_type = "*--"
            source_name, dest_name = dest_name, source_name
            
        elif clean_arrow == "o--":
            relation_type = "o--"
            
        elif clean_arrow == "--o": # Agrégation inversée
            relation_type = "o--"
            source_name, dest_name = dest_name, source_name
            
        elif clean_arrow in ("-->", "..>"):
            relation_type = clean_arrow
            
        elif clean_arrow in ("<--", "<.."): # Association directionnelle inversée
            relation_type = "-->" if "-" in clean_arrow else "..>"
            source_name, dest_name = dest_name, source_name
            
        elif clean_arrow in ("--", ".."): # Association bidirectionnelle
            relation_type = "--"
            
        else:
            return # Flèche non reconnue (sécurité)

        # --- Étape E : Auto-création et liaison ---
        if source_name not in self.elements_map:
            new_c = self.language.Class()
            new_c.setName(source_name)
            self.elements_map[source_name] = new_c
            self.default_package._elements.append(new_c)
            
        if dest_name not in self.elements_map:
            # Si on implémente (..|>), la destination est sûrement une interface
            if relation_type == "..|>":
                new_c = self.language.Interface()
            else:
                new_c = self.language.Class()
            new_c.setName(dest_name)
            self.elements_map[dest_name] = new_c
            self.default_package._elements.append(new_c)
            
        source_class = self.elements_map.get(source_name)
        dest_class = self.elements_map.get(dest_name)
        
        print(f"Relation détectée : {source_class._name} {relation_type} {dest_class._name}")
        self._create_relation(source_class, dest_class, relation_type)

    def _parse_members(self, line: str) -> None:
        """Parse les attributs et méthodes au sein d'une classe."""
        # Regex pour une méthode: + nom(param1: type, ...): retour
        method_match = re.match(r"([-+#~])\s*(\w+)\s*\((.*?)\)\s*(?::\s*(\w+))?", line)
        if method_match:
            vis_char, name, params_str, return_type = method_match.groups()
            
            method = self.language.Method()
            method.setName(name)
            method.setVisibility(self._get_visibility(vis_char))
            if return_type:
                method.setReturnType(return_type)
            
            # Gestion basique des paramètres
            if params_str:
                params = [p.strip() for p in params_str.split(',')]
                method.setParameters(params)
                
            self.current_class.addMethod(method)
            return

        # Regex pour un attribut: - nom: type
        attr_match = re.match(r"([-+#~])\s*(\w+)\s*:\s*(\w+)", line)
        if attr_match:
            vis_char, name, attr_type = attr_match.groups()
            
            attr = self.language.Attribute()
            attr.setName(name)
            attr.setType(attr_type)
            attr.setVisibility(self._get_visibility(vis_char))
            
            self.current_class.addAttribute(attr)

    def _get_visibility(self, char: str) -> accessSpecifier:
        if char == '+': return accessSpecifier.PUBLIC
        if char == '-': return accessSpecifier.PRIVATE
        if char == '#': return accessSpecifier.PROTECTED
        return accessSpecifier.PUBLIC

    def _create_relation(self, source: Class, dest: Class, relation_type: str) -> None:
        """Instancie la bonne relation selon le symbole PlantUML."""
        # 1. Héritage classique (extends en Java, public parent en C++)
        if relation_type == "--|>":
            relation = self.language.Generalization()
            source._parent = dest._name
            
        # 2. Implémentation d'interface (implements en Java, public interface en C++)
        elif relation_type == "..|>":
            relation = self.language.Generalization()
            source._implements = dest._name
            
        elif relation_type == "*--":
            relation = self.language.Composition()
            rel_attribute = self.language.Attribute()
            rel_attribute.setName(f"composed_{dest._name.lower()}")
            rel_attribute.setType(dest._name)
            rel_attribute.setVisibility(accessSpecifier.PRIVATE)
            source.addAttribute(rel_attribute)
            
        elif relation_type == "o--":
            relation = self.language.Agregation()
            rel_attribute = self.language.Attribute()
            rel_attribute.setName(f"ref_{dest._name.lower()}")
            rel_attribute.setType(dest._name)
            rel_attribute.setVisibility(accessSpecifier.PRIVATE)
            source.addAttribute(rel_attribute)
            
        # Association directionnelle
        elif relation_type in ("-->", "..>"):
            relation = self.language.Association()
            rel_attribute = self.language.Attribute()
            rel_attribute.setName("relation" + str(self.rel_counter))
            rel_attribute.setType(dest._name)
            source.addAttribute(rel_attribute)
            self.rel_counter += 1 
            
        # Association bidirectionnelle (Attributs chez la source ET la destination)
        elif relation_type == "--":
            relation = self.language.Association()
            
            rel_attr_src = self.language.Attribute()
            rel_attr_src.setName(f"linked_{dest._name.lower()}_{self.rel_counter}")
            rel_attr_src.setType(dest._name)
            source.addAttribute(rel_attr_src)
            
            rel_attr_dest = self.language.Attribute()
            rel_attr_dest.setName(f"linked_{source._name.lower()}_{self.rel_counter}")
            rel_attr_dest.setType(source._name)
            dest.addAttribute(rel_attr_dest)
            
            self.rel_counter += 1

        if relation:
            relation.setSource(source)
            relation.setDestination(dest)
            self.default_package._elements.append(relation)