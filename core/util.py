"Importing package needed"
import sys, os


def keyword_ext(keyword, line):    
    encasing = line.strip(keyword + " ")
    if not encasing.startswith("(") or not encasing.endswith(")"):
        raise AttributeError(f"'{keyword}' butuh ['(' & ')']. Ex: {keyword} (*args)")

    return encasing.strip("(").strip(")")

class JVArgument:
    def __init__(self, name):
        self.name = name
        self.type = None

def parse_args(line) -> JVArgument:
    "parsing argument"
    
    if line == "":
        return []
    result: JVArgument = []
    
    for args in line.split(","):
        argument = JVArgument(args.strip().split(":")[0])
        if ":" in args:
            argument.type = ":".join(args.split(":")[1:]).lstrip()
        result.append(argument)
    return result

block = [
    "ketika",
    "untuk",
    "jika",
    "kecuali"
]

class JVEndCheck:
    "if items in block list, we need to end them to code the next block"
    def __init__(self):
        self.vstack = JVStack()
        
    def parseLine(self, line) -> bool:
        "Parse the line"
        if line.split(" ")[0] in block:
            self.vstack.push(line.split(" ")[0])
        if line == "henti":
            if len(self.vstack) == 0:
                return True
            self.vstack.pop()

class JVTypes:
    Bool = "bool"
    Text = "text"
    Number = "number"
    Null = "null"
    Void = "void"
    
types_set = [
    JVTypes.Bool,
    JVTypes.Text,
    JVTypes.Number,
    JVTypes.Null
]

class JVEntity:
    def __init__(self, _type, value):
        self.type = _type
        self.value = value
        
class JVvariable:
    def __init__(self, name, value: JVEntity, _type = JVTypes.Bool):
        self.value: JVEntity = value
        self.type = _type
        self.explicit_type = None

        self.name = name
        self.constant = False
        self.castable = False

class JVScope:
    def __init__(self):
        self.entities = {
            "variables": {},
            "objects": {}
        }

        self.checker = JVEndCheck()

class JVPythonBlock(JVScope):
    def __init__(self):
        super().__init__()
        
class JVStack:
    def __init__(self):
        self.stack: list = []

    def pop(self):
        v = self.stack[0]
        self.stack.pop(0)
        return v

    def push(self, value):
        self.stack.insert(0, value)

    def __getitem__(self, index):
        return self.stack[index]
    
class JVIFELSENEXT(JVScope):
    def __init__(self):
        super().__init__()
        self.all_lost = True

        self.done = False

class IF(JVScope):
    def __init__(self, condition):
        super().__init__()
        cond_type = type(condition)
        self.condition: cond_type = condition
        
class ELSE(JVScope):
    def __init__(self):
        super().__init__()
        self.running = True
        
class WHILE(JVScope):
    def __init__(self, condition):
        super().__init__()

        self.condition: str = condition
        self.code: str = []
        self.definition = True

class FOR(JVScope):
    def __init__(self, initialization, condition, post):
        super().__init__()

        self.initialization = initialization
        self.condition = condition
        self.post = post

        self.code = []
        self.running = False

