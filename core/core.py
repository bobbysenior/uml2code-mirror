class Langage:
    Class = None
    Relations = None

class Class:
    pass

class Relation:
    pass

class CppRelations:
    pass

class CppClass(Class):
    pass



class Cpp(Langage):
    Class = CppClass
    Relations = CppRelations

choice = input()
if choice == "CPP":
    langage = Cpp

# test