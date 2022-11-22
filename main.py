from core.util import Tokenrun; import sys

def run_intepreter(files):
    if (len(sys.argv) > 1):
        if (not files.endswith(".jv")):
            print("That is not the compitable file, try another file with (.jv) ext")
        else:
            with open(files, 'r') as f:
                data = f.read()
                result, error = Tokenrun(files, data)
                if error:
                    print(error.as_string())
                if result:
                    if len(result.elements) == 1:
                        print(repr(result.elements[0]))
                    else:
                        print(repr(result))

def run_from_gui(valueN, value):
    result, error = Tokenrun(valueN, value)
    if error:
        print(error.as_string())
    if result:
        if len(result.elements) == 1:
            print(repr(result.elements[0]))
        else:
            print(repr(result))
                        
if __name__ == "__main__":
    try:
        run_intepreter(sys.argv[1])
    except Exception as err:
        print(f"Error: {err}")
