from typing import List
from core.core import (
    Language, Class, Method, Attribute, Enum, Interface,
    Association, Agregation, Generalization, Composition, accessSpecifier
)

# --- Aides au formatage Python ---

def get_python_type(uml_type: str) -> str:
    mapping = {
        "int": "int",
        "String": "str",
        "boolean": "bool",
        "float": "float",
        "void": "None"
    }
    return mapping.get(uml_type, uml_type)

def get_python_visibility(vis: accessSpecifier, name: str) -> str:
    if vis == accessSpecifier.PRIVATE:
        return f"__{name}"
    elif vis == accessSpecifier.PROTECTED:
        return f"_{name}"
    return name

# --- Implémentations Concrètes (Le 'toCode') ---

class PythonAttribute(Attribute):
    def toCode(self) -> str:
        py_name = get_python_visibility(self._visibility, self._name)
        py_type = get_python_type(self._type)
        return f"        self.{py_name}: {py_type} = None"

class PythonMethod(Method):
    def toCode(self) -> str:
        py_name = get_python_visibility(self._visibility, self._name)
        py_return = get_python_type(self._returnType) if getattr(self, '_returnType', None) else "None"
        
        formatted_params = ["self"]
        for p in self._parameters:
            if ":" in p:
                p_name, p_type = [x.strip() for x in p.split(":")]
                formatted_params.append(f"{p_name}: {get_python_type(p_type)}")
            else:
                formatted_params.append(p)
                
        params_str = ", ".join(formatted_params)
        
        code = f"    def {py_name}({params_str}) -> {py_return}:\n"
        code += f"        pass\n"
        return code

class PythonClass(Class):
    def toCode(self) -> str:
        code = f"class {self._name}:\n"
        code += "    def __init__(self):\n"
        if not self._attributes:
             code += "        pass\n"
        else:
            for attr in self._attributes:
                code += f"{attr.toCode()}\n"
                
        code += "\n"
        if self._methods:
            for method in self._methods:
                code += f"{method.toCode()}\n"
        
        return code

class PythonInterface(Interface):
    def toCode(self) -> str:
        code = f"from abc import ABC, abstractmethod\n\n"
        code += f"class {self._name}(ABC):\n"
        if not self._methods:
             code += "    pass\n"
        else:
            for method in self._methods:
                 method_code = method.toCode().replace("    def ", "    @abstractmethod\n    def ")
                 code += f"{method_code}\n"
        return code

class PythonEnum(Enum):
    def toCode(self) -> str:
        code = f"from enum import Enum\n\n"
        code += f"class {self._name}(Enum):\n"
        if not self._elements:
            code += "    pass\n"
        else:
            for i, elem in enumerate(self._elements, start=1):
                code += f"    {elem} = {i}\n"
        return code

# --- Relations (Simplifiées pour le moment) ---

class PythonAssociation(Association):
    def toCode(self) -> str: return f"# Association"
class PythonAgregation(Agregation):
    def toCode(self) -> str: return f"# Agrégation"
class PythonComposition(Composition):
    def toCode(self) -> str: return f"# Composition"
class PythonGeneralization(Generalization):
    def toCode(self) -> str: return f"# Héritage"

# --- La "Factory" attendue par ton Main ---

class Python(Language):
    """
    C'est CETTE classe que ton main va instancier dynamiquement 
    quand tu feras `-l Python`
    """
    @property
    def Class(self) -> type[Class]: return PythonClass
    @property
    def Attribute(self) -> type[Attribute]: return PythonAttribute
    @property
    def Method(self) -> type[Method]: return PythonMethod
    @property
    def Enum(self) -> type[Enum]: return PythonEnum
    @property
    def Interface(self) -> type[Interface]: return PythonInterface
    @property
    def Association(self) -> type[Association]: return PythonAssociation
    @property
    def Agregation(self) -> type[Agregation]: return PythonAgregation
    @property
    def Generalization(self) -> type[Generalization]: return PythonGeneralization
    @property
    def Composition(self) -> type[Composition]: return PythonComposition