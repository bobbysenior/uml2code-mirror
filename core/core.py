from __future__ import annotations
from abc import ABC, abstractmethod
from enum import Enum as PyEnum
from typing import List, Optional

# --- Enums (Conforme au diagramme) ---

class AccessSpecifier(PyEnum):
    PUBLIC = "+"
    PRIVATE = "-"
    PROTECTED = "#"
    # PACKAGE = "~" # Ajouté par nécessité pratique pour le parser, bien que non explicite sur le diagramme

# --- Base Abstraite ---

class CodableElement(ABC):
    """
    Correspond à abstract class CodableElement
    """
    def __init__(self, comment: str = ""):
        self._comment: str = comment

    @abstractmethod
    def to_code(self) -> str:
        """+ toCode(): String"""
        pass

# --- Composants de Classe ---

class Attribute(CodableElement):
    """
    Correspond à abstract class Attribute
    """
    def __init__(self, name: str = "", type_name: str = "", visibility: AccessSpecifier = AccessSpecifier.PUBLIC):
        super().__init__()
        self._name: str = name
        self._type: str = type_name
        self._visibility: AccessSpecifier = visibility

    # + setName(name: String): void
    def set_name(self, name: str) -> None:
        self._name = name

    # + setType(type: String): void
    def set_type(self, type_name: str) -> None:
        self._type = type_name

    # + setVisibility(vis: accessSpecifier): void
    def set_visibility(self, vis: AccessSpecifier) -> None:
        self._visibility = vis

    def to_code(self) -> str:
        pass

class Method(CodableElement):
    """
    Correspond à abstract class Method
    """
    def __init__(self, name: str = "", visibility: AccessSpecifier = AccessSpecifier.PUBLIC, 
                 parameters: List[str] = None, return_type: str = "void"):
        super().__init__()
        self._name: str = name
        self._visibility: AccessSpecifier = visibility
        self._parameters: List[str] = parameters if parameters else []
        self._return_type: str = return_type

    # + setName(name: String): void
    def set_name(self, name: str) -> None:
        self._name = name

    # + setVisibility(vis: accessSpecifier): void
    def set_visibility(self, vis: AccessSpecifier) -> None:
        self._visibility = vis

    # + setParameters(p: String[]): void
    def set_parameters(self, p: List[str]) -> None:
        self._parameters = p

    # + setReturnType(type: String): void
    def set_return_type(self, type_name: str) -> None:
        self._return_type = type_name

    def to_code(self) -> str:
        pass

# --- Structures de Données ---

class Class(CodableElement):
    """
    Correspond à abstract class Class
    """
    def __init__(self, id_num: int = 0, name: str = "", is_abstract: bool = False):
        super().__init__()
        self._id: int = id_num
        self._name: str = name
        self._is_abstract: bool = is_abstract
        
        # Relations de composition définies dans le diagramme :
        # Attribute "*" --* "1" Class
        # Method "*" --* "1" Class
        self._attributes: List[Attribute] = []
        self._methods: List[Method] = []
        
        # Champs techniques (hors diagramme visuel mais nécessaires pour la génération de code via parser)
        self._parents: List[str] = [] 
        self._includes: List[str] = []

    # + setId(id: int): void
    def set_id(self, id_num: int) -> None:
        self._id = id_num

    # + setName(name: String): void
    def set_name(self, name: str) -> None:
        self._name = name

    # + setAbstract(isAbstract: boolean): void
    def set_abstract(self, is_abstract: bool) -> None:
        self._is_abstract = is_abstract

    # + addAttribute(attr: Attribute): void
    def add_attribute(self, attr: Attribute) -> None:
        self._attributes.append(attr)

    # + addMethod(meth: Method): void
    def add_method(self, meth: Method) -> None:
        self._methods.append(meth)

    # Méthodes utilitaires pour le parser/générateur (Implémentation technique)
    def add_parent(self, parent_name: str) -> None:
        self._parents.append(parent_name)
    
    def add_include(self, include_name: str) -> None:
        if include_name not in self._includes:
            self._includes.append(include_name)

    def to_code(self) -> str:
        pass

class Interface(Class):
    """
    Correspond à abstract class Interface extends Class
    """
    def to_code(self) -> str:
        pass

class Enum(CodableElement):
    """
    Correspond à abstract class Enum
    """
    def __init__(self, name: str = "", elements: List[str] = None):
        super().__init__()
        self._name: str = name
        self._elements: List[str] = elements if elements else []

    # + setName(name: String): void
    def set_name(self, name: str) -> None:
        self._name = name

    # + setElements(elements: String[]): void
    def set_elements(self, elements: List[str]) -> None:
        self._elements = elements

    # Helper pour le parser
    def add_element(self, element: str) -> None:
        self._elements.append(element)

    def to_code(self) -> str:
        pass

# --- Relations ---

class Relation(CodableElement):
    """
    Correspond à abstract class Relation
    """
    def __init__(self):
        super().__init__()
        self._role: str = ""
        self._semantics: str = "" # Note: sementics dans le diagramme, corrigé en semantics
        self._source: Optional[Class] = None
        self._destination: Optional[Class] = None

    # + setSource(source: Class): void
    def set_source(self, source: Class) -> None:
        self._source = source

    # + setDestination(destination: Class): void
    def set_destination(self, destination: Class) -> None:
        self._destination = destination

    # + setRole(role: String): void
    def set_role(self, role: str) -> None:
        self._role = role

    # + setSemantics(text: String): void
    def set_semantics(self, text: str) -> None:
        self._semantics = text

    def to_code(self) -> str:
        pass

class CardinalityRelation(Relation):
    """
    Correspond à abstract class CardinalityRelation extends Relation
    """
    def __init__(self):
        super().__init__()
        self._source_cardinality: str = ""
        self._destination_cardinality: str = ""

    # + setSourceCardinality(cap: String): void
    def set_source_cardinality(self, cap: str) -> None:
        self._source_cardinality = cap

    # + setDestinationCardinality(cap: String): void
    def set_destination_cardinality(self, cap: str) -> None:
        self._destination_cardinality = cap

# Relations concrètes définies dans le package "together"
class Generalization(Relation): pass
class Association(Relation): pass
class Implementation(Relation): pass

class Agregation(CardinalityRelation): pass
class Composition(CardinalityRelation): pass

# --- Documentation et Conteneur ---

class Note(CodableElement):
    """
    Correspond à abstract class Note
    """
    def __init__(self, body: str = ""):
        super().__init__()
        self._body: str = body
        self._target: Optional[CodableElement] = None

    # + setBody(text: String): void
    def set_body(self, text: str) -> None:
        self._body = text

    # + setTarget(target: Class): void
    # Le diagramme dit setTarget(target: Class) mais la relation visuelle pointe vers CodableElement.
    # On utilise CodableElement pour plus de flexibilité (note sur methode ou classe).
    def set_target(self, target: CodableElement) -> None:
        self._target = target

    def to_code(self) -> str:
        pass

class ClassDiagram:
    """
    Correspond à abstract class ClassDiagram
    Aggrège CodableElement (*)
    """
    def __init__(self):
        self._elements: List[CodableElement] = []

    # Helper pour l'accès public (property pythonique) ou via méthode
    @property
    def elements(self) -> List[CodableElement]:
        return self._elements

    def add_element(self, element: CodableElement) -> None:
        self._elements.append(element)


class Language(ABC):
    """
    Interface qui permet à chaque langage de précicer ses structures
    """
    Class = None
    Attribute
    Method
    Enum
    Interface
    Association 
    Agregation 
    Generalization 
    Composition 
