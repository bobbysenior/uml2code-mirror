from core.core import (
    Language, Class, Attribute, Method, Enum, Interface,
    Association, Agregation, Generalization, Composition, accessSpecifier
)

# --- Spécialisation des éléments et implémentation de toCode() ---

class CppAttribute(Attribute):
    def toCode(self) -> str:
        # Génère une ligne du type : int monAttribut;
        return f"{self._type} {self._name};"

class CppMethod(Method):
    def toCode(self) -> str:
        # Génère une ligne du type : void maMethode(int p1, string p2);
        params = ", ".join(self._parameters) if self._parameters else ""
        ret_type = self._returnType if self._returnType else "void"
        return f"{ret_type} {self._name}({params});"

class CppClass(Class):
    def toCode(self) -> str:
        lines = []
        
        # 1. Gestion de la déclaration de la classe avec ou sans héritage
        if hasattr(self, '_parent') and self._parent:
            lines.append(f"class {self._name} : public {self._parent} {{")
        else:
            lines.append(f"class {self._name} {{")

        # 2. En C++, on regroupe par visibilité
        for vis in [accessSpecifier.PUBLIC, accessSpecifier.PROTECTED, accessSpecifier.PRIVATE]:
            # On filtre les attributs et méthodes pour la visibilité courante
            attrs = [a for a in self._attributes if a._visibility == vis]
            meths = [m for m in self._methods if m._visibility == vis]
            
            if attrs or meths:
                # Ajoute le modificateur d'accès (ex: "public:")
                lines.append(f"{vis.value.lower()}:")
                
                # Ajoute les attributs
                for a in attrs:
                    lines.append(f"    {a.toCode()}")
                
                # Ajoute les méthodes
                for m in meths:
                    lines.append(f"    {m.toCode()}")

        lines.append("};")
        return "\n".join(lines)

class CppEnum(Enum):
    def toCode(self) -> str:
        lines = [f"enum class {self._name} {{"]
        if self._elements:
            lines.append("    " + ",\n    ".join(self._elements))
        lines.append("};")
        return "\n".join(lines)

class CppInterface(Interface):
    def toCode(self) -> str:
        lines = [f"class {self._name} {{", "public:", f"    virtual ~{self._name}() = default;"]
        
        # Toutes les méthodes d'une interface C++ doivent être des virtuelles pures
        for m in self._methods:
            params = ", ".join(m._parameters) if m._parameters else ""
            ret_type = m._returnType if m._returnType else "void"
            lines.append(f"    virtual {ret_type} {m._name}({params}) = 0;")
            
        lines.append("};")
        return "\n".join(lines)

# --- Spécialisation des relations ---
# Pour un premier jet, on peut les traduire sous forme de commentaires 
# dans le code ou préparer le terrain pour des "#include" futurs.

class CppAssociation(Association):
    def toCode(self) -> str:
        return f"// Association : {self._source._name if self._source else '?'} -> {self._destination._name if self._destination else '?'}"

class CppAgregation(Agregation):
    def toCode(self) -> str:
        return f"// Agrégation : {self._source._name if self._source else '?'} o-- {self._destination._name if self._destination else '?'}"

class CppGeneralization(Generalization):
    def toCode(self) -> str:
        return f"// Héritage : {self._source._name if self._source else '?'} hérite de {self._destination._name if self._destination else '?'}"

class CppComposition(Composition):
    def toCode(self) -> str:
        return f"// Composition : {self._source._name if self._source else '?'} *-- {self._destination._name if self._destination else '?'}"

# --- Implémentation de l'interface Language (Abstract Factory) ---

class Cpp(Language):
    """
    Factory concrète pour le langage C++.
    Respecte la nouvelle interface avec les propriétés en majuscule.
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
    
    @property
    def file_extension(self) -> str:
        return "cpp"