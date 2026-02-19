from abc import ABC, abstractmethod
from enum import Enum as PyEnum
from typing import List, Optional

# --- Enums ---

class accessSpecifier(PyEnum):
    PUBLIC = "PUBLIC"
    PRIVATE = "PRIVATE"
    PROTECTED = "PROTECTED"

# --- Interfaces & Abstract Classes ---

class Language(ABC):
    """
    Interface faisant le pont entre le parser et les implémentations spécifiques des langages.
    Chaque propriété retourne le type/la classe concrète à instancier.
    """
    @property
    @abstractmethod
    def Class(self) -> type['Class']:
        pass

    @property
    @abstractmethod
    def Attribute(self) -> type['Attribute']:
        pass

    @property
    @abstractmethod
    def Method(self) -> type['Method']:
        pass

    @property
    @abstractmethod
    def Enum(self) -> type['Enum']:
        pass

    @property
    @abstractmethod
    def Interface(self) -> type['Interface']:
        pass

    @property
    @abstractmethod
    def Association(self) -> type['Association']:
        pass

    @property
    @abstractmethod
    def Agregation(self) -> type['Agregation']:
        pass

    @property
    @abstractmethod
    def Generalization(self) -> type['Generalization']:
        pass

    @property
    @abstractmethod
    def Composition(self) -> type['Composition']:
        pass

class CodableElement(ABC):
    def __init__(self):
        self._id: int = 0
        self._comment: str = ""

    @abstractmethod
    def toCode(self) -> str:
        pass

# --- Core Elements ---

class Package:
    def __init__(self):
        self._id: int = 0
        self._elements: List[CodableElement] = [] # Package "1" o-- "*" CodableElement

    def toCode(self) -> str:
        pass

class ClassDiagram:
    def __init__(self):
        self._id: int = 0
        self._packages: List[Package] = [] # ClassDiagram "1" o-- "*" Package

    def toCode(self) -> str:
        pass

# --- Modélisation détaillée ---

class Class(CodableElement):
    def __init__(self):
        super().__init__()
        self._id: int = 0
        self._name: str = ""
        self._isAbstract: bool = False
        self._fileName: str = ""
        self._attributes: List['Attribute'] = [] # Attribute "*" --* "1" Class
        self._methods: List['Method'] = []       # Method "*" --* "1" Class

    def setId(self, id: int) -> None:
        self._id = id

    def setName(self, name: str) -> None:
        self._name = name

    def setAbstract(self, isAbstract: bool) -> None:
        self._isAbstract = isAbstract

    def setFilename(self, name: str) -> None:
        self._fileName = name

    def addAttribute(self, attr: 'Attribute') -> None:
        self._attributes.append(attr)

    def addMethod(self, meth: 'Method') -> None:
        self._methods.append(meth)

class Method(CodableElement):
    def __init__(self):
        super().__init__()
        self._name: str = ""
        self._visibility: accessSpecifier = accessSpecifier.PUBLIC
        self._parameters: List[str] = []
        self._returnType: str = ""

    def setName(self, name: str) -> None:
        self._name = name

    def setVisibility(self, vis: accessSpecifier) -> None:
        self._visibility = vis

    def setParameters(self, p: List[str]) -> None:
        self._parameters = p

    def setReturnType(self, type: str) -> None:
        self._returnType = type

class Attribute(CodableElement):
    def __init__(self):
        super().__init__()
        self._name: str = ""
        self._type: str = ""
        self._visibility: accessSpecifier = accessSpecifier.PUBLIC

    def setName(self, name: str) -> None:
        self._name = name

    def setType(self, type_: str) -> None:
        self._type = type_

    def setVisibility(self, vis: accessSpecifier) -> None:
        self._visibility = vis

class Enum(CodableElement):
    def __init__(self):
        super().__init__()
        self._name: str = ""
        self._filename: str = ""
        self._elements: List[str] = []

    def setName(self, name: str) -> None:
        self._name = name

    def setFilename(self, name: str) -> None:
        self._filename = name

    def setElements(self, elements: List[str]) -> None:
        self._elements = elements

class Interface(Class):
    pass

class Note(CodableElement):
    def __init__(self):
        super().__init__()
        self._body: str = ""
        self._target: Optional[CodableElement] = None # Note -- CodableElement : target >

    def setBody(self, text: str) -> None:
        self._body = text

    def setTarget(self, target: CodableElement) -> None:
        self._target = target

# --- Relations ---

class Relation(CodableElement):
    def __init__(self):
        super().__init__()
        self._semantics: str = ""
        self._source: Optional[Class] = None      # Relation "*" --> "2" Class
        self._destination: Optional[Class] = None # Relation "*" --> "2" Class

    def setSource(self, source: Class) -> None:
        self._source = source

    def setDestination(self, destination: Class) -> None:
        self._destination = destination

    def setSemantics(self, text: str) -> None:
        self._semantics = text

class CardinalityRelation(Relation):
    def __init__(self):
        super().__init__()
        self._sourceRole: str = ""
        self._sourceCardinality: str = ""
        self._destinationRole: str = ""
        self._destinationCardinality: str = ""

    def setSourceRole(self, role: str) -> None:
        self._sourceRole = role

    def setSourceCardinality(self, cap: str) -> None:
        self._sourceCardinality = cap

    def setDestinationRole(self, role: str) -> None:
        self._destinationRole = role

    def setDestinationCardinality(self, cap: str) -> None:
        self._destinationCardinality = cap

class Generalization(Relation):
    pass

class Implementation(Relation):
    pass

class Association(CardinalityRelation):
    pass

class Agregation(CardinalityRelation):
    pass

class Composition(CardinalityRelation):
    pass