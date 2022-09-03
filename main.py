import sys, core.util as util, os

def run_intepreter(files):
    intepreterJV = util.JVInterpreter("JV")
    if (len(sys.argv) > 1):
        if (not sys.argv[1].endswith(".jv")):
            print("That is not the compitable file, try another file with (.jv) ext")
        else:
            for line in open(sys.argv[1], "r"):
                intepreterJV.interpret_line(line)

if __name__ == "__main__":
    try:
        run_intepreter(sys.argv[1])
    except Exception as err:
        print(f"Error: {err}")