class JVInterpreter:
    def __init__(self, iname):
        self.iname = iname

        self.stack = JVStack()
        self.stack.push(JVScope())
        self.scope = self.stack[0]

        self.path = JVStack()

    def type_exists(self, name) -> bool:
        if (name in types_set):
            return True

        if (self.get_entity("objects", name) != None):
            return True
    
    def get_entity(self, section, name): 
        for i in range(len(self.stack.stack) - 1, -1, -1):
            if (name in self.stack[i].entities[section]):
                return self.stack[i].entities[section][name]
            
        return None
    
    def set_entity(self, section, name, value: JVEntity):
        index = 0

        if (isinstance(self.stack[0], JVPythonBlock)):
            index = 1

        self.stack[index].entities[section][name] = value
        
    def get_var(self, name):
        return self.get_entity("variables", name)

    def set_var(self, name, value: JVvariable):
        if (value.type == JVTypes.Void):
            print("Anda tidak boleh menggunakan nilai kembalian dari Null -- itu tidak berarti apa-apa!")

        self.set_entity("variables", name, value)

    def null(self):
        "Return null."

        return JVEntity(JVTypes.Null, None)
    
    def void(self):
        "Return void."
        return JVEntity(JVTypes.Void, None)

    def interpret_line(self, line: str):
        line = line.strip()

        if "'" in line:
            return self.null()
        
        if line == "" or line == " ":
            return self.null()


        keywords = line.split(" ")
        klen = len(keywords)

        keyword = keywords[0]
        
        if (isinstance(self.stack[0], JVPythonBlock)):
            if (keyword != "henti"):
                exec(line, globals().update({
                    "interpreter": self,
                    "get": self.get_entity,
                    "set": self.set_entity,
                    "get_var": self.get_var,
                    "set_var": self.set_var
                }))


                return self.null()
        
        if (isinstance(self.stack[0], IF)):
            if keyword != "henti":
                if (not self.stack[0].condition):
                    return
        if (isinstance(self.stack[0], ELSE)):
            if keyword != "henti" or self.stack[0].running:
                self.stack[1].done = True
                if (not self.stack[1].all_lost):
                    return
        if (isinstance(self.stack[0], WHILE)):
            if (self.stack[0].definition):
                if (keyword != "henti"):
                    self.stack[0].code.append(line)
                    return

                self.stack[0].definition = False

                while self.interpret_line(self.stack[0].condition).value:
                    for line in self.stack[0].code:
                        self.interpret_line(line)

                self.stack.pop()
                return
        if (isinstance(self.stack[0], FOR)):
            if (self.stack[0].running):
                if (keyword != "henti"):
                    self.stack[0].code.append(line)
                    return
                self.stack[0].running = False

                while (self.interpret_line(self.stack[0].condition).value):
                    for line in self.stack[0].code:
                        self.interpret_line(line)
                    self.interpret_line(self.stack[0].post)
                self.stack.pop()
                return
        
        if (line.startswith("`")):
            if (not line.endswith("`")):
                print("Text harus menggunakan backtick -> (`).")
            text = line.strip("`")
            return JVEntity(JVTypes.Text, text)
        
        if (line.isnumeric()):
            return JVEntity(JVTypes.Number, int(keyword))

        if (keyword == "kosong"):
            return self.null()

        if (keyword == "valid"):
            return JVEntity(JVTypes.Bool, True)

        if (keyword == "non-valid"):
            return JVEntity(JVTypes.Bool, False)
        
        if (self.get_var(keyword) != None):
            value = self.get_var(keyword)

            if (value.type == JVTypes.Void):
                self.error("Anda tidak boleh menggunakan nilai kembalian dari Null -- itu tidak berarti apa-apa!")
            if ("=" in line):
                to = self.interpret_line(line.split("=")[1].strip())
                if (value.constant):
                    print("Penugasan kembali variabel const adalah ilegal.")

                value.value = to

            return value.value
        
        if (keyword == "lewati"):
            return self.null()
        
        if (keyword == "jika"):
            try:
                condition = self.interpret_line(keyword_ext("jika ", line))
            except AttributeError:
                print("Kondisi statement-jika harus ada ['(' dan ')'].")
            
            main_block = JVIFELSENEXT()
            
            if (condition.value):
                main_block.all_lost = False

            self.stack.push(main_block)
            self.stack.push(IF(condition.value))

            return self.null()
        
        if (line == "kecuali"):
            if (not isinstance(self.stack[0], JVIFELSENEXT)):
                print("'statement-kecuali' gabisa dipake kalo gaada 'statement-jika'")
            
            self.stack.push(ELSE())
            return self.null()
        
        if (keyword == "ketika"):
            try:
                condition = keyword_ext("ketika ", line)
            except AttributeError:
                print("")

            wh = WHILE(condition)
            self.stack.push(wh)
            return self.null()
        
        if (keyword == "untuk"):
            try:
                body = keyword_ext("untuk ", line)
            except AttributeError:
                print("Isi dari statement-untuk harus ada ['(' dan ')'].")

            init, cond, post = [x.strip() for x in body.split(";")]

            sfor = FOR(init, cond, post)
            self.stack.push(sfor)
            sfor.init = self.interpret_line(init)
            sfor.running = True

            return self.null()

        if (keyword == "katakan"):
            print(self.interpret_line(keywords[1]).value)
            return self.null()
        
        if (keyword == "ini"):
            name = line.split("=")[0].strip().strip("ini ")
            if (":" in name):
                name = name.split(":")[0].strip()
                
            for section in ["variables", "objects"]:
                if (self.get_entity(section, name) != None):
                    print("Definisi ulang 'variable' 'object' 'function'")
                    
            value = self.interpret_line(line.split("=")[1].strip())
            var: JVvariable = JVvariable(name, value, value.type)

            self.set_var(name, var)
            
            return value
            
        if (keyword == "henti"):
            if (klen > 1):
                print("Keyword 'henti' tidak ada lanjutan, keyword ini keyword penutup.")

            if (len(self.stack.stack) > 1):
                self.stack.pop()

            return self.null()
        
        """Operator section ========================================================================"""
        if (">" in line):
            left, right = [self.interpret_line(x) for x in [x.strip() for x in line.split(">")]]

            return JVEntity(JVTypes.Bool, left.value > right.value)

        if (">" in line):
            left, right = [self.interpret_line(x) for x in [x.strip() for x in line.split(">=")]]

            return JVEntity(JVTypes.Bool, left.value >= right.value)

        if ("<" in line):
            left, right = [self.interpret_line(x) for x in [x.strip() for x in line.split("<")]]
            return JVEntity(JVTypes.Bool, left.value < right.value)

        if ("<=" in line):
            left, right = [self.interpret_line(x) for x in [x.strip() for x in line.split("<=")]]
            return JVEntity(JVTypes.Bool, left.value <= right.value)

        if ("==" in line):
            left, right = [self.interpret_line(x) for x in [x.strip() for x in line.split("==")]]
            return JVEntity(JVTypes.Bool, left == right)

        if ("!=" in line):
            left, right = [self.interpret_line(x) for x in [x.strip() for x in line.split("!=")]]
            return JVEntity(JVTypes.Bool, left != right)
        
        if ("adalah" in line):
            left, right = [self.interpret_line(x) for x in [x.strip() for x in line.split("===")]]
            return JVEntity(JVTypes.Bool, left.value is right.value)

        if ("bukan" in line):
            left, right = [self.interpret_line(x) for x in [x.strip() for x in line.split("!==")]]
            return JVEntity(JVTypes.Bool, left.value is not right.value)
        
        if ("++" in keyword): 
            pre = self.interpret_line(keyword.split("++")[0])
            pre.value += 1
            return JVEntity(JVTypes.Number, pre.value)

        if ("--" in keyword): 
            pre = self.interpret_line(keyword.split("--")[0])
            pre.value -= 1
            return JVEntity(JVTypes.Number, pre.value)

        if ("+" in line):
            leftNumb, rightNumb = [self.interpret_line(x) for x in [x.strip() for x in line.split("+")]]
            return JVEntity(JVTypes.Number, leftNumb.value + rightNumb.value)
        
        if ("-" in line):
            leftNumb, rightNumb = [self.interpret_line(x) for x in [x.strip() for x in line.split("-")]]
            return JVEntity(JVTypes.Number, leftNumb.value - rightNumb.value)
        
        if ("*" in line):
            leftNumb, rightNumb = [self.interpret_line(x) for x in [x.strip() for x in line.split("*")]]
            return JVEntity(JVTypes.Number, leftNumb.value * rightNumb.value)
        
        if ("/" in line):
            leftNumb, rightNumb = [self.interpret_line(x) for x in [x.strip() for x in line.split("/")]]
            return JVEntity(JVTypes.Number, leftNumb.value / rightNumb.value)
        
        if ("%" in line):
            leftNumb, rightNumb = [self.interpret_line(x) for x in [x.strip() for x in line.split("%")]]
            return JVEntity(JVTypes.Number, leftNumb.value % rightNumb.value)
        
