from core.core import *
from typing import List

# --- Utilitaires de mappage C++ ---
def map_visibility(vis: AccessSpecifier) -> str:
    if vis == AccessSpecifier.PUBLIC: return "public"
    if vis == AccessSpecifier.PRIVATE: return "private"
    if vis == AccessSpecifier.PROTECTED: return "protected"
    return "public" # default

def map_type(type_name: str) -> str:
    # Gestion des listes génériques venant du parser
    if type_name.startswith("List<"):
        inner_type = type_name[5:-1] # extrait 'T' de 'List<T>'
        return f"std::vector<{inner_type}*>" 
    
    # Types primitifs
    if type_name.lower() in ["string", "str"]: return "std::string"
    if type_name.lower() == "int": return "int"
    if type_name.lower() == "double": return "double"
    if type_name.lower() == "boolean": return "bool"
    if type_name.lower() == "void": return "void"
    
    # Par défaut, on assume que c'est une autre classe -> pointeur
    return f"{type_name}*" 

# --- Classes Spécifiques C++ ---

class CppAttribute(Attribute):
    def to_code(self) -> str:
        return f"    {map_type(self._type)} {self._name};"

class CppMethod(Method):
    def to_code(self) -> str:
        # Transformation des paramètres "nom:type" en "Type nom"
        params_list = []
        for p in self._parameters:
            if ':' in p:
                p_name, p_type = p.split(':')
                params_list.append(f"{map_type(p_type.strip())} {p_name.strip()}")
            else:
                # Fallback si pas de type
                params_list.append(f"int {p.strip()}")

        params_code = ", ".join(params_list)
        return f"    {map_type(self._return_type)} {self._name}({params_code});"

class CppClass(Class):
    def to_code(self) -> str:
        lines = []
        guard = self._name.upper() + "_H"
        lines.append(f"#ifndef {guard}")
        lines.append(f"#define {guard}")
        lines.append("")
        
        lines.append("#include <string>")
        lines.append("#include <vector>")
        
        for parent in self._parents:
            lines.append(f'#include "{parent}.h"')
            
        lines.append("")

        # Forward declarations
        declared_classes = set()
        for attr in self._attributes:
            clean_type = attr._type.replace("List<", "").replace(">", "")
            if clean_type.lower() not in ["int", "double", "float", "string", "void", "bool"]:
                if clean_type != self._name and clean_type not in declared_classes:
                    lines.append(f"class {clean_type};")
                    declared_classes.add(clean_type)
        
        lines.append("")

        inheritance = ""
        if self._parents:
            inheritance = " : " + ", ".join([f"public {p}" for p in self._parents])
        
        lines.append(f"class {self._name}{inheritance} {{")
        
        for vis in [AccessSpecifier.PRIVATE, AccessSpecifier.PROTECTED, AccessSpecifier.PUBLIC]:
            filtered_attrs = [a for a in self._attributes if a._visibility == vis]
            filtered_meths = [m for m in self._methods if m._visibility == vis]
            
            if filtered_attrs or filtered_meths:
                lines.append(f"{map_visibility(vis)}:")
                for a in filtered_attrs:
                    lines.append(a.to_code())
                for m in filtered_meths:
                    lines.append(m.to_code())
                lines.append("")
        
        lines.append("};")
        lines.append("")
        lines.append(f"#endif // {guard}")
        return "\n".join(lines)

class CppInterface(Interface):
    def to_code(self) -> str:
        lines = []
        guard = self._name.upper() + "_H"
        lines.append(f"#ifndef {guard}")
        lines.append(f"#define {guard}")
        lines.append("")
        lines.append("#include <string>") # Au cas où
        lines.append("")
        lines.append(f"class {self._name} {{")
        lines.append("public:")
        lines.append(f"    virtual ~{self._name}() {{}}") 
        
        for m in self._methods:
            # CORRECTION ICI : Utilisation de m._parameters au lieu de self._parameters
            params_list = []
            for p in m._parameters:
                if ':' in p:
                    p_name, p_type = p.split(':')
                    params_list.append(f"{map_type(p_type.strip())} {p_name.strip()}")
                else:
                    params_list.append(f"int {p.strip()}")
            
            params_code = ", ".join(params_list)
            
            # Méthode virtuelle pure
            lines.append(f"    virtual {map_type(m._return_type)} {m._name}({params_code}) = 0;")
            
        lines.append("};")
        lines.append(f"#endif // {guard}")
        return "\n".join(lines)

class CppEnum(Enum):
    def to_code(self) -> str:
        lines = []
        guard = self._name.upper() + "_H"
        lines.append(f"#ifndef {guard}")
        lines.append(f"#define {guard}")
        lines.append("")
        lines.append(f"enum class {self._name} {{")
        # Extraction du nom depuis la ligne brute (parfois le parser envoie "VAL" ou "VAL,")
        clean_elements = [e.replace(',', '').strip() for e in self._elements]
        for i, elem in enumerate(clean_elements):
            comma = "," if i < len(clean_elements) - 1 else ""
            lines.append(f"    {elem}{comma}")
        lines.append("};")
        lines.append(f"#endif // {guard}")
        return "\n".join(lines)