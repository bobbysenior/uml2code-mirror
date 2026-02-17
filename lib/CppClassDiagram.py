### CppClassDiagram.py
from core.core import *
from typing import List

# --- Utilitaires de mappage C++ ---

def cpp_type_map(uml_type: str) -> str:
    """Convertit les types UML basiques en types C++."""
    mapping = {
        "String": "std::string",
        "string": "std::string",
        "int": "int",
        "boolean": "bool",
        "void": "void"
    }
    return mapping.get(uml_type, uml_type)

def cpp_visibility_map(vis: AccessSpecifier) -> str:
    if vis == AccessSpecifier.PUBLIC:
        return "public"
    elif vis == AccessSpecifier.PROTECTED:
        return "protected"
    else:
        return "private"

def format_params(params: List[str]) -> str:
    """Convertit ['id: int', 'name: String'] en 'int id, std::string name'."""
    cpp_params = []
    for p in params:
        if ":" in p:
            name, type_val = p.split(":")
            cpp_params.append(f"{cpp_type_map(type_val.strip())} {name.strip()}")
        else:
            # Fallback si le format n'est pas respecté
            cpp_params.append(p)
    return ", ".join(cpp_params)

# --- Implémentations Concrètes C++ ---

class CppAttribute(Attribute):
    def to_code(self) -> str:
        # Ex: std::string _name;
        t = cpp_type_map(self._type)
        return f"{t} {self._name};"

class CppMethod(Method):
    def __init__(self, name: str = "", visibility: AccessSpecifier = AccessSpecifier.PUBLIC, 
                 parameters: List[str] = None, return_type: str = "void", is_pure_virtual: bool = False):
        super().__init__(name, visibility, parameters, return_type)
        self._is_pure_virtual = is_pure_virtual

    def to_code(self) -> str:
        # Ex: void setName(std::string name);
        ret = cpp_type_map(self._return_type)
        params = format_params(self._parameters)
        virtual_suffix = " = 0" if self._is_pure_virtual else ""
        virtual_prefix = "virtual " if self._is_pure_virtual else ""
        return f"{virtual_prefix}{ret} {self._name}({params}){virtual_suffix};"

class CppClass(Class):
    def to_code(self) -> str:
        lines = []
        
        # Guard clause basique
        guard_name = f"{self._name.upper()}_H"
        lines.append(f"#ifndef {guard_name}")
        lines.append(f"#define {guard_name}")
        lines.append("")
        
        # Includes standards si besoin (simplifié)
        lines.append("#include <string>")
        lines.append("#include <vector>")
        for inc in self._includes:
            lines.append(f'#include "{inc}.h"')
        lines.append("")

        # Declaration de classe et héritage
        inheritance_str = ""
        if self._parents:
            # On suppose un héritage public par défaut pour le diagramme de classe
            inheritance_str = " : " + ", ".join([f"public {p}" for p in self._parents])
        
        lines.append(f"class {self._name}{inheritance_str} {{")

        # Tri par visibilité pour respecter les conventions C++
        grouped = {
            AccessSpecifier.PUBLIC: [],
            AccessSpecifier.PROTECTED: [],
            AccessSpecifier.PRIVATE: []
        }

        # Ajouter attributs
        for attr in self._attributes:
            grouped[attr._visibility].append(attr)
        
        # Ajouter méthodes
        for meth in self._methods:
            grouped[meth._visibility].append(meth)

        # Génération du corps
        for vis in [AccessSpecifier.PUBLIC, AccessSpecifier.PROTECTED, AccessSpecifier.PRIVATE]:
            elements = grouped[vis]
            if elements:
                lines.append(f"{cpp_visibility_map(vis)}:")
                for elem in elements:
                    # Conversion dynamique si l'objet n'est pas déjà un CppElement
                    # Ceci permet d'utiliser des objets Core génériques si besoin
                    code = elem.to_code()
                    if code:
                        lines.append(f"    {code}")
                lines.append("")

        lines.append("};")
        lines.append("")
        lines.append(f"#endif // {guard_name}")
        
        return "\n".join(lines)

class CppInterface(Interface):
    def __init__(self, name: str = ""):
        super().__init__(name=name)
        # En C++, une interface est une classe abstraite pure
        self._is_abstract = True

    def to_code(self) -> str:
        # Similaire à Class, mais on force les méthodes à être virtuelles pures si ce n'est pas déjà fait
        # Pour cet exemple, on réutilise la logique de CppClass en adaptant le constructeur
        # Dans une implémentation réelle, on pourrait hériter de CppClass
        
        # On cast temporairement en CppClass pour réutiliser to_code
        # Ou mieux, on utilise la composition ou le mixin. Ici, simple copie de logique :
        
        cpp_class = CppClass(name=self._name)
        for meth in self._methods:
            # Force virtual pure pour les interfaces
            cpp_meth = CppMethod(meth._name, meth._visibility, meth._parameters, meth._return_type, is_pure_virtual=True)
            cpp_class.add_method(cpp_meth)
            
        return cpp_class.to_code()

