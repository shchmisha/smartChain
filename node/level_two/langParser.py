from node.level_one.blockchain import Blockchain

# BLOCKCHAIN COMMANDS:
# BLOCKCHAIN UPLOAD VAR
# upload data stored in that variable to the blockchain
# each data uploaded will be signed by the vm's private key
# BLOCKCHAIN GET VAR or BLOCKCHAIN GET NUM
# get document at given index. if index is -1, gets the latest document
# BLOCKCHAIN FILTER VAR or BLOCKCHAIN FILTER STRING
# get all documents filtered by having a certain key in their dict


# rework the document pool to just have a list of different pieces of data.
# these pieces will probably be dictionaries.
# the data stored inside will not be checked by default in the chain, but by the vm and the instructions uploaded for interractions

# input "request_key" var
# stores a certain value of the request dictionary in that variable

# userRequest.user_request = dict({"key":"key", "data": {"content1": "content", "content2": "content"}, "signature": "signature"})

# when the chain is created, create the default configurations and add them to the chain straight away. when syncing, these can be replaced
# (networking transfers are not put through the interpreter)

# add dictionaries
# dictionaries will be dictated by the dict keyword
# $var = { "STRING": value, "STRING2": value2 }
# if tokens[-1] == EQUALS: tokens.append(DICT)
# store user request as a dictionary itself

# what to add:
#   dictionaries
#   ways to get specific documents by a certain key
#   ways to compare data from user request
#   ways to interact with data in dictionaries




