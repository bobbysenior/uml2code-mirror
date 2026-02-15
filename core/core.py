from __future__ import annotations
from abc import ABC, abstractmethod
from enum import Enum as PyEnum
from typing import List, Optional

# --- Enums ---

class AccessSpecifier(PyEnum):
    PUBLIC = "+"
    PRIVATE = "-"
    PROTECTED = "#"

# --- Base Abstraite ---

class CodableElement(ABC):
    def __init__(self, comment: str = ""):
        self._comment = comment

    @abstractmethod
    def to_code(self) -> str:
        """Les classes qui implémentent cette interface peuvent être converties en code."""
        pass

# --- Composants de Classe ---

class Attribute(CodableElement):
    def __init__(self, name: str = "", type_name: str = "", visibility: AccessSpecifier = AccessSpecifier.PUBLIC):
        super().__init__()
        self._name = name
        self._type = type_name
        self._visibility = visibility

    def set_name(self, name: str) -> None:
        self._name = name

    def set_type(self, type_name: str) -> None:
        self._type = type_name

    def set_visibility(self, vis: AccessSpecifier) -> None:
        self._visibility = vis

    def to_code(self) -> str:
        # Implémentation spécifique au langage cible à définir
        pass

class Method(CodableElement):
    def __init__(self, name: str = "", visibility: AccessSpecifier = AccessSpecifier.PUBLIC, 
                 parameters: List[str] = None, return_type: str = "void"):
        super().__init__()
        self._name = name
        self._visibility = visibility
        self._parameters = parameters if parameters else []
        self._return_type = return_type

    def set_name(self, name: str) -> None:
        self._name = name

    def set_visibility(self, vis: AccessSpecifier) -> None:
        self._visibility = vis

    def set_parameters(self, p: List[str]) -> None:
        self._parameters = p

    def set_return_type(self, return_type: str) -> None:
        self._return_type = return_type

    def to_code(self) -> str:
        pass

# --- Structures de Données ---

class Class(CodableElement):
    def __init__(self, id_num: int = 0, name: str = "", is_abstract: bool = False):
        super().__init__()
        self._id = id_num
        self._name = name
        self._is_abstract = is_abstract
        self._attributes: List[Attribute] = []
        self._methods: List[Method] = []

    def set_id(self, id_num: int) -> None:
        self._id = id_num

    def set_name(self, name: str) -> None:
        self._name = name

    def set_abstract(self, is_abstract: bool) -> None:
        self._is_abstract = is_abstract

    def add_attribute(self, attr: Attribute) -> None:
        self._attributes.append(attr)

    def add_method(self, meth: Method) -> None:
        self._methods.append(meth)

    def to_code(self) -> str:
        pass

class Interface(Class):
    def to_code(self) -> str:
        pass

class Enum(CodableElement):
    def __init__(self, name: str = "", elements: List[str] = None):
        super().__init__()
        self._name = name
        self._elements = elements if elements else []

    def set_name(self, name: str) -> None:
        self._name = name

    def set_elements(self, elements: List[str]) -> None:
        self._elements = elements

    def to_code(self) -> str:
        pass

# --- Relations ---

class Relation(CodableElement):
    def __init__(self):
        super().__init__()
        self._role: str = ""
        self._semantics: str = ""
        self._source: Optional[Class] = None
        self._destination: Optional[Class] = None

    def set_source(self, source: Class) -> None:
        self._source = source

    def set_destination(self, destination: Class) -> None:
        self._destination = destination

    def set_role(self, role: str) -> None:
        self._role = role

    def set_semantics(self, text: str) -> None:
        self._semantics = text

    def to_code(self) -> str:
        pass

class CardinalityRelation(Relation):
    def __init__(self):
        super().__init__()
        self._source_cardinality: str = ""
        self._destination_cardinality: str = ""

    def set_source_cardinality(self, cap: str) -> None:
        self._source_cardinality = cap

    def set_destination_cardinality(self, cap: str) -> None:
        self._destination_cardinality = cap

class Generalization(Relation): pass
class Association(Relation): pass
class Implementation(Relation): pass
class Agregation(CardinalityRelation): pass
class Composition(CardinalityRelation): pass

# --- Documentation et Conteneur ---

class Note(CodableElement):
    def __init__(self, body: str = ""):
        super().__init__()
        self._body = body
        self._target: Optional[CodableElement] = None

    def set_body(self, text: str) -> None:
        self._body = text

    def set_target(self, target: CodableElement) -> None:
        self._target = target

    def to_code(self) -> str:
        pass

class ClassDiagram:
    def __init__(self):
        self._elements: List[CodableElement] = []

    def add_element(self, element: CodableElement) -> None:
        self._elements.append(element)