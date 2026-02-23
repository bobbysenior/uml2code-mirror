"""
Module:       JavaClassDiagram
Project:      uml2code
Author:       Reichmann Galy
AI Assistant: Claude Opus 4.6 (Anthropic)
License:      GPL3.0

Description:
    Implémentation concrète de l'Abstract Factory pour le langage Java. Traduit le modèle UML en code Java 
    en distinguant notamment l'héritage (extends) et l'implémentation d'interfaces (implements).

Dependencies:
    - core.core
"""
from core.core import (
    Language, Class, Attribute, Method, Enum, Interface,
    Association, Agregation, Generalization, Composition, accessSpecifier
)

# Correspondance entre les niveaux de visibilité et les mots-clés Java
VISIBILITY_MAP = {
    accessSpecifier.PUBLIC:    "public",
    accessSpecifier.PRIVATE:   "private",
    accessSpecifier.PROTECTED: "protected",
}

def get_visibility(vis) -> str:
    return VISIBILITY_MAP.get(vis, "private")

def cardinality_is_multiple(card: str) -> bool:
    """Détermine si une cardinalité représente une collection (0..*, 1..*, etc.)"""
    if not card:
        return False
    return "*" in card or "n" in card.lower()


# ---------------------------------------------------------------------------
# Eléments de base
# ---------------------------------------------------------------------------

class JavaAttribute(Attribute):
    def toCode(self) -> str:
        keyword = get_visibility(self._visibility)
        return f"{keyword} {self._type} {self._name};"


class JavaMethod(Method):
    def toCode(self) -> str:
        keyword = get_visibility(self._visibility)
        ret     = self._returnType or "void"
        args    = ", ".join(self._parameters) if self._parameters else ""
        body    = "\n        // TODO: à implémenter\n    "
        return f"{keyword} {ret} {self._name}({args}) {{{body}}}"


# ---------------------------------------------------------------------------
# Classe principale
# ---------------------------------------------------------------------------

class JavaClass(Class):

    def __init__(self):
        super().__init__()
        self._linked_relations: list[tuple[str, str, str]] = []
        self._implements: str = None

    def addRelation(self, kind: str, target: str, multiplicity: str = "one") -> None:
        self._linked_relations.append((kind, target, multiplicity))

    def _build_header(self) -> str:
        prefix     = "abstract " if self._isAbstract else ""
        parent     = getattr(self, "_parent", None)
        implements = getattr(self, "_implements", None)

        declaration = f"public {prefix}class {self._name}"
        if parent:
            declaration += f" extends {parent}"
        if implements:
            declaration += f" implements {implements}"
        return declaration + " {"

    def _build_fields(self) -> list[str]:
        result = []
        for attr in self._attributes:
            result.append(f"    {attr.toCode()}")
        for (kind, target, multiplicity) in self._linked_relations:
            field_name = target[0].lower() + target[1:]
            if multiplicity == "many":
                result.append(f"    private List<{target}> {field_name}List = new ArrayList<>();")
            else:
                result.append(f"    private {target} {field_name};")
        return result

    def _build_methods(self) -> list[str]:
        return [f"    {meth.toCode()}" for meth in self._methods]

    def toCode(self) -> str:
        sections  = [self._build_header()]
        sections += self._build_fields()
        sections.append("")
        sections += self._build_methods()
        sections.append("}")
        return "\n".join(sections)


# ---------------------------------------------------------------------------
# Enum et Interface
# ---------------------------------------------------------------------------

class JavaEnum(Enum):
    def toCode(self) -> str:
        body = ",\n    ".join(self._elements) if self._elements else ""
        return f"public enum {self._name} {{\n    {body}\n}}"


class JavaInterface(Interface):
    def toCode(self) -> str:
        output = [f"public interface {self._name} {{"]
        for meth in self._methods:
            args = ", ".join(meth._parameters) if meth._parameters else ""
            ret  = meth._returnType or "void"
            output.append(f"    {ret} {meth._name}({args});")
        output.append("}")
        return "\n".join(output)


# ---------------------------------------------------------------------------
# Relations — injection via setDestination() dans tous les cas
# ---------------------------------------------------------------------------

class JavaAssociation(Association):
    def setDestination(self, destination: Class) -> None:
        super().setDestination(destination)
        if self._source and hasattr(self._source, "addRelation"):
            mult = "many" if cardinality_is_multiple(self._destinationCardinality) else "one"
            self._source.addRelation("association", destination._name, mult)

    def toCode(self) -> str:
        src  = self._source._name      if self._source      else "?"
        dest = self._destination._name if self._destination else "?"
        return f"// Association {src} --> {dest}"


class JavaAgregation(Agregation):
    def setDestination(self, destination: Class) -> None:
        super().setDestination(destination)
        if self._source and hasattr(self._source, "addRelation"):
            mult = "many" if cardinality_is_multiple(self._destinationCardinality) else "one"
            self._source.addRelation("agregation", destination._name, mult)

    def toCode(self) -> str:
        src  = self._source._name      if self._source      else "?"
        dest = self._destination._name if self._destination else "?"
        return f"// Agrégation {src} o--> {dest}"


class JavaGeneralization(Generalization):
    def setDestination(self, destination: Class) -> None:
        super().setDestination(destination)
        if self._source and self._destination:
            if isinstance(self._destination, JavaInterface):
                # implements : renseigne _implements ET copie les méthodes de l'interface
                self._source._implements = self._destination._name
                for meth in self._destination._methods:
                    self._source.addMethod(meth)
            else:
                # extends classique
                self._source._parent = self._destination._name

    def toCode(self) -> str:
        src  = self._source._name      if self._source      else "?"
        dest = self._destination._name if self._destination else "?"
        if self._destination and isinstance(self._destination, JavaInterface):
            return f"// {src} implements {dest}"
        return f"// {src} extends {dest}"


class JavaComposition(Composition):
    def setDestination(self, destination: Class) -> None:
        super().setDestination(destination)
        if self._source and hasattr(self._source, "addRelation"):
            mult = "many" if cardinality_is_multiple(self._destinationCardinality) else "one"
            self._source.addRelation("composition", destination._name, mult)

    def toCode(self) -> str:
        src  = self._source._name      if self._source      else "?"
        dest = self._destination._name if self._destination else "?"
        return f"// Composition {src} *--> {dest}"


# ---------------------------------------------------------------------------
# Factory Java
# ---------------------------------------------------------------------------

class Java(Language):
    """Abstract Factory pour la génération de code Java."""

    @property
    def Class(self) -> type[JavaClass]:
        return JavaClass

    @property
    def Attribute(self) -> type[JavaAttribute]:
        return JavaAttribute

    @property
    def Method(self) -> type[JavaMethod]:
        return JavaMethod

    @property
    def Enum(self) -> type[JavaEnum]:
        return JavaEnum

    @property
    def Interface(self) -> type[JavaInterface]:
        return JavaInterface

    @property
    def Association(self) -> type[JavaAssociation]:
        return JavaAssociation

    @property
    def Agregation(self) -> type[JavaAgregation]:
        return JavaAgregation

    @property
    def Generalization(self) -> type[JavaGeneralization]:
        return JavaGeneralization

    @property
    def Composition(self) -> type[JavaComposition]:
        return JavaComposition

    @property
    def file_extension(self) -> str:
        return "java"