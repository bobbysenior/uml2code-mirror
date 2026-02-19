### uml2code.py
import argparse
import sys
import os

def main() -> None:
    arg_parser = argparse.ArgumentParser(
                    prog='Uml2Code',
                    description='Un petit programme qui permet de convertir un diagramme de classe UML en code.',
                    epilog='')
    
    arg_parser.add_argument('input_file')           # positional argument
    arg_parser.add_argument('-l', '--language')   
    arg_parser.add_argument('-o', '--output')

    
    

    

if __name__ == '__main__':
    main()