class CppEnum(Enum):
    def to_code(self) -> str:
        lines = []
        lines.append(f"enum class {self._name} {{")
        for i, elem in enumerate(self._elements):
            comma = "," if i < len(self._elements) - 1 else ""
            lines.append(f"    {elem}{comma}")
        lines.append("};")
        return "\n".join(lines)

# --- Relations C++ ---

class CppExtension(Generalization):
    def to_code(self) -> str:
        # L'héritage modifie la définition de la classe source.
        # Ce code retourne l'instruction à injecter.
        if self._source and self._destination:
            # En C++, Source : public Destination
            self._source.add_parent(self._destination._name)
            self._source.add_include(self._destination._name)
        return ""

class CppComposition(Composition):
    def to_code(self) -> str:
        # La composition ajoute un attribut dans la classe source
        if self._source and self._destination:
            # Ex: Destination* role;
            # Nous créons un CppAttribute à la volée et l'ajoutons à la source
            attr_name = self._role if self._role else self._destination._name.lower()
            # En C++, pour une composition, on utilise souvent un objet direct ou un unique_ptr
            # Ici on reste simple : pointeur
            attr_type = f"{self._destination._name}*"
            new_attr = CppAttribute(attr_name, attr_type, AccessSpecifier.PRIVATE)
            self._source.add_attribute(new_attr)
            self._source.add_include(self._destination._name)
        return ""

class CppAssociation(Association):
    def to_code(self) -> str:
        # Similaire à composition mais sémantique différente (souvent référence ou pointeur nu)
        if self._source and self._destination:
            attr_name = self._role if self._role else f"ref_{self._destination._name.lower()}"
            attr_type = f"{self._destination._name}*"
            new_attr = CppAttribute(attr_name, attr_type, AccessSpecifier.PRIVATE)
            self._source.add_attribute(new_attr)
            # En association, on utilise souvent forward declaration au lieu d'include pour éviter les cycles
            # Mais pour simplifier ici :
            self._source.add_include(self._destination._name)
        return ""

# --- Générateur Principal ---

class CppCodeGenerator:
    """
    Cette classe orchestre la génération.
    Elle prend un ClassDiagram (core), convertit ou traite les relations,
    puis déclenche la génération du code pour chaque classe.
    """
    def generate(self, diagram: ClassDiagram):
        results = {}
        
        # 1. Traitement des relations (Passerelle entre relations et structures de classes)
        # On doit parcourir les relations pour modifier les classes (ajouter parents, attributs)
        for element in diagram._elements:
            if isinstance(element, Relation):
                # Si c'est une relation spécifique Cpp, on appelle to_code qui fait le travail de liaison
                # Si c'est une relation Core générique, on devrait la mapper vers CppExtension/etc.
                # Ici, on assume que les objets passés sont déjà des CppExtension ou compatibles
                element.to_code()

        # 2. Génération du code des classes
        for element in diagram._elements:
            if isinstance(element, Class) and not isinstance(element, Relation):
                # Si l'élément est une classe Core standard, on peut vouloir la "transformer" en CppClass
                # pour bénéficier du to_code spécifique, ou supposer que l'utilisateur a construit des CppClass.
                
                # Pour la robustesse, on vérifie si to_code renvoie quelque chose
                code = element.to_code()
                if code is None:
                    # Ce n'est pas une CppClass, on ignore ou on convertit à la volée (complexe)
                    continue
                    
                filename = f"{element._name}.h"
                results[filename] = code
                
        return results

# Exemple d'usage (Commenté)
"""
if __name__ == "__main__":
    diag = ClassDiagram()
    
    # Création des éléments
    cls_a = CppClass(name="User")
    cls_a.add_attribute(CppAttribute("username", "String"))
    cls_a.add_method(CppMethod("login", parameters=["password: String"], return_type="boolean"))
    
    cls_b = CppClass(name="Admin")
    
    # Héritage: Admin extends User
    rel = CppExtension()
    rel.set_source(cls_b)
    rel.set_destination(cls_a)
    
    diag.add_element(cls_a)
    diag.add_element(cls_b)
    diag.add_element(rel)
    
    gen = CppCodeGenerator()
    files = gen.generate(diag)
    
    for fname, content in files.items():
        print(f"--- {fname} ---")
        print(content)
"""