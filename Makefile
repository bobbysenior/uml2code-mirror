test:
  python uml2code.py -l Cpp -o tests/output tests/model.puml
  python uml2code.py -l Java -o tests/output tests/model.puml
  python uml2code.py -l Python -o tests/output tests/model.puml

clean:
  rm tests/output/*