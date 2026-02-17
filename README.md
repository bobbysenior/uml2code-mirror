# Uml2Code

#### Auteurs : MEZINO Thomas, GALY Reichmann, GUILLIER Yaële

Un petit projet de cours dont l'objectif est de transformer un diagramme (pour l'instant uniquement diagramme de classe) UML en code.
Nous avons décidé d'implémenter les 3 langages suivants :
- Java (Reichmann)
- C++ (Thomas)
- Python (Yaële)

## Architecture du code

Voici l'architecture que nous allons utiliser pour réaliser notre projet :

![diagramme](uml_diagrams/core_diagram.png)

Voici l'architecture globale de notre projet (avec les 3 langages que nous avons choisis.)

![diagramme](uml_diagrams/implementation_diagram.png)

**Remarque** : Dans le diagramme ci-dessus, l'interface langage permet à chaque langage de spécifier quels sont ses spécificités. Elle n'est pas nécessaire en soi, mais elle sera très utile pour l'implémentation python.

Exemple concret :
```python
if user_input = "Java":
    language = Java
else:
    language = Cpp

language.attribute

# STDOUT
# <class: JavaAttribute>   // si user_input = "Java"
# <class: CppAttribute>   // si user_input != "Java"
```
