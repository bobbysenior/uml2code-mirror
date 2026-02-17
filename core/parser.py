### core/parser.py
import re
from typing import Optional, List, Dict
from core.core import ClassDiagram, ModelFactory, AccessSpecifier, Class, Interface, Enum

class PlantUMLParser:
    def __init__(self, factory: ModelFactory):
        self.factory = factory
        self.diagram = ClassDiagram()
        self.current_class: Optional[Class] = None
        self.classes_map: Dict[str, Class] = {} # Pour retrouver les classes par nom

    def parse_file(self, filepath: str) -> ClassDiagram:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.readlines()
        return self.parse_lines(content)

    def parse_lines(self, lines: List[str]) -> ClassDiagram:
        for line in lines:
            line = line.strip()
            if not line or line.startswith("'") or line == "@startuml" or line == "@enduml":
                continue
            
            self._process_line(line)
        
        return self.diagram

    def _process_line(self, line: str):
        # 1. Détection de fin de classe
        if line == "}":
            self.current_class = None
            return

        # 2. Détection Début de Classe / Interface / Enum
        # Regex: (abstract)? class|interface|enum Name ({)?
        class_pattern = re.compile(r'^(abstract\s+)?(class|interface|enum)\s+(\w+)(?:\s*\{)?')
        match = class_pattern.match(line)
        if match:
            is_abstract = match.group(1) is not None
            type_str = match.group(2)
            name = match.group(3)
            
            if type_str == "class":
                new_element = self.factory.create_class(name, is_abstract)
            elif type_str == "interface":
                new_element = self.factory.create_interface(name)
            elif type_str == "enum":
                new_element = self.factory.create_enum(name)
            
            self.diagram.add_element(new_element)
            self.current_class = new_element
            self.classes_map[name] = new_element
            return

        # 3. Détection des Membres (si on est dans une classe)
        if self.current_class:
            if isinstance(self.current_class, Enum):
                # Pour les enums, on prend juste le mot
                # Ex: VAL1
                if re.match(r'^\w+$', line):
                    self.current_class.add_element(line)
                return
            
            # Attributs et Méthodes
            # Syntaxe PlantUML: {visibility} name : type  OU  {visibility} name(params) : type
            
            # A. Méthode : detecte parenthèses
            method_pattern = re.compile(r'^([+\-#~])\s*(\w+)\s*\((.*?)\)\s*:\s*(\w+)')
            m_match = method_pattern.match(line)
            if m_match:
                vis_symbol = m_match.group(1)
                name = m_match.group(2)
                params_str = m_match.group(3)
                ret_type = m_match.group(4)
                
                method = self.factory.create_method(name, self._get_visibility(vis_symbol), ret_type)
                
                # Gestion simple des paramètres (ex: "id: int, val: string")
                if params_str:
                    params = [p.strip() for p in params_str.split(',')]
                    method.set_parameters(params) # Suppose que Method a set_parameters
                
                self.current_class.add_method(method)
                return

            # B. Attribut
            attr_pattern = re.compile(r'^([+\-#~])\s*(\w+)\s*:\s*(\w+)')
            a_match = attr_pattern.match(line)
            if a_match:
                vis_symbol = a_match.group(1)
                name = a_match.group(2)
                type_name = a_match.group(3)
                
                attr = self.factory.create_attribute(name, type_name, self._get_visibility(vis_symbol))
                self.current_class.add_attribute(attr)
                return

        # 4. Détection Relations (Héritage simple)
        # Ex: Child -up-|> Parent  OU  Child --|> Parent OU Child extends Parent
        # Simplification: on cherche juste le motif d'héritage <|-- ou --|>
        
        # Cas: Parent <|-- Child (Parent est étendu par Child)
        inherit_pattern_1 = re.compile(r'(\w+)\s+<\|(?:--|\.\.)\s+(\w+)')
        rel_match_1 = inherit_pattern_1.search(line)
        if rel_match_1:
            parent_name = rel_match_1.group(1)
            child_name = rel_match_1.group(2)
            self._add_inheritance(child_name, parent_name)
            return

        # Cas: Child --|> Parent (Child étend Parent)
        inherit_pattern_2 = re.compile(r'(\w+)\s+(?:--|\.\.)\|>\s+(\w+)')
        rel_match_2 = inherit_pattern_2.search(line)
        if rel_match_2:
            child_name = rel_match_2.group(1)
            parent_name = rel_match_2.group(2)
            self._add_inheritance(child_name, parent_name)
            return

    def _add_inheritance(self, child_name: str, parent_name: str):
        # On stocke l'info. Si l'objet Child existe déjà, on met à jour.
        # Sinon, il faudra gérer l'ordre de définition (ou post-traitement).
        # Ici on suppose que les classes sont définies ou on utilise la map.
        if child_name in self.classes_map:
            self.classes_map[child_name].add_parent(parent_name)
        else:
            # Cas où la relation est déclarée avant la classe (plus complexe, ignoré pour l'instant)
            pass

    def _get_visibility(self, symbol: str) -> AccessSpecifier:
        if symbol == "-": return AccessSpecifier.PRIVATE
        if symbol == "#": return AccessSpecifier.PROTECTED
        if symbol == "~": return AccessSpecifier.PACKAGE
        return AccessSpecifier.PUBLIC