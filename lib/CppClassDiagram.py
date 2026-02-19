from core import (
    Language, Class, Attribute, Method, Enum, Interface,
    Association, Agregation, Generalization, Composition
)

# --- Spécialisation des éléments principaux ---

class CppClass(Class):
    def toCode(self) -> str:
        # TODO: Implémenter la génération de code C++ pour une classe
        pass

class CppAttribute(Attribute):
    def toCode(self) -> str:
        # TODO: Implémenter la génération de code C++ pour un attribut
        pass

class CppMethod(Method):
    def toCode(self) -> str:
        # TODO: Implémenter la génération de code C++ pour une méthode
        pass

class CppEnum(Enum):
    def toCode(self) -> str:
        # TODO: Implémenter la génération de code C++ pour une énumération
        pass

class CppInterface(Interface):
    def toCode(self) -> str:
        # TODO: Implémenter la génération de code C++ pour une interface
        # Note : En C++, une interface est généralement une classe avec uniquement des méthodes virtuelles pures.
        pass

# --- Spécialisation des relations ---

class CppAssociation(Association):
    def toCode(self) -> str:
        # TODO: Implémenter la génération de code C++ pour une association
        pass

class CppAgregation(Agregation):
    def toCode(self) -> str:
        # TODO: Implémenter la génération de code C++ pour une agrégation (ex: pointeur ou référence)
        pass

class CppGeneralization(Generalization):
    def toCode(self) -> str:
        # TODO: Implémenter la génération de code C++ pour un héritage
        pass

class CppComposition(Composition):
    def toCode(self) -> str:
        # TODO: Implémenter la génération de code C++ pour une composition (ex: instanciation par valeur)
        pass

# --- Implémentation de l'interface Language (Abstract Factory) ---

class Cpp(Language):
    """
    Factory concrète pour le langage C++.
    Retourne les classes spécifiques au C++ pour chaque élément de modélisation.
    """
    
    @property
    def Class(self) -> type[CppClass]:
        return CppClass

    @property
    def Attribute(self) -> type[CppAttribute]:
        return CppAttribute

    @property
    def Method(self) -> type[CppMethod]:
        return CppMethod

    @property
    def Enum(self) -> type[CppEnum]:
        return CppEnum

    @property
    def Interface(self) -> type[CppInterface]:
        return CppInterface

    @property
    def Association(self) -> type[CppAssociation]:
        return CppAssociation

    @property
    def Agregation(self) -> type[CppAgregation]:
        return CppAgregation

    @property
    def Generalization(self) -> type[CppGeneralization]:
        return CppGeneralization

    @property
    def Composition(self) -> type[CppComposition]:
        return CppComposition