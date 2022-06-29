import json
import secrets
from node.level_one.blockchain import Blockchain


# TOKEN STRING:"DOCUMENT_NAME" STRING:"HOST" NUM:PORT
# creates a token
# add

class Interpreter:
    def __init__(self, blockchain, vm):
        self.tokens = []
        self.vm = vm
        self.symbols = {}
        self.arrays = {}
        self.dicts = {}

        self.functions = {}
        self.return_val = ""

        self.classes = {}
        # request data will be a reference inside the symbols dict, such as REQ:KEY

        self.blockchain = blockchain
        self.blockchain_data = {}

        self.user_request = {}

        self.upload_data = {} # includes any data that needs to be uploaded
        self.return_data = {}  # any data that needs to be added to the pool
        self.new_access_tokens = {}

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
        tokens = []
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
            # print(char)
            count+=1
            tok+=char
            # print(tok)
            if tok == " " or tok == ",": # is the , addition good?
                if var!="":
                    tokens.append("VAR:" + var)
                    # print(var)
                    var = ""
                    varStarted = 0
                elif expr != "":
                    tokens.append("NUM:" + expr)
                    expr = ""
                if state == 0:
                    tok = ""
                else:
                    # tok = " "
                    # print("tok to add", tok)
                    string += tok
                    tok = ""
            elif tok == "\\":

                if state == 0:
                    tokens.append("\\")
                    tok = ""
                else:
                    # print("hashaha gotcha")
                    # tok = " "
                    string += "\\"
                    # print(string, "string")
                    tok = ""
            elif tok == ".":
                if var != "":
                    tokens.append("VAR:" + var)
                    # print(var)
                    var = ""
                    varStarted = 0
                elif expr != "":
                    tokens.append("NUM:" + expr)
                    expr = ""
                if state == 0:
                    tok = ""
                else:
                    tok = "."
            elif tok == "\n" or char == "§" or tok == ";": #########
                if expr!="":
                    tokens.append("NUM:"+expr)
                    expr=""
                elif var!="":
                    tokens.append("VAR:"+var)
                    # print(var) problem found here
                    var = ""
                    varStarted = 0
                if tok == ";":
                    tokens.append("EOI")
                elif tok =="\n" and tokens[-1]!="NL":
                    tokens.append("NL")
                tok = ""
            elif tok == "=" and state == 0:
                if expr!="":
                    tokens.append("NUM:"+expr)
                    expr=""
                if var!="":
                    tokens.append("VAR:"+var)
                    # print(var) and here
                    var = ""
                    varStarted = 0
                if len(tokens) > 0 and tokens[-1] == "EQUALS":
                    tokens[-1] = "EQEQ"
                else:
                    tokens.append("EQUALS")
                tok = ""
            elif tok == "$" and state == 0:
                varStarted = 1
                var += tok
                tok = ""
            elif varStarted == 1:
                if tok == "<":
                    if var!="":
                        tokens.append("VAR:"+var)
                        var = ""
                        varStarted = 0
                elif tok == ")" or tok == "(":
                    if var!="":
                        tokens.append("VAR:"+var)
                        var = ""
                        varStarted = 0
                    elif expr!="":
                        tokens.append("NUM:"+expr)
                        expr=""
                    tokens.append("OP:"+tok)
                    tok = ""

                elif tok == "[" or tok == "]":
                    if var!="":
                        tokens.append("VAR:"+var)
                        var = ""
                        varStarted = 0
                    tokens.append("ARR")
                    tok=""
                else:
                    var+=tok
                    tok = ""
            elif tok == "FUNC" or tok == "func":
                tokens.append("FUNC")
                tok = ""
            elif tok == "ENDFUNC" or tok == "endfunc":
                tokens.append("FUNC")
                tok = ""
            elif tok == "PRINT" or tok == "print":
                tokens.append("PRINT")
                tok = "" # reset the token each time a valid token has been found
            elif tok == "INPUT" or tok == "input":
                tokens.append("INPUT")
                tok = ""
            elif tok == ":":
                ############# the semi colon needs to be seperate from var
                # print("reached : ")
                if state == 0:
                    if expr != "":
                        tokens.append("NUM:" + expr)
                        expr = ""
                    elif var != "" and varStarted == 1:
                        tokens.append("VAR:" + var)
                        var = ""
                        varStarted = 0
                    tokens.append(":")
                elif state == 1:
                    # print(string, "eeee")
                    string += tok
                tok = ""
            elif tok == "GET" or tok == "get":
                tokens.append("GET")
                tok = ""
            elif tok == "UPLOAD" or tok == "upload":
                tokens.append("UPLOAD")
                tok = ""
            elif tok == "IF" or tok == "if":
                tokens.append("IF")
                tok = ""
            elif tok == "ENDIF" or tok == "endif":
                tokens.append("ENDIF")
                tok = ""
            elif tok == "WHILE" or tok == "while":
                tokens.append("WHILE")
                tok = ""
            elif tok == "FOREACH" or tok == "foreach":
                tokens.append("FOREACH")
                tok = ""
            elif tok == "RETURN" or tok == "return":
                tokens.append("RETURN")
                tok = ""
            elif tok == "UPLOAD" or tok == "upload":
                tokens.append("UPLOAD")
                tok = ""
            elif tok == "GET" or tok == "get":
                tokens.append("GET")
                tok = ""
            elif tok == "BLOCKCHAIN" or tok == "blockchain":
                tokens.append("BLOCKCHAIN")
                tok = ""
            elif tok == "{":
                if state == 1:
                    string += tok
                elif len(tokens) == 0:
                    tokens.append("DICT")
                elif tokens[-1] == ":":
                    tokens.append("DICT")
                elif tokens[-1] == "EQUALS":
                    tokens.append("DICT")
                else:
                    tokens.append(":")
                tok = ""
            elif tok == "}":
                if state == 1:
                    string += tok
                elif state == 0:
                    if expr != "":
                        tokens.append("NUM:" + expr)
                        expr = ""
                    elif var != "" and varStarted == 1:
                        tokens.append("VAR:" + var)
                        var = ""
                        varStarted = 0
                    i = len(tokens) - 1
                    num_of_stmt = 0
                    while i >= 0:
                        # check for both starts and finishes
                        if tokens[i] == "ENDIF" or tokens[i] == "ENDWHILE" or tokens[i] == "ENDFUNC" or tokens[
                            i] == "ENDFOREACH" or tokens[i] == "ENDDICT":
                            num_of_stmt += 1
                        elif tokens[i] == "IF" or tokens[i] == "WHILE" or tokens[i] == "FUNC" or tokens[
                            i] == "FOREACH" or tokens[i] == "DICT":
                            if num_of_stmt == 0:
                                if tokens[i] == "IF":
                                    tokens.append("ENDIF")
                                    break
                                elif tokens[i] == "WHILE":
                                    tokens.append("ENDWHILE")
                                    break
                                elif tokens[i] == "FUNC":
                                    tokens.append("ENDFUNC")
                                    break
                                elif tokens[i] == "FOREACH":
                                    tokens.append("ENDFOREACH")
                                    break
                                elif tokens[i] == "DICT":
                                    tokens.append("ENDDICT")
                                    break
                            else:
                                num_of_stmt -= 1
                        i -= 1
                    # tokens.append("}")
                tok = ""
            elif tok == "[":
                if state == 1:
                    string += tok
                    tok = ""
                else:
                    if var != "":
                        tokens.append("VAR:" + var)
                        # print(var)
                        var = ""
                        varStarted = 0
                    elif expr != "":
                        tokens.append("NUM:" + expr)
                        expr = ""
                    tokens.append("ARR")
                    tok = ""
            elif tok == "append" or tok == "APPEND":
                tokens.append("APPEND")
                tok = ""
            elif tok == "pop" or tok == "POP":
                tokens.append("POP")
                tok = ""
            elif tok == "]":
                if state == 1:
                    string += tok
                    tok = ""
                else:
                    if var != "":
                        tokens.append("VAR:" + var)
                        # print(var)
                        var = ""
                        varStarted = 0
                    elif expr != "":
                        tokens.append("NUM:" + expr)
                        expr = ""
                    tokens.append("ENDARR")
                    tok = ""
            elif tok == "ENDWHILE" or tok == "endwhile":
                tokens.append("ENDWHILE")
                tok = ""
            elif tok == "0" or tok == "1" or tok == "2" or tok == "3" or tok == "4" or tok == "5" or tok == "6" or tok == "7" or tok == "8" or tok == "9":
                if varStarted == 1:
                    var += tok
                elif state == 1:
                    string += tok
                else:
                    expr += tok
                tok = ""
            elif tok == "+" or tok == "-" or tok == "*" or tok == "/" or tok == "(" or tok == ")" or tok == "%":
                if state == 1 and tok == "+":
                    string += tok

                elif expr != "":
                    tokens.append("NUM:" + expr)
                    expr = ""
                else:
                    tokens.append("OP:" + tok)  # ????????
                tok = ""
            elif tok == ">" or tok == "<":
                if var != "":
                    tokens.append("VAR:" + var)
                    var = ""
                    varStarted = 0
                elif expr!="":
                    tokens.append("NUM:"+expr)
                    expr=""
                tokens.append("COMP:"+tok)
                tok=""
            elif tok == "\t":
                # maybe do something here
                tok = ""
            elif tok == "\"" or tok == " \"":
                # print("\"")
                # print(string)
                if state == 0: # if a double quote sign is found when state is 0, the state is switched to 1
                    # tok = ""
                    state = 1
                elif state == 1:  # if a double quote sign is found when the state is 1, the state is switched to 0 and the string is returned
                    # print(tokens[-1], 'smth')
                    if string[-1] == "\\":
                        # print(string)
                        string += tok
                        tok = ""
                    # elif string[-1] == "\"":
                    #     # print("SHHSHSSHSH",string)
                    #     tok = ""
                    else:
                        tokens.append("STRING:" + string + "\"")
                        string = ""
                        state = 0
                        tok = ""
            elif state == 1:  # if the character is found while state is 1, the character is added to
                # if string == ["\"S"]:
                # print("such wow")
                string += tok
                tok = ""
            # print(tok)
        return tokens

    def evalExpr(self, toks, index):
        # have an eval function for strings adn arrays as well
        prev_index = index
        string = ""
        last_type = None
        isstr = 0
        count=0
        while (index<len(toks)):
            #
            if toks[index]=="NL":
                break
            # if toks[index]==":":
            #     break
            if toks[index][0:2] == "OP":
                if last_type == "VAR" or last_type == "NUM" or last_type == "STRING" or last_type == None:
                    string+=toks[index][3:]
                    last_type = toks[index][0:2]
                    index+=1
                else:
                    if index!=prev_index:
                        index-=1
                    break
            elif toks[index][0:3] == "VAR" or toks[index][0:3] == "NUM" or toks[index][0:6]=="STRING":
                if last_type == "OP" or last_type == None:
                    # print(last_type)
                    if toks[index][0:3] == "VAR":
                        # print("toks[index][0:3] == VAR")
                        varval = self.symbols[toks[index][4:]]
                        # add support for strings

                        if varval[0:3] == "NUM":

                            if isstr==1:
                                string+="\""+varval[4:]+"\""
                            else:
                                string+=varval[4:]
                        elif varval[0:3] == "VAR":
                            varval_val = self.symbols[varval[4:]]
                            if varval_val[0:3] == "NUM":
                                if isstr==1:
                                    string+="\""+varval_val[4:]+"\""
                                else:
                                    string+=varval_val[4:]
                            elif varval_val[0:6] == "STRING":
                                string+=varval_val[7:]
                                isstr=1
                        elif varval[0:6] == "STRING":
                            string+=varval[7:]
                            isstr=1
                        elif varval[0:3] == "ARR":
                            if toks[index][0:3]+" "+toks[index+1] == "VAR ARR":
                                # eval the expression inside by providing the toks and the index after the ARR token

                                val, add_to = self.evalExpr(toks, index+2)
                                # print(val)
                                # while toks[index]!="ENDARR":
                                string+=str(self.arrays[toks[index][4:]][int(val[4:])][4:])

                                while toks[index]!="ENDARR":
                                    index+=1
                            elif toks[index][0:3]+" "+toks[index+1]=="VAR POP":
                                string+=str(self.arrays[toks[index][4:]].pop()[4:])
                        elif varval[0:4]=="FUNC":

                            self.exec_func(toks, index)
                            string+=self.return_val
                        #     addmore indexes

                        elif varval[0:4] == "DICT":

                            if varval[0:4]+" "+toks[index+1] == "DICT ARR":
                                # eval the expression inside by providing the toks and the index after the ARR token

                                val, add_to = self.evalExpr(toks, index + 2)
                                dict_val = self.dicts[toks[index][4:]][val[8:-1]]
                                if dict_val[:3]=="NUM":

                                    if isstr==1:
                                        # print(self.dicts[toks[index][4:]][val[8:-1]][4:])
                                        string+="\""+dict_val[4:]+"\""
                                    else:
                                        string+=dict_val[4:]
                                elif dict_val[:3]=="VAR":
                                    # later check whether the value isastringora num
                                    if isstr==1:
                                        # print(self.dicts[toks[index][4:]][val[8:-1]][4:])
                                        string+="\""+self.symbols[dict_val[4:]][4:]+"\""
                                    else:
                                        string+=self.symbols[dict_val[4:]][4:]
                                elif dict_val[:6]=="STRING":
                                    string+=dict_val[7:]
                                    isstr=1
                                # print(index)
                                while toks[index]!="ENDARR":
                                    index+=1
                                # print(index)
                        last_type = "VAR"
                        index+=1
                    elif toks[index][0:3] == "NUM":
                        if isstr==1:
                            string+= "\""+toks[index][4:]+"\""
                        else:
                            string+= toks[index][4:]
                        last_type = toks[index][0:3]
                        index+=1
                    elif toks[index][0:6] == "STRING":
                        string+=toks[index][7:]
                        last_type = toks[index][0:6]
                        isstr=1
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
            # print(toks[index], string, index, "evalexpr")

        if isstr==1:
            return "STRING:\""+eval(string)+"\"", index-prev_index
        else:
            # print(string)
            return "NUM:"+str(eval(string)), index-prev_index

    def evalComp(self, toks, index):
        # have an eval function for strings adn arrays as well
        prev_index = index
        string = ""
        last_type = None
        count=0
        while (index<len(toks)):

            if toks[index]=="NL":
                break
            # if toks[index]==":":
            #     break
            if toks[index] == "EQEQ" or toks[index][0:2] == "OP" or toks[index][0:4] == "COMP":
                if last_type == "VAR" or last_type == "NUM" or last_type == "STRING" or last_type == None:
                    if toks[index][0:2] == "OP":
                        string+=toks[index][3:]
                        last_type = toks[index][0:2]
                        index+=1
                    elif toks[index] == "EQEQ":
                        string+="=="
                        last_type = toks[index]
                        index+=1
                    elif toks[index][0:4] == "COMP":
                        string+=toks[index][5:]
                        last_type = toks[index][0:4]
                        index+=1
                else:
                    if index!=prev_index:
                        index-=1
                    break
            elif toks[index][0:3] == "VAR" or toks[index][0:3] == "NUM" or toks[index][0:6]=="STRING":
                if last_type == "OP" or last_type == "COMP" or last_type == "EQEQ" or last_type == None:
                    # print(last_type)
                    if toks[index][0:3] == "VAR":
                        # print("toks[index][0:3] == VAR")
                        varval = self.symbols[toks[index][4:]]
                        # add support for strings
                        if varval[0:3] == "NUM":
                            string+=varval[4:]
                        elif varval[0:6] == "STRING":
                            string+=varval[7:]
                        elif varval[0:3] == "ARR":
                            if toks[index][0:3]+" "+toks[index+1] == "VAR ARR":
                                # eval the expression inside by providing the toks and the index after the ARR token

                                val, add_to = self.evalExpr(toks, index+2)
                                # print(val)
                                # while toks[index]!="ENDARR":
                                string+=str(self.arrays[toks[index][4:]][int(val[4:])][4:])

                                while toks[index]!="ENDARR":
                                    index+=1
                            elif toks[index][0:3]+" "+toks[index+1]=="VAR POP":
                                string+=str(self.arrays[toks[index][4:]].pop()[4:])
                        elif varval[0:4]=="FUNC":

                            self.exec_func(toks, index)
                            string+=self.return_val
                        #     addmore indexes

                        elif varval[0:4] == "DICT":

                            if varval[0:4]+" "+toks[index+1] == "DICT ARR":
                                # eval the expression inside by providing the toks and the index after the ARR token

                                val, add_to = self.evalExpr(toks, index + 2)
                                dict_val = self.dicts[toks[index][4:]][val[8:-1]]
                                if dict_val[:3]=="NUM":

                                    string+=dict_val[4:]
                                elif dict_val[:3]=="VAR":
                                    # later check whether the value isastringora num
                                    string+=self.symbols[dict_val[4:]][4:]
                                elif dict_val[:6]=="STRING":
                                    string+=dict_val[7:]
                                    isstr=1
                                # print(index)
                                while toks[index]!="ENDARR":
                                    index+=1
                                # print(index)
                        last_type = "VAR"
                        index+=1
                    elif toks[index][0:3] == "NUM":
                        string+= toks[index][4:]
                        last_type = toks[index][0:3]
                        index+=1
                    elif toks[index][0:6] == "STRING":
                        string+=toks[index][7:]
                        last_type = toks[index][0:6]
                        isstr=1
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
        return eval(string), index-prev_index

    def doAssign(self,varName,varVal):
        # check whether the value is a number or a variable or an expression
        self.symbols[varName[4:]] = varVal

    def getVariableTypes(self, toks, i):
        # print(toks[i], toks[i+1])
        if toks[i+1][0:2] == "OP" or toks[i+1] == "ARR":
            if self.symbols[toks[i][4:]][:4]=="FUNC":
                to_add = self.exec_func(toks, i)
                return self.return_val, to_add
            val, to_add = self.evalExpr(toks, i)
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
        self.parse_test(toks, func_desc[1], func_desc[0]+1)
        # print(endfunc_index)
        return func_args_index+1

    def getVariable(self, varName):
        if varName[4:] in self.symbols:
            if self.symbols[varName[4:]][:3]=="ARR":
                return self.arrays[self.symbols[varName[4:]][4:]]
            elif self.symbols[varName[4:]][:4]=="DICT":
                return self.dicts[self.symbols[varName[4:]][5:]]
            else:
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

    def getDict(self, toks, index):
        # print(toks[index])
        new_index = index
        new_dict = {}
        # loop until the token is not ENDDICT
        # STRING : NUM/STRING/VAR/ARR/DICT/FUNC

        while toks[new_index]!="ENDDICT":

            if toks[new_index] == "DICT":
                new_index+=1
            elif toks[new_index][:3]=="VAR" or toks[new_index][:6]=="STRING":

                # new_dict[self.symbols[toks[new_index][4:]][8:-1]] = toks[new_index+2]
                # new_index+=3
                # print(toks, toks[new_index], toks[new_index+1])
                dict_key, to_add_1 = self.evalExpr(toks, new_index)
                # check whether the val is a dict
                # can be done by checking whether the value of to_add_1+2 is DICT
                # if dict_key == "STRING:\"signature\"":
                #     new_dict[dict_key[8:-1]]=toks[new_index+to_add_1+2],toks[new_index+to_add_1+2]
                #     new_index+=to_add_1+3+to_add_2
                # else:
                # print(toks[new_index + to_add_1 + 2], )
                if toks[new_index + to_add_1 + 2] == "DICT":
                    print(toks, new_index + to_add_1 + 2)
                    dict_val, to_add_2 = self.getDict(toks, new_index + to_add_1 + 2)
                    new_dict[dict_key[8:-1]] = dict_val
                    new_index += to_add_1 + 3 + to_add_2
                else:
                    dict_val, to_add_2 = self.evalExpr(toks, new_index + to_add_1 + 2)
                    new_dict[dict_key[8:-1]] = dict_val
                    new_index += to_add_1 + 3 + to_add_2



        # print(toks[new_index])

        return new_dict, new_index-index

    def define_func(self, toks, i):
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
        return endfunc_index

    # def get_comp(self, toks, i):
    #     new_index = i
    #     condt1, to_add = self.evalExpr(toks, i+1)
    #     condt2, to_add = self.evalExpr(toks, i+2+to_add)
    #     if condt1[0:3]=="NUM" and condt2[0:3]=="NUM":
    #         return condt1[4:]+toks
    #     return

    def parse_test(self, toks, toks_end_index, toks_start_index=0):
        i = toks_start_index
        to = toks_end_index
        # INSTEAD OF HAVING SET PATTERNS,ONLY REACT TO CERTAIN KEYWORDS
        # ONCE A KEYWORD IS REACHED, THE PARSER SEEKS THE PATTERN
        # THIS ALLOWS FOR VALUES TO BE FORMED FROM EXPRESSIONS
        while (i<to):
            # print(toks[i])

            if toks[i]=="ENDIF" or toks[i]=="NL" or toks[i]=="ENDARR" or toks[i]=="ENDFUNC" or toks[i]=="ENDDICT" or toks[i]=="ENDWHILE": # tokes representing nl can be used tonotdisruptthe flow of the program, as well as disrupting the flow of some evaluations

                i+=1
            elif toks[i] == "RETURN":
                val, to_add = self.evalExpr(toks, i+1)
                self.return_val = val
                # one way to break
                i=to
                # print("Eeee")
            elif toks[i][0:3] == "VAR":

                if toks[i+1]=="OP:(" and self.symbols[toks[i][4:]][:4]=="FUNC":
                    # print("func call")
                    # print(i)
                    i+=self.exec_func(toks, i)
                    # print(i)
                elif toks[i+1]=="ARR":
                    varval = self.symbols[toks[i][4:]]
                    key,to_add_1 = self.evalExpr(toks,i+2)
                    new_val,to_add_2 = self.evalExpr(toks,i+3+to_add_1)
                    if varval[:3]=="ARR":
                        arr = self.arrays[toks[i][4:]]
                        arr[int(key[4:])]=new_val
                    if varval[:4]=="DICT":
                        dictionary = self.dicts[toks[i][4:]]
                        dictionary[int(key[4:])]=new_val
                    i+=3+to_add_1+to_add_2
                elif toks[i+1]=="POP":
                    arr = self.getVariable(toks[i])
                    arr.pop()
                    i+=2
                elif toks[i+1] == "EQUALS":
                    # how to do this
                    # use the eval exprfunction to assign nums and strings
                    #when assigning arrays and dicts, use different methods

                    if toks[i+2]=="ARR":
                        val, to_add = self.getArr(toks, i+3)
                        self.arrays[toks[i][4:]]=val

                        self.doAssign(toks[i], "ARR:"+toks[i][4:])
                    elif toks[i+2]=="DICT":
                        val, to_add = self.getDict(toks, i+3)
                        self.dicts[toks[i][4:]]=val

                        self.doAssign(toks[i], "DICT:"+toks[i][4:])
                    elif toks[i+2][0:3]=="VAR":
                        varval = self.symbols[toks[i+2][4:]]
                        to_add=0

                        if varval[:3] == "ARR":
                            if toks[i+2]=="ARR":
                                val, to_add = self.evalExpr(toks, i + 2)
                                self.doAssign(toks[i], val)
                            else:
                                # check if the value stored is an array
                                arr = self.arrays[toks[i+2][4:]]
                                self.arrays[toks[i][4:]]=arr
                                self.doAssign(toks[i], "ARR:"+toks[i][4:])
                        elif varval[:4] == "DICT":
                            if toks[i+2]=="ARR":
                                val, to_add = self.evalExpr(toks, i + 2)
                                self.doAssign(toks[i], val)
                            else:
                                # check if the value stored is an array
                                dict = self.dicts[toks[i+2][4:]]
                                self.dicts[toks[i][4:]]=dict
                                self.doAssign(toks[i], "DICT:"+toks[i][4:])
                        elif varval[:4] == "FUNC":
                            # execute the function, set the value as the returned value of that function and then
                            end_of_call_index = self.exec_func(toks,i+2)
                            self.doAssign(toks[i], self.return_val)
                            to_add+=(end_of_call_index-2)
                        else:
                            val, to_add = self.evalExpr(toks, i + 2)

                            self.doAssign(toks[i], val)
                            # print(toks[i+to_add+3])


                    else:
                        val, to_add = self.evalExpr(toks, i + 2)
                        self.doAssign(toks[i], toks[i+2])

                        # when an array gets assigned to a var, the array is stored in a dictionary
                        # the value stored in the symbols is the ARR header with the name of the variable
                        # getting the array from a variable is the matter of checking that the ARR header is present and then using what comes after as the key for the arrays dict
                    i+=to_add+3
                    # print(toks[i])
                elif toks[i+1]=="APPEND":
                    arr = self.arrays[toks[i][4:]]
                    to_add = 0
                    # print(self.dicts)
                    if toks[i + 2][0:3] == "VAR":
                        if self.symbols[toks[i + 2][4:]][:3] == "ARR" and toks[i + 3] != "ARR":
                            arr.append(self.arrays[toks[i + 2][4:]])
                        elif self.symbols[toks[i + 2][4:]][:4] == "DICT" and toks[i + 3] != "ARR":
                            arr.append(self.dicts[toks[i + 2][4:]])
                        else:
                            append_val, to_add = self.evalExpr(toks, i + 2)
                            arr.append(append_val)
                    i += 3 + to_add
            elif toks[i]=="FUNC":
                i = self.define_func(toks,i)
            elif toks[i] == "INPUT":
                #  INPUT "REQUEST_VAR_KEY" VAR
                #  inside VAR, stores the key for that value inside the user input
                #  create the blockchain api, where the values of these vars can be uploaded
                ############
                # print("input")
                key_string, to_add = self.evalExpr(toks, i + 1)
                # print(key_string[8:-1])

                req_val = self.user_request[key_string[8:-1]]

                # problem: before lexing, if value is a string, it is not detected
                # print("reqval",req_val)
                if type(req_val) == str:
                    # print("EEEE", req_val)
                    req_val_data = "STRING:\"" + req_val + "\""
                    self.symbols[toks[i + 2 + to_add][4:]] = req_val_data
                    # to_add = 0
                elif type(req_val) == int:
                    req_val_data = "NUM:" + req_val
                    self.symbols[toks[i + 2 + to_add][4:]] = req_val_data
                    # to_add = 0
                else:
                    req_val_data = self.lex(json.dumps(req_val))
                    # print(req_val_data)
                    if req_val_data[0] == "DICT":
                        req_val_dict, dict_index = self.getDict(req_val_data, 0)
                        # print(i + 2 + to_add, toks)
                        self.dicts[toks[i + 2 + to_add][4:]] = req_val_dict
                        self.symbols[toks[i + 2 + to_add][4:]] = "DICT:" + toks[i + 2 + to_add][4:]
                    else:
                        # check forlength ofthe array
                        if len(req_val_data) == 1:
                            self.symbols[toks[i + 2 + to_add][4:]] = req_val_data[0]
                            # to_add = 0
                        else:
                            req_val_arr, dict_index = self.getArr(req_val_data, 0)
                            self.dicts[toks[i + 2 + to_add][4:]] = req_val_arr
                            self.symbols[toks[i + 2 + to_add][4:]] = "ARR:" + toks[i + 2 + to_add][4:]

                            # to_add = 1
                # print(req_val_data)
                # print(toks[i+to_add+2])
                i += to_add + 3
            elif toks[i] == "UPLOAD":
                # how will uploading work:
                # either literally add whatever is stored in the document to the blockchain
                # or
                # save everything to one upload_data object and save it to the blockchain
                varval = self.symbols[toks[i+2][4:]]
                if varval[:4] =="DICT":
                    dictionary = self.dicts[varval[5:]]
                    for key in dictionary:
                        if dictionary[key][:3]=="NUM":
                            dictionary[key]=dictionary[key][4:]
                        elif dictionary[key][:6]=="STRING":
                            dictionary[key] = dictionary[key][8:-1]
                        elif dictionary[key][:3]=="VAR":
                            dict_val = self.symbols[dictionary[key][4:]]
                            if dict_val[:3]=="NUM":
                                dictionary[key]=dict_val[4:]
                            elif dict_val[:6]=="STRING":
                                dictionary[key] = dict_val[8:-1]
                    self.upload_data[toks[i+1][8:-1]] = dictionary
                elif varval[:3] =="ARR":
                    arr = self.arrays[varval[4:]]
                    for arr_i in range(len(arr)):
                        if arr[arr_i][:3]=="NUM":
                            arr[arr_i]=arr[arr_i][4:]
                        elif arr[arr_i][:6]=="STRING":
                            arr[arr_i]=arr[arr_i][7:]
                        elif arr[arr_i][:3]=="VAR":
                            arr_val = self.symbols[arr[arr_i][4:]]
                            if arr_val[:3]=="NUM":
                                arr[arr_i]=arr_val[4:]
                            elif arr_val[:6]=="STRING":
                                arr[arr_i]=arr_val[7:]
                    self.upload_data[toks[i+1][8:-1]] = arr
                else:
                    self.upload_data[toks[i+1][8:-1]] = varval
                # print("upload data", self.upload_data)
                i+=3
            elif toks[i] == "IF":
                # if var1 > var2:
                # if condition is correct, + 5
                # else, find the position of the end of the if statement and then adds that many spaces
                # print(getVariable(toks[i+1])[4:], toks[i+3][4:])
                comparison, to_add = self.evalComp(toks, i+1)
                if comparison:
                    i+=to_add+2
                else:
                    while toks[i] != "ENDIF":
                        i+=1
            elif toks[i]=="FOREACH":
                if toks[i+1]=="BLOCKCHAIN":
                    endforeach_index = i
                    counter = 0
                    while True:
                        endforeach_index += 1
                        if toks[endforeach_index] == "FOREACH":
                            counter += 1
                        elif toks[endforeach_index] == "ENDFOREACH":
                            if counter > 0:
                                counter -= 1
                            elif counter == 0:
                                break

                    for block in self.blockchain.chain:
                        for data in block.data:
                            # if "script" not in data:
                            doc_data = None
                            # print(data)
                            if "script" in data:
                                doc_data = self.lex(json.dumps(data["script"]))
                            elif "content" in data:
                                doc_data = self.lex(json.dumps(data["content"]))
                            if doc_data[0] == "DICT":
                                # print(data)
                                val, endd1ict_index = self.getDict(doc_data, 0)

                                self.dicts[toks[i + 2][4:]] = val
                                self.symbols[toks[i + 2][4:]] = "DICT:" + toks[i + 2][4:]
                            else:
                                # check forlength ofthe array
                                if len(doc_data) == 1:
                                    self.symbols[toks[i + 2][4:]] = doc_data[0]
                                else:
                                    self.symbols[toks[i + 2][4:]] = doc_data
                            self.parse_test(toks, endforeach_index, i + 4)
                            # else:

                    i = endforeach_index+1
                else:

                    endforeach_index = i
                    counter = 0
                    while True:
                        endforeach_index += 1
                        if toks[endforeach_index] == "FOREACH":
                            counter += 1
                        elif toks[endforeach_index] == "ENDFOREACH":
                            if counter > 0:
                                counter -= 1
                            elif counter == 0:
                                break

                    arr = self.getVariable(toks[i + 1])
                    for el_i in range(len(arr)):
                        self.doAssign(toks[i + 2], arr[el_i])
                        self.parse_test(toks, endforeach_index, i + 4)
                        arr[el_i] = self.symbols[toks[i + 2][4:]]
                    i = endforeach_index + 1
            elif toks[i] == "WHILE":
                # have a loop until endwhile ismet
                # if while is met, increment counter
                # if endwhile is met and counter is greater than 0, dcreement counter
                # if endwhile is met and counter is 0, set index as endwhile index
                endwhile_index = i
                counter = 0
                while True:
                    endwhile_index += 1
                    if toks[endwhile_index] == "WHILE":
                        counter += 1
                    elif toks[endwhile_index] == "ENDWHILE":
                        if counter > 0:
                            counter -= 1
                        elif counter == 0:
                            break

                comparison, to_add = self.evalComp(toks, i + 1)

                while comparison:
                    # print(toks[i+to_add+3])
                    self.parse_test(toks, endwhile_index, i+to_add+3)
                    comparison, to_add = self.evalComp(toks, i+1)
                i = endwhile_index+1
            elif toks[i] == "BLOCKCHAIN":
                # print("HWHWHWHWWHWHWHWWHWHWHWHWHWHWWHWHWHWHWH")
                if toks[i+1]=="GET":
                    # BLOCKCHAIN GET VAR STRING/NUM
                    # how will getting docs work:
                    # gets the data stored at that index and assigns it to the variable provided
                    # the actual data will be stored in the blockchain_data array
                    fetched_data = None
                    data_key, to_add = self.evalExpr(toks, i+3)
                    if data_key[:3]=="NUM":

                        data_index = int(data_key[4:])
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

                        doc_data = self.lex(json.dumps(fetched_data))

                        val, enddict_index = self.getDict(doc_data, 0)
                        self.dicts[toks[i + 2][4:]] = val
                        self.symbols[toks[i + 2][4:]] = "DICT:" + toks[i + 2][4:]
                    elif data_key[:6] == "STRING":
                        # print(self.blockchain.chain[-1].data[-1])
                        # final_data = self.blockchain.chain[-1].data[-1]
                        for block in self.blockchain.chain:
                            for data in block.data:
                                print(data)
                                # print(self.lex(json.dumps(data)))
                                if "content" in data and "name" in data["content"]:
                                    if data_key[8:-1] == data["content"]["name"]:
                                        # print("REACHED 2")
                                        fetched_data = data["content"]
                        print(fetched_data)
                        if type(fetched_data) == str:
                            # print("EEEE", toks[i+3])
                            req_val_data = "STRING:\"" + fetched_data + "\""
                            self.symbols[toks[i + 2 + to_add][4:]] = req_val_data
                            # to_add = 0
                        elif type(fetched_data) == int:
                            req_val_data = "NUM:" + fetched_data
                            self.symbols[toks[i + 2 + to_add][4:]] = req_val_data
                            # to_add = 0
                        else:
                            doc_data = self.lex(json.dumps(fetched_data))
                            print(fetched_data)
                            if doc_data[0] == "DICT":
                                val, enddict_index = self.getDict(doc_data, 0)
                                # print(val)
                                self.dicts[toks[i + 2][4:]] = val
                                self.symbols[toks[i + 2][4:]] = "DICT:" + toks[i + 2][4:]
                            else:
                                # check forlength ofthe array
                                if len(doc_data) == 1:
                                    self.symbols[toks[i + 2][4:]] = doc_data[0]
                                else:
                                    self.symbols[toks[i + 2][4:]] = doc_data
                    # toks[i+3+to_add]
                    i += 4 + to_add
                elif toks[i+1]=="RETURN":
                    # print("RECHE")
                    string, to_add = self.evalExpr(toks, i + 3)
                    varval = self.symbols[toks[i + 2][4:]]
                    if varval[:4] == "DICT":
                        dictionary = self.dicts[varval[5:]]
                        # print(dictionary)
                        for key in dictionary:
                            if dictionary[key][:3] == "NUM":
                                dictionary[key] = dictionary[key][4:]
                            elif dictionary[key][:6] == "STRING":
                                dictionary[key] = dictionary[key][7:]
                            elif dictionary[key][:3] == "VAR":
                                dict_val = self.symbols[dictionary[key][4:]]
                                if dict_val[:3] == "NUM":
                                    dictionary[key] = dict_val[4:]
                                elif dict_val[:6] == "STRING":
                                    dictionary[key] = dict_val[7:]
                        self.return_data[string[8:-1]] = dictionary
                    elif varval[:3] == "ARR":
                        arr = self.arrays[varval[4:]]
                        for arr_i in range(len(arr)):
                            el_data = self.lex(json.dumps(arr[arr_i]))
                            if el_data[0] == "DICT":
                                pass
                            else:
                                if arr[arr_i][:3] == "NUM":
                                    arr[arr_i] = arr[arr_i][4:]
                                elif arr[arr_i][:6] == "STRING":
                                    arr[arr_i] = arr[arr_i][7:]
                                elif arr[arr_i][:3] == "VAR":
                                    arr_val = self.symbols[arr[arr_i][4:]]
                                    if arr_val[:3] == "NUM":
                                        arr[arr_i] = arr_val[4:]
                                    elif arr_val[:6] == "STRING":
                                        arr[arr_i] = arr_val[7:]
                        self.return_data[string[8:-1]] = arr
                    else:
                        self.return_data[string[8:-1]] = varval

                    i += 4 + to_add
            elif toks[i] == "TOKEN":
                # granting:
                # TOKEN GRANT STRING:"NAME_OF_DOC" STRING:"CHAIN_TOKEN"
                # accessing
                # TOKEN ACCESS STRING:"CHAIN_TOKEN"
                if toks[i + 1] == "GRANT":
                    name_of_doc, to_add = self.evalExpr(toks, i + 2)
                    external_chain_token, to_add = self.evalExpr(toks, i + 2 + name_of_doc)
                    self.new_access_tokens[str(secrets.token_hex(16))] = {'chain_token': external_chain_token,
                                                                          'name_of_doc': name_of_doc}
                    i += to_add + 2
                elif toks[i + 1] == "ACCESS":
                    access_token, to_add = self.evalExpr(toks, i + 2)
                    pass
                    # function in the vm that connects to another node and gets data by access token
                    # function will be accessible y direct route or thoough the interpreter
            else:
                break

    def clear(self):
        self.tokens = list()
        self.symbols = dict()
        self.arrays = dict()
        self.functions = dict()
        self.upload_data = dict()
        self.return_val = dict()
        self.return_data = dict()

    def exec_instruction_test(self, instruction):
        toks = self.lex(instruction + "§")
        print(toks)
        self.parse_test(toks, len(toks))
        # print(instruction, self.upload_data, self.return_data, self.symbols, self.dicts)
        upload_data = dict(self.upload_data)
        return_data = dict(self.return_data)
        # print("return data", self.return_data)
        self.clear()
        return upload_data, return_data

    # def exec_instruction(self, instruction):
    #     toks = self.lex(instruction+"§")
    #     print(toks)
    #     self.parse(toks, len(toks))
    #     upload_data = self.upload_data
    #     return_data = self.return_data
    #     self.clear()
    #     return upload_data, return_data