class Interpreter:
    def __init__(self, blockchain):
        self.tokens = []

        self.symbols = {}
        self.arrays = {}

        self.functions = {}
        self.return_val = ""

        self.classes = {}
        # request data will be a reference inside the symbols dict, such as REQ:KEY

        self.blockchain = blockchain
        self.blockchain_data = {}

        self.user_request = {}

        self.upload_data = {} # includes any data that needs to be uploaded
        self.return_data = {} # any data that needs to be added to the pool

    def open_file(self, filename):
        data = open(filename, "r").read()
        data+="§"
        return data

    def lex(self,data):
        # how the lexer  works is that is goes through each character, appends it to a token and checks if the token is valid
        # if token is equal to a statement, it adds the statement to the tokens list
        # if token is in state one, and a double quote is encountered, the string saved will be saved to the tokens list with a string appendage

        # in order to keep multiple different data types in the lexer cache, have multiple variables for each type and whenever a state is switched, the variable towhich the token is added is switched
        tok = "" # a token is built up from character and reset whenever a valid token is found
        state = 0 # if state is 0, every letter we find is a variable/operator, if state is 1, every letter is part of a string
        # a variable like state cna be used to represent entering the state of a function for things like recursion
        varStarted = 0
        string = ""
        expr = "" # forms the desired expression
        # checkif while expression is on and some other state is switched, save the number
        var = ""
        count = 0
        data = list(data)
        for char in data:
            count+=1
            tok+=char
            if tok == " " or tok == ",": # is the , addition good?
                if var!="":
                    self.tokens.append("VAR:"+var)
                    # print(var)
                    var = ""
                    varStarted = 0
                elif expr!="":
                    self.tokens.append("NUM:"+expr)
                    expr=""
                if state == 0:
                    tok = ""
                else:
                    tok = " "
            elif tok == ".":
                if var!="":
                    self.tokens.append("VAR:"+var)
                    # print(var)
                    var = ""
                    varStarted = 0
                elif expr!="":
                    self.tokens.append("NUM:"+expr)
                    expr=""
                if state == 0:
                    tok = ""
                else:
                    tok = "."
            elif tok == "\n" or char == "§" or tok == ";": #########
                if expr!="":
                    self.tokens.append("NUM:"+expr)
                    expr=""
                elif var!="":
                    self.tokens.append("VAR:"+var)
                    # print(var) problem found here
                    var = ""
                    varStarted = 0
                if tok == ";":
                    self.tokens.append("EOI")
                elif tok =="\n" and self.tokens[-1]!="NL":
                    self.tokens.append("NL")
                tok = ""
            elif tok == "=" and state == 0:
                if expr!="":
                    self.tokens.append("NUM:"+expr)
                    expr=""
                if var!="":
                    self.tokens.append("VAR:"+var)
                    # print(var) and here
                    var = ""
                    varStarted = 0
                if self.tokens[-1] == "EQUALS":
                    self.tokens[-1] = "EQEQ"
                else:
                    self.tokens.append("EQUALS")
                tok = ""
            elif tok == "$" and state == 0:
                varStarted = 1
                var += tok
                tok = ""
            elif varStarted == 1:
                if tok == "<":
                    if var!="":
                        self.tokens.append("VAR:"+var)
                        var = ""
                        varStarted = 0
                elif tok == ")" or tok == "(":
                    if var!="":
                        self.tokens.append("VAR:"+var)
                        var = ""
                        varStarted = 0
                    elif expr!="":
                        self.tokens.append("NUM:"+expr)
                        expr=""
                    self.tokens.append("OP:"+tok)
                    tok = ""
                elif tok == "[" or tok == "]":
                    if var!="":
                        self.tokens.append("VAR:"+var)
                        var = ""
                        varStarted = 0
                    self.tokens.append("ARR")
                    tok=""
                else:
                    var+=tok
                    tok = ""
            elif tok == "FUNC" or tok == "func":
                self.tokens.append("FUNC")
                tok = ""
            elif tok == "ENDFUNC" or tok == "endfunc":
                self.tokens.append("FUNC")
                tok = ""
            elif tok == "PRINT" or tok == "print":
                self.tokens.append("PRINT")
                tok = "" # reset the token each time a valid token has been found
            elif tok == "INPUT" or tok == "input":
                self.tokens.append("INPUT")
                tok = ""
            elif tok == ":":
                ############# the semi colon needs to be seperate from var
                # print("reached : ")
                if expr!="":
                    self.tokens.append("NUM:"+expr)
                    expr=""
                elif var!="" and varStarted==1:
                    self.tokens.append("VAR:"+var)
                    var = ""
                    varStarted = 0
                self.tokens.append(":")
                tok = ""
            elif tok == "GET" or tok == "get":
                self.tokens.append("GET")
                tok = ""
            elif tok == "UPLOAD" or tok == "upload":
                self.tokens.append("UPLOAD")
                tok = ""
            elif tok == "IF" or tok == "if":
                self.tokens.append("IF")
                tok = ""
            elif tok == "ENDIF" or tok == "endif":
                self.tokens.append("ENDIF")
                tok = ""
            elif tok == "WHILE" or tok == "while":
                self.tokens.append("WHILE")
                tok = ""
            elif tok == "FOREACH" or tok == "foreach":
                self.tokens.append("FOREACH")
                tok = ""
            elif tok == "RETURN" or tok == "return":
                self.tokens.append("RETURN")
                tok = ""
            elif tok == "UPLOAD" or tok == "upload":
                self.tokens.append("UPLOAD")
                tok = ""
            elif tok == "GET" or tok == "get":
                self.tokens.append("GET")
                tok = ""
            elif tok == "BLOCKCHAIN" or tok == "blockchain":
                self.tokens.append("BLOCKCHAIN")
                tok = ""
            elif tok == "{":
                self.tokens.append(":")
                tok = ""
            elif tok == "}":
                i = len(self.tokens)-1
                num_of_stmt = 0
                while i>=0:
                    # check for both starts and finishes
                    if self.tokens[i]=="ENDIF" or self.tokens[i]=="ENDWHILE" or self.tokens[i]=="ENDFUNC" or self.tokens[i]=="ENDFOREACH":
                        num_of_stmt+=1
                    elif self.tokens[i]=="IF" or self.tokens[i]=="WHILE" or self.tokens[i]=="FUNC" or self.tokens[i]=="FOREACH":
                        if num_of_stmt ==0:
                            if self.tokens[i]=="IF":
                                self.tokens.append("ENDIF")
                                break
                            elif self.tokens[i]=="WHILE":
                                self.tokens.append("ENDWHILE")
                                break
                            elif self.tokens[i]=="FUNC":
                                self.tokens.append("ENDFUNC")
                                break
                            elif self.tokens[i]=="FOREACH":
                                self.tokens.append("ENDFOREACH")
                                break
                        else:
                            num_of_stmt-=1
                    i-=1
                # tokens.append("}")
                tok = ""
            elif tok=="[":
                if var!="":
                    self.tokens.append("VAR:"+var)
                    # print(var)
                    var = ""
                    varStarted = 0
                elif expr!="":
                    self.tokens.append("NUM:"+expr)
                    expr=""
                self.tokens.append("ARR")
                tok=""
            elif tok=="append" or tok == "APPEND":
                self.tokens.append("APPEND")
                tok=""
            elif tok=="pop" or tok == "POP":
                self.tokens.append("POP")
                tok=""
            elif tok == "]":
                if var!="":
                    self.tokens.append("VAR:"+var)
                    # print(var)
                    var = ""
                    varStarted = 0
                elif expr!="":
                    self.tokens.append("NUM:"+expr)
                    expr=""
                self.tokens.append("ENDARR")
                tok=""
            elif tok == "ENDWHILE" or tok == "endwhile":
                self.tokens.append("ENDWHILE")
                tok = ""
            elif tok == "0" or tok == "1" or tok == "2" or tok == "3" or tok == "4" or tok == "5" or tok == "6" or tok == "7" or tok == "8" or tok == "9":
                if varStarted == 1:
                    var+=tok
                    tok=""
                else:
                    expr+=tok
                    tok=""
            elif tok == "+" or tok == "-" or tok == "*" or tok == "/" or tok == "(" or tok == ")" or tok == "%":
                if expr!="":
                    self.tokens.append("NUM:"+expr)
                    expr=""
                if self.tokens[-1]=="OP:+" and tok=="+":
                    self.tokens[-1] = "PLPL"
                else:
                    self.tokens.append("OP:"+tok) #????????
                tok=""
            elif tok == ">" or tok == "<":
                if var!="":
                    self.tokens.append("VAR:"+var)
                    var = ""
                    varStarted = 0
                elif expr!="":
                    self.tokens.append("NUM:"+expr)
                    expr=""
                self.tokens.append("COMP:"+tok)
                tok=""
            elif tok == "\t":
                # maybe do something here
                tok = ""
            elif tok == "\"" or tok == " \"":
                if state == 0: # if a double quote sign is found when state is 0, the state is switched to 1
                    # tok = ""
                    state = 1
                elif state == 1: # if a double quote sign is found when the state is 1, the state is switched to 0 and the string is returned
                    self.tokens.append("STRING:"+string+"\"")
                    string = ""
                    state = 0
                    tok = ""
            elif state == 1: # if the character is found while state is 1, the character is added to
                string += tok
                tok = ""
            # print(tok)
        return self.tokens

    def evalString(self, toks, index):
        # have an eval function for strings adn arrays as well
        prev_index = index
        string = ""
        last_type = None
        count=0
        while (index<len(toks)):
            # print(string)
            if toks[index]=="NL":
                break
            if toks[index][0:2] == "OP":
                if last_type == "VAR" or last_type == "NUM" or last_type == "STRING" or last_type == None:
                    string+=toks[index][3:]
                    last_type = toks[index][0:2]
                    index+=1
                else:
                    index-=1
                    break
            elif toks[index][0:3] == "VAR" or toks[index][0:3] == "NUM" or (toks[index][0:6]=="STRING" and len(toks)>7):
                if last_type == "OP" or last_type == None:
                    # print(last_type)
                    if toks[index][0:3] == "VAR":
                        # print("toks[index][0:3] == VAR")
                        varval = self.symbols[toks[index][4:]]
                        # add support for strings
                        if varval[0:3] == "NUM":
                            string+="\""+varval[4:]+"\""
                        elif varval[0:6] == "STRING":
                            string+=varval[7:]
                        last_type = "VAR"
                        index+=1
                    elif toks[index][0:3] == "NUM":
                        string+= "\""+toks[index][4:]+"\""
                        last_type = toks[index][0:3]
                        index+=1
                    elif toks[index][0:6] == "STRING":
                        string+=toks[index][7:]
                        last_type = toks[index][0:6]
                        index+=1
                    else:
                        if index!=prev_index:
                            index-=1
                        break
                else:
                    if index!=prev_index:
                        index-=1
                    break
            else:
                if index!=prev_index:
                    index-=1
                break
        return "STRING:"+eval(string), index-prev_index

    def evalExpression(self, toks, index):
        # have an eval function for strings adn arrays as well
        prev_index = index
        expression = ""
        last_type = None
        count=0
        while (index<len(toks)):
            # print(expression)
            if toks[index]=="NL":
                break

            # if not( and (toks[index][0:3] == "VAR" or toks[index][0:3] == "NUM")):
            #     break
            # if last_type == "VAR" or last_type == "NUM" and toks[index][0:2] == "OP"
            # check whether the last type is a value and the current type is and operation or vice versa
            # if toks[index]=="EOI":
            #     break
            # print(toks[index])
            if toks[index][0:2] == "OP":
                if last_type == "VAR" or last_type == "NUM" or last_type == None:
                    if toks[index][0:3] == "VAR":
                        varval = self.symbols[toks[index][4:]]
                        if varval[0:3] == "NUM":
                            expression+=varval[4:]
                        last_type = toks[index][0:3]
                        index+=1
                    elif toks[index][0:2] == "OP":
                        expression+=toks[index][3:]
                        last_type = toks[index][0:2]
                        index+=1
                    elif toks[index][0:3] == "NUM":
                        expression+=toks[index][4:]
                        last_type = toks[index][0:3]
                        index+=1
                else:
                    index-=1
                    break
            elif toks[index][0:3] == "VAR" or toks[index][0:3] == "NUM":
                if last_type == "OP" or last_type == None:
                    # print(last_type)
                    if toks[index][0:3] == "VAR":
                        # print("toks[index][0:3] == VAR")
                        varval = self.symbols[toks[index][4:]]
                        # add support for strings
                        if varval[0:3] == "NUM":
                            expression+=varval[4:]
                        elif varval[0:3] == "ARR":
                            if toks[index][0:3]+" "+toks[index+1] == "VAR ARR":
                                # eval the expression inside by providing the toks and the index after the ARR token

                                val, add_to = self.evalExpression(toks, index+2)
                                # while toks[index]!="ENDARR":
                                expression+=str(self.arrays[toks[index][4:]][val][4:])

                                while toks[index]!="ENDARR":
                                    index+=1
                            elif toks[index][0:3]+" "+toks[index+1]=="VAR POP":
                                expression+=str(self.arrays[toks[index][4:]].pop()[4:])
                        last_type = "VAR"
                        index+=1
                    elif toks[index][0:2] == "OP":
                        expression+=toks[index][3:]
                        last_type = toks[index][0:2]
                        index+=1
                    elif toks[index][0:3] == "NUM":
                        expression+=toks[index][4:]
                        last_type = toks[index][0:3]
                        index+=1
                    else:
                        if index!=prev_index:
                            index-=1
                        break
                else:
                    if index!=prev_index:
                        index-=1
                    break
            else:
                if index!=prev_index:
                    index-=1
                break
            # print(count)
            # print(toks[index])
            # count+=1
        return eval(expression), index-prev_index

    def doAssign(self,varName,varVal):
        # check whether the value is a number or a variable or an expression
        self.symbols[varName[4:]] = varVal

    def getVariableTypes(self, toks, i):
        # print(toks[i], toks[i+1])
        if toks[i+1][0:2] == "OP" or toks[i+1] == "ARR":
            if self.symbols[toks[i][4:]][:4]=="FUNC":
                to_add = self.exec_func(toks, i)
                return self.return_val, to_add
            val, to_add = self.evalExpression(toks, i)
            return val, to_add
        else:
            if toks[i][:3]=="VAR":
                return self.symbols[toks[i][4:]], 0
            return toks[i], 0

    def exec_func(self,toks, i):
        func_desc = self.functions[toks[i][4:]]

        # set the variables in the func_desc to the variables provided inside the
        args_index = i+2
        func_args_index = 2

        while toks[args_index]!="OP:)":
            self.symbols[func_desc[func_args_index]] = toks[args_index]
            args_index+=1
            func_args_index+=1

        # call the function recursively
        self.parse(toks, func_desc[1], func_desc[0]+1)
        # print(endfunc_index)
        return func_args_index+1

    def getVariable(self, varName):
        if varName[4:] in self.symbols:
            if self.symbols[varName[4:]][:3]=="ARR":
                return self.arrays[self.symbols[varName[4:]][4:]]
            return self.symbols[varName[4:]]
        else:
            print("Variable does not exist")
            return None

    def getArr(self,toks, index):
        new_index = index
        arr = []
        while new_index<len(toks):
            if toks[new_index]=="ENDARR":
                break
            elif toks[new_index][:3]=="VAR":
                arr.append(toks[new_index])
            elif toks[new_index][:3]=="NUM":
                arr.append(toks[new_index])
            elif toks[new_index][:6]=="STRING":
                arr.append(toks[new_index])
            new_index+=1
        return arr,new_index-index+1

    def parse(self, toks, toks_end_index, toks_start_index=0):
        i = toks_start_index
        to = toks_end_index
        # whnever there is a value encountered, have a function that gets the value of the expression no matter the type of the first value
        # the value that returns can either be assigned, compared or looped through

        # print(i)
        # print(to)
        while (i<to):
            # print(symbols)
            # if toks[i] == "FUNC":
            #     print(toks[i] + " " + toks[i+1][:3] + " " + toks[i+2][:2])

            # if i==16:
            #     break
            if toks[i]=="ENDIF" or toks[i]=="NL" or toks[i]=="ENDARR" or toks[i]=="ENDFUNC": # tokes representing nl can be used tonotdisruptthe flow of the program, as well as disrupting the flow of some evaluations
                i+=1
            elif toks[i] + " " + toks[i+1][:3] == "RETURN VAR" or toks[i] + " " + toks[i+1][:3] == "RETURN NUM" or toks[i] + " " + toks[i+1][:6] == "RETURN STRING":
                if (toks[i+1][:3] == "VAR" and self.symbols[toks[i+1][4:]][:3] == "NUM") or toks[i+1][:3] == "NUM":
                    val, to_add = self.evalExpression(toks, i+1)
                    self.return_val = "NUM:"+str(val)
                elif toks[i+1][:3] == "VAR" and self.symbols[toks[i+1][4:]][:3] == "ARR":
                    if self.symbols[toks[i+1][4:]][:4] == "FUNC":
                        self.exec_func(toks, i+1)
                    else:
                        self.return_val = self.symbols[toks[i+1][4:]]
                elif toks[i+1][:6] == "STRING":
                    self.return_val = toks[i+1]
                # one way to break
                i=to
            elif toks[i] + " " + toks[i+1][0:6] == "PRINT STRING" or toks[i] + " " + toks[i+1][0:3] == "PRINT NUM" or toks[i] + " " + toks[i+1][0:3] == "PRINT VAR":
                to_add = 0
                if toks[i+1][0:6]=="STRING":
                    print(toks[i+1][8:-1])
                elif toks[i+1][0:3]=="NUM":
                    val, to_add = self.evalExpression(toks, i+1)
                    print(val)
                elif toks[i+1][0:3]=="VAR":
                    # check teh value of each variable
                    if self.symbols[toks[i+1][4:]][:3] == "REQ":

                        print(self.user_request[self.symbols[toks[i+1][4:]][5:-1]])
                    else:
                        val, to_add = self.getVariableTypes(toks, i + 1) # account for token being at the end of the line
                        if to_add==0:
                            print(self.getVariable(toks[i+1]))
                        else:
                            print(val)
                i+=(2+to_add)
                # sort out the matter of indexes being replaced after a new value is evaluated
            elif toks[i][:3] + " " + toks[i+1] == "VAR OP:(" and self.symbols[toks[i][4:]][:4]=="FUNC":
                # print("REACHED")
                # how does it work:
                # get the func_desc array from functions dict
                # assign all vaiables in the func_desc array to data provided inside the brackets
                # call the parse function from the starting index of the function to the ending

                func_desc = self.functions[toks[i][4:]]

                # set the variables in the func_desc to the variables provided inside the
                args_index = i+2
                func_args_index = 2

                while toks[args_index]!="OP:)":
                    if toks[args_index][:3] == "VAR":
                        self.symbols[func_desc[func_args_index]] = self.symbols[toks[args_index][4:]]
                    else:
                        self.symbols[func_desc[func_args_index]] = toks[args_index]
                    args_index+=1
                    func_args_index+=1
                # call the function recursively
                self.parse(toks, func_desc[1], func_desc[0]+1)
                # gothrough each value that was provided to the args, check ifitis a variable and then override their values with the values of the arguement
                i+=(func_args_index+1)
                # either deassign these variables or leave them be
            elif toks[i][:3] + " " + toks[i+1] == "VAR POP":
                arr = self.getVariable(toks[i])
                arr.pop()
                i+=2
            elif toks[i] + " " + toks[i+1][:3] + " " + toks[i+2]== "FUNC VAR OP:(":


                self.doAssign(toks[i+1], "FUNC:"+toks[i+1][4:])
                func_desc = [] # [start, end, arg1, ...]
                # get start of function
                startfunc_index = i
                while toks[startfunc_index]!=":":
                    # print("startfunc")
                    startfunc_index+=1
                func_desc.append(startfunc_index)
                # get end of function
                endfunc_index = startfunc_index
                while toks[endfunc_index]!="ENDFUNC":
                    # print("endfunc")
                    endfunc_index+=1
                func_desc.append(endfunc_index)

                args_index = i+2
                while toks[args_index]!=":":
                    # print("arg")
                    if toks[args_index][:3]=="VAR":
                        func_desc.append(toks[args_index][4:])
                        self.doAssign(toks[args_index], "NONE")
                    args_index +=1

                self.functions[toks[i+1][4:]] = func_desc
                # print(endfunc_index)
                i = endfunc_index
                # print(functions)
                # a func is declared with the variable name to which it willbe tied. calling functions willbe different form calling variables
            elif toks[i][0:3] + " " + toks[i+1] + " " + toks[i+2][0:6] == "VAR EQUALS STRING" or toks[i][0:3] + " " + toks[i+1] + " " + toks[i+2][0:3] == "VAR EQUALS NUM" or toks[i][0:3] + " " + toks[i+1] + " " + toks[i+2][0:3] == "VAR EQUALS VAR" or toks[i][0:3] + " " + toks[i+1] + " " + toks[i+2] == "VAR EQUALS ARR":
                # whenever values are assigned to variables, the type recognisers have to be in place inside the symbols dict
                # variables can hold either numbers, strings, arrays and functions
                to_add = 0
                if toks[i+2][0:6]=="STRING":
                    val, to_add = self.evalString(toks, i+2)
                    self.doAssign(toks[i], toks[i+2])
                elif toks[i+2][0:3]=="NUM":
                    val, to_add = self.evalExpression(toks, i+2)
                    self.doAssign(toks[i], "NUM:"+str(val))
                elif toks[i+2][0:3]=="VAR":
                    # check for functions and strings
                    varval = self.symbols[toks[i+2][4:]]
                    # print("symbols")
                    if varval[:3] == "NUM":
                        val, to_add = self.evalExpression(toks, i+2)
                        # print("NUM:"+str(val))
                        self.doAssign(toks[i], "NUM:"+str(val))
                    elif varval[:3] == "ARR":
                        # check if the value stored is an array
                        arr = self.arrays[toks[i+2][4:]]
                        self.arrays[toks[i][4:]]=arr
                        self.doAssign(toks[i], "ARR:"+toks[i][4:])
                    elif varval[:4] == "FUNC":
                        # execute the function, set the value as the returned value of that function and then
                        end_of_call_index = self.exec_func(toks,i+2)
                        self.doAssign(toks[i], self.return_val)
                        to_add+=(end_of_call_index-2)
                    elif varval[:6] == "STRING":
                        val, to_add = self.evalString(toks, i+2)
                        self.doAssign(toks[i], "STRING:\""+val+"\"")

                elif toks[i+2]=="ARR":
                    val, to_add = self.getArr(toks, i+3)
                    self.arrays[toks[i][4:]]=val

                    self.doAssign(toks[i], "ARR:"+toks[i][4:])
                    # when an array gets assigned to a var, the array is stored in a dictionary
                    # the value stored in the symbols is the ARR header with the name of the variable
                    # getting the array from a variable is the matter of checking that the ARR header is present and then using what comes after as the key for the arrays dict
                i+=3+to_add
            elif toks[i][:3] + " " + toks[i+1] + " " + toks[i+2][:3] == "VAR APPEND VAR" or toks[i][:3] + " " + toks[i+1] + " " + toks[i+2][:3] == "VAR APPEND NUM":
                to_add = 0
                arr = self.getVariable(toks[i])
                if toks[i+2][:3] == "VAR":
                    if self.symbols[toks[i+2][4:]][:3]=="NUM":
                        val, to_add = self.evalExpression(toks, i+2)
                        arr.append("NUM:"+str(val))
                    elif self.symbols[toks[i+2][4:]][:4]=="FUNC":
                        to_add = self.exec_func(toks, i+2)
                        val = self.return_val
                        if self.return_val[:3]=="NUM":
                            arr.append("NUM:"+val)
                    # if val[:3]=="VAR":
                    #     val = getVariable(val[4:])

                elif toks[i+2][:3] == "NUM":
                    val, to_add = self.evalExpression(toks, i+2)
                    arr.append("NUM:"+str(val))
                i+=3+to_add
            elif toks[i]+" "+toks[i+1][0:6]+ " "+ toks[i+2][0:3] == "INPUT STRING VAR":
                #  INPUT "REQUEST_VAR_KEY" VAR
                #  inside VAR, stores the key for that value inside the user input
                #  create the blockchain api, where the values of these vars can be uploaded
                ############
                self.doAssign(toks[i+2], "REQ:"+toks[i+1][7:])
                i+=3
            elif toks[i]+" "+toks[i+1][:6]+ " "+ toks[i+2][0:3] == "UPLOAD STRING VAR":
                # how will uploading work:
                # either literally add whatever is stored in the document to the blockchain
                # or
                # save everything to one upload_data object and save it to the blockchain
                varval = self.symbols[toks[i+2][4:]]
                if varval[:3] =="REQ":
                    self.upload_data[toks[i+1][8:-1]] = self.user_request[varval[5:-1]]
                else:
                    self.upload_data[toks[i+1][8:-1]] = varval
                i+=3
            elif toks[i]+" "+toks[i+1][0:3]+ " "+ toks[i+2]+ " "+ toks[i+3][0:3] == "BLOCKCHAIN VAR GET NUM" or toks[i]+" "+toks[i+1][0:3]+ " "+ toks[i+2][0:3]+ " "+ toks[i+3][0:3] == "BLOCKCHAIN VAR GET VAR" or toks[i]+" "+toks[i+1][0:3]+ " "+ toks[i+2][0:3]+ " "+ toks[i+3][0:2] == "BLOCKCHAIN VAR GET OP":
                # how will getting docs work:
                # gets the data stored at that index and assigns it to the variable provided
                # the actual data will be stored in the blockchain_data array
                fetched_data = None
                data_index, to_add = self.evalExpression(toks, i+3)
                if data_index == -1:
                    fetched_data = self.blockchain.chain[-1].data[-1]
                else:
                    index = 0

                    while index<data_index:
                        for block in self.blockchain.chain:
                            for data in block.data:
                                if index == data_index-1:
                                    fetched_data = data
                                index+=1


                self.symbols[toks[i+1][4:]] = "BCD:"+toks[i+1][4:]
                self.blockchain_data[toks[i+1][4:]] = fetched_data

                i+=4+to_add
            elif toks[i]+" "+toks[i+1]+ " "+ toks[i+2][0:3]+ " "+ toks[i+3][0:6] == "BLOCKCHAIN RETURN VAR STRING":
                string, to_add = self.evalString(toks,i+3)
                if self.symbols[toks[i+2][4:]][:3] == "BCD":
                    self.return_data[string[7:]] = self.blockchain_data[toks[i+2][4:]]
                elif self.symbols[toks[i+2][4:]][:3] == "ARR":
                    self.return_data[string[7:]] = self.arrays[toks[i+2][4:]]
                elif self.symbols[toks[i+2][4:]][:3] == "REQ":

                    self.return_data[string[7:]] = self.user_request[self.symbols[toks[i+2][4:]][5:-1]]
                else:
                    self.return_data[string[7:]] = self.symbols[toks[i+2][4:]]

                i+=4+to_add
            elif toks[i] + " " + toks[i+1][0:3] + " " + toks[i+2] + " " + toks[i+3][0:3] + " " + toks[i+4] == "IF VAR EQEQ NUM :":
                # if condition is correct, + 5
                # else, find the position of the end of the if statement and then adds that many spaces
                # print(getVariable(toks[i+1])[4:], toks[i+3][4:])
                if self.getVariable(toks[i+1])[4:] == toks[i+3][4:]:
                    i+=5
                else:
                    # loop through the expression until endif is found, then add that much to i and continue
                    while toks[i] != "ENDIF":
                        i+=1
            elif toks[i] + " " + toks[i+1][0:3] + " " + toks[i+2][0:3] + toks[i+3] == "FOREACH VAR VAR:":
                # foreach takes the array stored in the first var and assigns the secind var thevalue of each item of the array
                # makes afor in loop for the array
                # checks the current element of the array and then sets the second array to it
                endforeach_index = i
                while toks[endforeach_index]!="ENDFOREACH":
                    endforeach_index+=1

                arr = self.getVariable(toks[i+1])
                for el_i in range(len(arr)):
                    self.doAssign(toks[i+2], arr[el_i])
                    self.parse(toks, endforeach_index, i+4)
                    arr[el_i] = self.symbols[toks[i+2][4:]]
                i = endforeach_index+1
            elif toks[i] + " " + toks[i+1] + " " + toks[i+2][0:3] + toks[i+3] == "FOREACH BLOCKCHAIN VAR:":
                endforeach_index = i
                while toks[endforeach_index]!="ENDFOREACH":
                    endforeach_index+=1

                #complete this

                for block in self.blockchain.chain:
                    for data in block.data:
                        self.symbols[toks[i+2][4:]] = "BCD:"+toks[i+2][4:]
                        self.blockchain_data[toks[i+2][4:]] = data
                        self.parse(toks, endforeach_index, i+4)




                i = endforeach_index+1
            elif toks[i] + " " + toks[i+1][0:3] + " " + toks[i+2][0:4] + " " + toks[i+3][0:3] + toks[i+4] == "WHILE VAR COMP NUM:" or toks[i] + " " + toks[i+1][0:3] + " " + toks[i+2][0:4] + " " + toks[i+3][0:3] + toks[i+4] == "WHILE VAR COMP VAR:":
                # when a while loop is detected, check the values being compared.
                # if the comparison returns true, skip over the statement to the instruction and run it.
                # if the comparison returns false, skip over to after the next endwhile statement
                # when the instruction inside the loop is ran, the cursor reached the endwhile statement
                #

                #USE RECURSIVE PARSEFUNCTIONIN WWHILELOOPING
                # ceate an actual while loop, where the parse parses the toks list from index at the start of while loop till the end

                if toks[i+3][0:3] == "NUM":
                    endwhile_index = i
                    while toks[endwhile_index]!="ENDWHILE":
                        # need to loop to after the endwhile
                        endwhile_index+=1
                    while eval(self.getVariable(toks[i+1])[4:]+toks[i+2][5:]+toks[i+3][4:]):
                        self.parse(toks, endwhile_index, i+5)
                    i = endwhile_index+1
                elif toks[i+3][0:3] == "VAR":
                    endwhile_index = i
                    while toks[endwhile_index]!="ENDWHILE":
                        # need to loop to after the endwhile
                        endwhile_index+=1
                    while eval(self.getVariable(toks[i+1])[4:]+toks[i+2][5:]+self.getVariable(toks[i+3])[4:]):
                        self.parse(toks, endwhile_index, i+5)
                    i = endwhile_index+1

    def clear(self):
        self.tokens = []
        self.symbols = {}
        self.arrays = {}
        self.functions = {}
        self.upload_data = {}
        self.return_val = {}

    def run_file(self, filename):
        data = self.open_file(filename)
        toks = self.lex(data)
        self.parse(toks, len(toks))

    def exec_instruction(self, instruction):
        toks = self.lex(instruction+"§")
        # print(toks)
        self.parse(toks, len(toks))

        upload_data = self.upload_data
        return_data = self.return_data
        self.clear()
        return upload_data, return_data




