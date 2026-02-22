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

        # 5. Détection des Relations
        # Gère les cardinalités ("1", "*") et les directions de flèches (-up-|>, --*)
        relation_match = re.search(r"(\w+)(?:\s+\".*?\")?\s+([<*o|]?-[a-zA-Z\-]*[|>o*]?)\s+(?:\".*?\")?\s+(\w+)", line)
        
        if relation_match:
            source_name = relation_match.group(1)
            raw_arrow = relation_match.group(2)
            dest_name = relation_match.group(3)
            
            # Nettoyage de la flèche : on enlève les mots de direction (ex: "-up-|>" devient "--|>")
            clean_arrow = re.sub(r'[a-zA-Z]+', '', raw_arrow)
            
            # Gestion des flèches inversées (ex: A --* B équivaut à B *-- A)
            if clean_arrow == "--*":
                clean_arrow = "*--"
                source_name, dest_name = dest_name, source_name
            elif clean_arrow == "--o":
                clean_arrow = "o--"
                source_name, dest_name = dest_name, source_name
            elif clean_arrow == "<--":
                clean_arrow = "-->"
                source_name, dest_name = dest_name, source_name
            elif clean_arrow == "<|--":
                clean_arrow = "--|>"
                source_name, dest_name = dest_name, source_name

            source_class = self.elements_map.get(source_name)
            dest_class = self.elements_map.get(dest_name)
            
            if source_class and dest_class:
                print(f"Relation détectée : {source_class._name} {clean_arrow} {dest_class._name}")
                self._create_relation(source_class, dest_class, clean_arrow)

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
        """Instancie la bonne relation selon le symbole PlantUML et met à jour les classes."""
        relation = None
        if relation_type == "--|>":
            relation = self.language.Generalization()
            # Héritage : Ce n'est pas un attribut classique.
            # On ajoute dynamiquement une propriété `_parent` à la classe source.
            # (Il faudra que ta méthode toCode() l'utilise pour générer 'class A : public B')
            source._parent = dest._name
            
        elif relation_type == "*--":
            relation = self.language.Composition()
            # Composition : La classe source (le composite) est responsable du cycle de vie de la destination.
            # On lui ajoute un attribut privé.
            rel_attribute = self.language.Attribute()
            rel_attribute.setName(f"composed_{dest._name.lower()}")
            rel_attribute.setType(dest._name)
            rel_attribute.setVisibility(accessSpecifier.PRIVATE)
            source.addAttribute(rel_attribute)
            
        elif relation_type == "o--":
            relation = self.language.Agregation()
            # Agrégation : La classe source contient une référence vers la destination.
            rel_attribute = self.language.Attribute()
            rel_attribute.setName(f"ref_{dest._name.lower()}")
            rel_attribute.setType(dest._name) # Dans un cas réel C++, ça pourrait être un pointeur ou une référence
            rel_attribute.setVisibility(accessSpecifier.PRIVATE)
            source.addAttribute(rel_attribute)
            
        elif relation_type == "-->":
            relation = self.language.Association()
            rel_attribute = self.language.Attribute()
            rel_attribute.setName("relation" + str(self.rel_counter))
            rel_attribute.setType(dest._name)
            source.addAttribute(rel_attribute)
            # Incrémentation du compteur pour éviter les doublons de noms
            self.rel_counter += 1 
            
        if relation:
            relation.setSource(source)
            relation.setDestination(dest)
            self.default_package._elements.append(relation)