# what to put into the api and what to do automatically:
# data signatures will be done in the vm when the parsing is finished and data tobe uploaded is returned

# have a function that checkswhetherthe value being got is a string or a num

if __name__ == "__main__":
    interpreter = Interpreter("chain", "vm")
    interpreter.blockchain = Blockchain("")
    interpreter.blockchain.documentMap.append(
        {'script': {'route': 'upload_data', 'instruction': 'input "data" $var upload "doc_data" $var'}, 'signature': (
            107500695781264076404092045543405215499556981663122697785336867366830724747670,
            86647951037369554566547419937285212811305410737331794412213829469499743283225),
         'public_key': '-----BEGIN PUBLIC KEY-----\nMFYwEAYHKoZIzj0CAQYFK4EEAAoDQgAE7U3zJrO81Ike+GmNAim4T6TEfxkGup73\nlcHtNffTpSUl6L0n5AAUIpqG7zfg9ISPX3SNMUp6QNfmeb8YC1DRWQ==\n-----END PUBLIC KEY-----\n'})
    interpreter.blockchain.documentMap.append({'script': {'route': 'get_data',
                                                          'instruction': ' $arr = [ ] foreach blockchain $var { $arr append $var } blockchain return $arr "data"'},
                                               'signature': (
                                                   45053582901900210505014240088863943595482585855593071922571908052600085002059,
                                                   71608025411767655957430079021300988156124727024113088923880695520816108361007),
                                               'public_key': '-----BEGIN PUBLIC KEY-----\nMFYwEAYHKoZIzj0CAQYFK4EEAAoDQgAE7U3zJrO81Ike+GmNAim4T6TEfxkGup73\nlcHtNffTpSUl6L0n5AAUIpqG7zfg9ISPX3SNMUp6QNfmeb8YC1DRWQ==\n-----END PUBLIC KEY-----\n'})
    interpreter.blockchain.documentMap.append({'content': {'data': 'name', 'name': 'name'}})

    interpreter.blockchain.addBlock()
    interpreter.blockchain.documentMap = []
    interpreter.blockchain.documentMap.append({"content": {'data': 'data3'}})
    interpreter.user_request = dict(
        {"key": "key", "data": {"content1": "content", "content2": "content"}, "signature": "signature",
         "doc_name": "name"})
    test_instruction = "$var = 5 $var1 = $var +5 while $var < $var1 { $var = $var + 1 } $var3 = [ 1, 2, 4 ] $var3 append $var $var3 append 4 $var3 pop func $func($arg1) { foreach $var3 $element { $element = $element + $arg1 } } func $func2($arg3) { $func($arg3) } $func($var) input \"key\" $key_var input \"data\" $data_var $dict_var = {\"dict_val\" : $var, } "
    input_upload_test = "input \"data\" $var upload \"doc_data\" $var blockchain return $var \"return val\" + \"1\""
    dict_test = "$dict_var = {\"dict_val\" : 4 }"
    return_test = " $arr = [ ] foreach blockchain $var { $arr append $var } blockchain return $arr \"data\""
    # upload_data, return_data = interpreter.exec_instruction(input_upload_test)
    # for char in :
    # print(interpreter.lex(json.dumps({'route': 'get_data', "instruction": "$index = 0 foreach blockchain $var { blockchain return $var \"document\"+$index $index = $index + 1 }"})))
    get_named_data_test = " input \"doc_name\" $name blockchain get $var $name blockchain return $var \"data\" "
    upload_data, return_data = interpreter.exec_instruction_test(input_upload_test)
    print(return_data)
    # upload_data, return_data = interpreter.exec_instruction_test("input \"data\" $var upload \"doc_data\" $var")
    # upload_data, return_data = interpreter.exec_instruction("$var = {\"kay_val\": 3, \"kay_val1\": 3} print $var[\"kay_val\"]")
    # print(upload_data, return_data)
    # interpreter.blockchain.documentMap.append(upload_data)
    # interpreter.blockchain.addBlock()
    # interpreter.blockchain.documentMap = []

    # upload_data, return_data = interpreter.exec_instruction("$index = 0 foreach blockchain $var { blockchain return $var \"document\"+$index $index = $index + 1 }")
    # print(upload_data, return_data)
    # print(interpreter.blockchain.blockchain_to_json())