# what to put into the api and what to do automatically:
# data signatures will be done in the vm when the parsing is finished and data tobe uploaded is returned



if __name__ == "__main__":
    interpreter = Interpreter("chain")
    interpreter.blockchain = Blockchain("")
    interpreter.blockchain.documentMap.append("data1")
    interpreter.blockchain.documentMap.append("data2")
    interpreter.blockchain.addBlock()
    interpreter.blockchain.documentMap = []
    interpreter.blockchain.documentMap.append("data3")
    interpreter.user_request = dict({"key":"key", "data": {"content1": "content", "content2": "content"}, "signature": "signature"})
    test_instruction = "$var = 5 $var1 = $var +5 while $var < $var1 { $var = $var + 1 print $var } $var3 = [ 1, 2, 4 ] $var3 append $var $var3 append 4 print $var3 $var3 pop print $var3[1 + 1] + 1 func $func($arg1) { print $var3 foreach $var3 $element { $element = $element + $arg1 } print $var3 } func $func2($arg3) { $func($arg3) } $func($var) input \"key\" $key_var input \"data\" $data_var print $key_var print $data_var "
    input_upload_test = "input \"data\" $var upload \"doc_data\" $var blockchain return $var \"return val\" + \"1\""
    upload_data, return_data = interpreter.exec_instruction(input_upload_test)
    print(upload_data, return_data)
    interpreter.blockchain.documentMap.append(upload_data)

    interpreter.blockchain.addBlock()
    interpreter.blockchain.documentMap = []

    upload_data, return_data = interpreter.exec_instruction("$index = 0 foreach blockchain $var { blockchain return $var \"document\"+$index $index = $index + 1 }")
    print(upload_data, return_data)
    print(interpreter.blockchain.blockchain_to_json())



# dataarr = open("test.txt", "r").read()
    # print(dataarr)