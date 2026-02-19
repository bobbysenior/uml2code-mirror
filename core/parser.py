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

    def parse_file(self, filepath: str) -> ClassDiagram:
        with open(filepath, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            
        for line in lines:
            self._parse_line(line.strip())
            
        return self.diagram

    def _parse_line(self, line: str) -> None:
        # Ignorer les lignes vides ou les commentaires
        if not line or line.startswith("'") or line == "@startuml" or line == "@enduml":
            return

        # 1. Détection des Classes
        class_match = re.match(r"class\s+(\w+)", line)
        if class_match:
            class_name = class_match.group(1)
            # Utilisation de la factory pour instancier la bonne classe selon le langage
            new_class = self.language.Class() 
            new_class.setName(class_name)
            self.elements_map[class_name] = new_class
            self.default_package._elements.append(new_class)
            self.current_class = new_class
            return

        # 2. Détection des Interfaces
        interface_match = re.match(r"interface\s+(\w+)", line)
        if interface_match:
            interface_name = interface_match.group(1)
            new_interface = self.language.Interface()
            new_interface.setName(interface_name)
            self.elements_map[interface_name] = new_interface
            self.default_package._elements.append(new_interface)
            self.current_class = new_interface
            return

        # 3. Détection de la fin d'un bloc (ex: fin d'une classe)
        if line == "}":
            self.current_class = None
            return

        # 4. Attributs et Méthodes (si on est à l'intérieur d'une classe)
        if self.current_class:
            self._parse_members(line)
            return

        # 5. Détection des Relations (simplifié pour l'exemple)
        # Ex: ClassA --|> ClassB (Généralisation)
        relation_match = re.match(r"(\w+)\s+(--\|>|\*--|o--|-->)\s+(\w+)", line)
        if relation_match:
            source_name = relation_match.group(1)
            relation_type = relation_match.group(2)
            dest_name = relation_match.group(3)
            
            source_class = self.elements_map.get(source_name)
            dest_class = self.elements_map.get(dest_name)
            
            if source_class and dest_class:
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
        relation = None
        
        if relation_type == "--|>":
            relation = self.language.Generalization()
        elif relation_type == "*--":
            relation = self.language.Composition()
        elif relation_type == "o--":
            relation = self.language.Agregation()
        elif relation_type == "-->":
            relation = self.language.Association()
            
        if relation:
            relation.setSource(source)
            relation.setDestination(dest)
            self.default_package._elements.append(relation)