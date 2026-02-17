import re
from typing import Optional, List, Dict
from core.core import ClassDiagram, ModelFactory, AccessSpecifier, Class, Interface, Enum

class PlantUMLParser:
    def __init__(self, factory: ModelFactory):
        self.factory = factory
        self.diagram = ClassDiagram()
        self.current_class: Optional[Class] = None
        self.classes_map: Dict[str, Class] = {} 
        self.relations_buffer = [] 

    def parse_file(self, filepath: str) -> ClassDiagram:
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.readlines()
            
            self.parse_lines(content)
            self._resolve_relations_to_attributes()
            
            return self.diagram
        except Exception as e:
            print(f"Erreur critique lors du parsing : {e}")
            return self.diagram

    def parse_lines(self, lines: List[str]) -> ClassDiagram:
        for line in lines:
            # 1. Nettoyage : On enlève les commentaires (ce qui suit ') et les espaces
            line = line.split("'")[0].strip()
            
            if not line or line == "@startuml" or line == "@enduml":
                continue
            
            self._process_line(line)
        return self.diagram

    def _process_line(self, line: str):
        if line == "}":
            self.current_class = None
            return

        # --- Detection Classes ---
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

        # --- Detection Membres (si dans une classe) ---
        if self.current_class:
            if isinstance(self.current_class, Enum):
                # Pour les enums, on accepte des mots simples ou avec virgule
                if re.match(r'^\w+,?$', line):
                    self.current_class.add_element(line.replace(',', ''))
                return

            # Méthode : nom(params) : type (optionnel)
            method_pattern = re.compile(r'^([+\-#~])\s*(\w+)\s*\((.*?)\)(?:\s*:\s*(\w+))?')
            m_match = method_pattern.match(line)
            if m_match:
                vis_symbol = m_match.group(1)
                name = m_match.group(2)
                params_str = m_match.group(3)
                ret_type = m_match.group(4) if m_match.group(4) else "void"
                
                method = self.factory.create_method(name, self._get_visibility(vis_symbol), ret_type)
                if params_str:
                    params = [p.strip() for p in params_str.split(',')]
                    method.set_parameters(params)
                self.current_class.add_method(method)
                return

            # Attribut : nom : type
            attr_pattern = re.compile(r'^([+\-#~])\s*(\w+)\s*:\s*(\w+)')
            a_match = attr_pattern.match(line)
            if a_match:
                vis_symbol = a_match.group(1)
                name = a_match.group(2)
                type_name = a_match.group(3)
                attr = self.factory.create_attribute(name, type_name, self._get_visibility(vis_symbol))
                self.current_class.add_attribute(attr)
                return

        # --- Detection Relations ---
        # Format supporté : Class1 "card1" arrow "card2" Class2 : label
        # Regex améliorée pour ignorer les espaces superflus et gérer les guillemets optionnels
        rel_pattern = re.compile(r'^(\w+)(?:\s+"([\d\.\*]+)")?\s+([<o\*]?[-.]+[>o\*]?)\s+(?:\s+"([\d\.\*]+)")?\s+(\w+)(?:\s+:\s+"?([^"]+)"?)?')
        rel_match = rel_pattern.search(line)
        
        if rel_match:
            src_name = rel_match.group(1)
            src_card = rel_match.group(2)
            arrow = rel_match.group(3)
            dest_card = rel_match.group(4)
            dest_name = rel_match.group(5)
            label = rel_match.group(6) # Peut être None
            
            # Gestion Héritage spécial
            if arrow in ["<|--", "<|.."]: # Dest est Parent (notation inverse)
                self._add_inheritance(dest_name, src_name) # Correction sens
            elif arrow in ["--|>", "..|>"]: # Src est Enfant
                self._add_inheritance(src_name, dest_name)
            else:
                self.relations_buffer.append({
                    'src': src_name, 'src_card': src_card,
                    'arrow': arrow,
                    'dest': dest_name, 'dest_card': dest_card,
                    'label': label
                })
            return

    def _add_inheritance(self, child_name: str, parent_name: str):
        if child_name in self.classes_map:
            self.classes_map[child_name].add_parent(parent_name)

    def _get_visibility(self, symbol: str) -> AccessSpecifier:
        if symbol == "-": return AccessSpecifier.PRIVATE
        if symbol == "#": return AccessSpecifier.PROTECTED
        if symbol == "~": return AccessSpecifier.PACKAGE
        return AccessSpecifier.PUBLIC

    def _resolve_relations_to_attributes(self):
        for rel in self.relations_buffer:
            src = self.classes_map.get(rel['src'])
            dest = self.classes_map.get(rel['dest'])
            
            if not src or not dest: 
                continue

            arrow = rel['arrow']
            label = rel['label'] if rel['label'] else ""
            
            # 1. Direction Src -> Dest (Src possède Dest)
            # Flèches : -->, o--, *--, -- (bidirectionnel implicite si pas de <)
            if ">" in arrow or "o" in arrow or "*" in arrow or arrow == "--":
                # Vérifier qu'on n'est pas dans le cas "Source <|-- Dest" qui est un héritage
                if not ("<|" in arrow):
                    attr_name = self._generate_attr_name(dest._name, label, rel['dest_card'])
                    attr_type = self._determine_type(dest._name, rel['dest_card'])
                    
                    # Eviter les doublons si l'attribut existe déjà
                    if not any(a._name == attr_name for a in src._attributes):
                        attr = self.factory.create_attribute(attr_name, attr_type, AccessSpecifier.PRIVATE)
                        src.add_attribute(attr)
                        if hasattr(src, 'add_include'):
                            src.add_include(dest._name)

            # 2. Direction Dest -> Src (Dest possède Src)
            # Flèches : <--, --o, --*, -- (bidirectionnel)
            if "<" in arrow or arrow == "--":
                 if not ("|>" in arrow):
                    attr_name = self._generate_attr_name(src._name, label, rel['src_card'])
                    attr_type = self._determine_type(src._name, rel['src_card'])
                    
                    if not any(a._name == attr_name for a in dest._attributes):
                        attr = self.factory.create_attribute(attr_name, attr_type, AccessSpecifier.PRIVATE)
                        dest.add_attribute(attr)
                        if hasattr(dest, 'add_include'):
                            dest.add_include(src._name)

    def _determine_type(self, class_name: str, cardinality: str) -> str:
        if cardinality and ("*" in cardinality or ".." in cardinality):
            # Vérification : si c'est 1..1, ce n'est pas une liste
            if cardinality == "1..1":
                return class_name
            return f"List<{class_name}>"
        return class_name

    def _generate_attr_name(self, class_name: str, label: str, cardinality: str) -> str:
        base = ""
        if label:
            base = label.replace(" ", "_")
        else:
            base = class_name[0].lower() + class_name[1:] # camelCase simple
        
        # Pluralisation si liste
        if cardinality and ("*" in cardinality or (".." in cardinality and cardinality != "1..1")):
            if not base.endswith('s'):
                base += "s"
        return base