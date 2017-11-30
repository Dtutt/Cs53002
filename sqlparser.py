# CS 5300 Project 1 SQL -> relational algebra
# Luka Ivicevic and David Tutt
# Notes:
#   -   Trouble matching some single quoted strings, if test input is copy and pasted from website, 
#       the single quotes used are unicode right/left single quotation mark, if typed from my keyboard,
#       it is unicode apostrophe.
# 
#

# Imports
from anytree import Node, RenderTree

from pyparsing import Literal, CaselessLiteral, Word, delimitedList, Optional, \
    Combine, Group, alphas, nums, alphanums, ParseException, Forward, oneOf, quotedString, \
    ZeroOrMore, restOfLine, Keyword, upcaseTokens

def printtree(root):
    print("\nQuery Tree\n")
    for pre, fill, node in RenderTree(root):
        print("%s%s" % (pre, node.name))
    return

def optimizeTree(root,ftable,whereN):
    temp1=root
    temp2=ftable
    temp3=whereN
    optmize=[]
    fvar=[]
    keywords=["AS", "AND", "IN", "GROUP BY" ]
    open=False
    Ostring=""
    poss=False
    possibleO=[]
    found=[]
    for node in ftable:
        temp=node.name.replace('{RENAME}[','')
        possibleO.append(temp.replace(']','.'))
    temp=whereN.name.replace('{Select}','')

    for word in temp.split():
        if poss==False:
            for name in possibleO:
                if name in word:
                    poss=True
                    word.replace('[','')
                    word.replace(']','')
                    Ostring+=word+" "
                    tempf='{RENAME}['+name.replace('.','')+']'
                if word in keywords:
                    Ostring = ""
                    poss = False
        else:
            for name in possibleO:
                if name in word:
                    poss=False
                    Ostring=""
            if word[0]=="\'" and word[-1]=="\'":
                open=True
                Ostring+=word+" "
                found.append(Ostring)
                fvar.append(tempf)
                tempf=""
                poss=False
            elif word in keywords:
                Ostring=""
                poss=False
            else:
                Ostring+=word+" "
    if found.__len__()>0:
        for item in found:
            whereN.name=whereN.name.replace(item,'')
        if whereN.name.split()[-2] =='AND':
            temp=whereN.name
            whereN.name=temp.replace(" AND ]",']')
        for node in ftable:
            counter=0
            for var in fvar:
                if var in node.name:
                    optmize.append(Node(found[counter],node.parent))
                    node.parent=optmize[counter]
                    counter+=1
        printtree(root)


    return root

def parseQsql(columns,whereExp,tables):
    # RELATIONAL ALGEBRA TRANSLATION
    Aggfunc = ['COUNT', 'MAX', 'MAX', 'AVG', 'SUM']
    Aggfunc2 = ['GROUP BY', "HAVING"]
    # SELECT conversion
    # Create Regular Expression string
    Rastr = '{Projection}['

    # first element of section
    first = True
    rename = False
    # SELECT conversion
    try:
        for column in columns:
            if first:
                if str(column[0]) in Aggfunc:
                    Rastr = Rastr + str(column[column.__len__()-1])
                else:
                    Rastr = Rastr + str(column[0])
                first = False
            else:
                if str(column[0]) in Aggfunc:
                    Rastr = Rastr +','+ str(column[column.__len__() - 1])
                else:
                    Rastr = Rastr + ',' + str(column[0])

            # Rename Set
            found=False
            if column.__len__() > 1:
                if 'AS' in str(column):
                    for item in (column):
                        if str(item)=="AS":
                            found=True
                        elif found:
                            if rename:
                                renastr = renastr + ',' + str(column[2])
                            else:
                                renastr = "{Rename}" + "[" +str(column[0])+'('+ str(column[2]) +')' + '<-' + str(column[column.__len__() - 1]) + ','
                                rename = True
                            found=False

        if rename:
            Rastr = renastr + "]" + Rastr
        Rastr+="]"
        # WHERE conversion
        wheref=False
        for attr in whereExp:
            #if agg function detected
            aggfunc1 = False
            aggfunc2 = False
            #checks if and/or found
            if str(attr) == "AND" or str(attr) == 'OR':
                Rastr = Rastr + str(attr) + " "
            # checks for where statement and converts to select
            elif str(attr) == "WHERE":
                Rastr = Rastr + '{Select}['
                wheref=True
            else:
                for item in attr:
                    if str(item) in Aggfunc:
                        Rastr = Rastr + str(attr[0]) + '(' + str(attr[2]) + ')' + ' = ' + str(attr[5]) + ' '
                        aggfunc1 = True
                    elif str(item) in Aggfunc2:
                        Rastr = Rastr + str(item) + '('
                        aggfunc2 = True
                    else:
                        if aggfunc2:
                            if item[0] in Aggfunc:
                                Rastr = Rastr + str(item[0]) + '(' + str(item[2]) + ')' + '=' + str(item[5])
                            elif str(item) == "AND" or str(item) == "OR":
                                Rastr = Rastr + str(item) + " "
                            else:
                                Rastr = Rastr + str(item) + ') '
                        elif not aggfunc1:
                            Rastr = Rastr + str(item) + ' '
                if aggfunc2:
                    Rastr = Rastr + ')'
        if wheref:
            Rastr = Rastr + ']'

        # FROM conversion of SQL
        Rastr = Rastr + '['
        first = True
        for table in tables:
            if first:
                if table.__len__() == 1:
                    Rastr = Rastr + str(table[0])
                else:
                    Rastr = Rastr + '{Rename}[' + str(table[2]) + ']' + str(table[0])
                first = False
            else:
                if table.__len__() == 1:
                    Rastr = Rastr + ' X ' + str(table[0])
                elif table.__len__()==2:
                    Rastr= Rastr + ' X {Rename}[' + str(table[1]) + ']' + str(table[0])
                else:
                    Rastr = Rastr + ' X {Rename}[' + str(table[2]) + ']' + str(table[0])

        Rastr = Rastr + ']'
    except Exception as e:
        Rast=""
        print("Error:",e)
        if Rastr.endswith('['):
            Rastr=Rastr[:-1]

    return Rastr



def selectTree(columns,whereExp,tables):
    tablesN=[]
    renameN=[]
    renastrF=False
    # RELATIONAL ALGEBRA TRANSLATION
    Aggfunc = ['COUNT', 'MAX', 'MAX', 'AVG', 'SUM']
    Aggfunc2 = ['GROUP BY', "HAVING"]
    # SELECT conversion
    # Create Regular Expression string
    element = '{Projection}['

    # first element of section
    first = True
    rename = False
    # Projection NODE
    try:
        for column in columns:
            if first:
                if str(column[0]) in Aggfunc:
                    element = element + str(column[column.__len__()-1])
                else:
                    element = element + str(column[0])
                first = False
            else:
                if str(column[0]) in Aggfunc:
                    element = element +','+ str(column[column.__len__() - 1])
                else:
                    element = element + ',' + str(column[0])
            # Rename Set Node
            projectionN=Node(element+']')
            found=False
            if column.__len__() > 1:
                if 'AS' in str(column):
                    for item in (column):
                        if str(item)=="AS":
                            found=True
                        elif found:
                            if rename:
                                renastr = renastr + ',' + str(column[2])
                            else:
                                renastr = "{Rename}" + "[" +str(column[0])+'('+ str(column[2]) +')' + '<-' + str(column[column.__len__() - 1]) + ','
                                rename = True
                            found=False

        if rename:
            renastrN = Node(renastr+']')
            renastrF=True
        element=""
        # WHERE To Nodes
        wheref=False
        for attr in whereExp:
            #if agg function detected
            aggfunc1 = False
            aggfunc2 = False
            #checks if and/or found
            if str(attr) == "AND" or str(attr) == 'OR':
                element = element + str(attr) + " "
            # checks for where statement and converts to select
            elif str(attr) == "WHERE":
                element = element + '{Select}['
                wheref=True
            else:
                for item in attr:
                    if str(item) in Aggfunc:
                        element = element + str(attr[0]) + '(' + str(attr[2]) + ')' + ' = ' + str(attr[5]) + ' '
                        aggfunc1 = True
                    elif str(item) in Aggfunc2:
                        element = element + str(item) + '('
                        aggfunc2 = True
                    else:
                        if aggfunc2:
                            if item[0] in Aggfunc:
                                element = element + str(item[0]) + '(' + str(item[2]) + ')' + '=' + str(item[5])
                            elif str(item) == "AND" or str(item) == "OR":
                                element = element + str(item) + " "
                            else:
                                element = element + str(item) + ') '
                        elif not aggfunc1:
                            element = element + str(item) + ' '
                if aggfunc2:
                    element = element + ')'
        if wheref:
            element = element + ']'
        whereN=Node(element)
        # Create Table Nodes and their rename
        for table in tables:
            if table.__len__() == 1:
                tablesN.append(Node(str(table[0])))
            elif table.__len__()==2:
                tablesN.append(Node(str(table[0])))
                renameN.append(Node('{RENAME}[' + str(table[1]) + ']'))
            else:
                tablesN.append(Node(str(table[0])))
                renameN.append(Node('{RENAME}['+str(table[2])+']'))
    except Exception as e:
        print(e)
    #create Tree

    #Make Projection above Select Statment

    #Checks if renamed Attr projected and makes renamed attr roots else makes Projection root
    if renastrF:
        renastrN.parent=projectionN
        whereN.parent=renastrN
    else:
        whereN.parent=projectionN
    root=projectionN
    #swaps tablesN and rename data and makes TablesN the parrent of RenamesN
    ftable=[]
    if renameN.__len__()>0:
        size=renameN.__len__()
        for i in range(0,renameN.__len__()):
            ftable.append(Node(renameN[i].name))
            ftable[i].children=[tablesN[i]]
    else:
        for i in range(0,tablesN.__len__()):
            ftable.append(Node(tablesN[i].name))
    #Create Cross Product Roots
    if ftable.__len__()==3:
        tempcross=Node('X')
        ftable[0].parent=tempcross
        ftable[1].parent=tempcross
        tempcross2=Node('X')
        ftable[2].parent=tempcross2
        tempcross.parent=tempcross2
        tempcross2.parent=whereN
    elif ftable.__len__()==2:
        tempcross=Node('X')
        ftable[0].parent=tempcross
        ftable[1].parent=tempcross
        tempcross.parent = whereN
    elif ftable.__len__()==1:
        ftable[0].parent=whereN
    printtree(root)
    root=optimizeTree(root,ftable,whereN)
    return root

def sqlparse(sql):
    # Define SQL tokens
    print("SQL Validating")
    selectStmt = Forward()
    SELECT = Keyword("select", caseless=True).addParseAction(upcaseTokens)
    FROM = Keyword("from", caseless=True).addParseAction(upcaseTokens)
    WHERE = Keyword("where", caseless=True).addParseAction(upcaseTokens)
    AS = Keyword("as", caseless=True).addParseAction(upcaseTokens)
    UNION = Keyword("union", caseless=True).addParseAction(upcaseTokens)
    INTERSECT = Keyword("intersect", caseless=True).addParseAction(upcaseTokens)
    EXCEPT = Keyword("except", caseless=True).addParseAction(upcaseTokens)
    COUNT = Keyword("count", caseless=True).addParseAction(upcaseTokens)
    MAX = Keyword("max", caseless=True).addParseAction(upcaseTokens)
    AVG = Keyword("avg", caseless=True).addParseAction(upcaseTokens)
    SUM = Keyword("sum", caseless=True).addParseAction(upcaseTokens)
    S_ = Keyword("S", caseless=True).addParseAction(upcaseTokens)
    S2_ = Keyword("S2", caseless=True).addParseAction(upcaseTokens)
    R_ = Keyword("R", caseless=True).addParseAction(upcaseTokens)
    B_ = Keyword("B", caseless=True).addParseAction(upcaseTokens)

    ident = Word(alphas, alphanums + "_$").setName("identifier")
    columnName = (delimitedList(ident, ".", combine=True)).setName("column name").addParseAction(upcaseTokens)
    columnNameList = Group(delimitedList(columnName))
    tableName = (delimitedList(ident, ".", combine=True)).setName("table name").addParseAction(upcaseTokens)
    tableNameAs = (delimitedList(ident + " " + AS + " " + ident, ",", combine=True)).setName("table name").addParseAction(
        upcaseTokens)
    tableNameList = delimitedList(tableName)
    funcs = ((COUNT | MAX | AVG | SUM) + "(" + ("*" | columnName) + ")")

    whereExpression = Forward()
    space_ = Keyword(" ", caseless=True).addParseAction(upcaseTokens) 
    and_ = Keyword("and", caseless=True).addParseAction(upcaseTokens)
    or_ = Keyword("or", caseless=True).addParseAction(upcaseTokens)
    in_ = Keyword("in", caseless=True).addParseAction(upcaseTokens)
    exists_ = Keyword("exists", caseless=True).addParseAction(upcaseTokens)
    not_ = Keyword("not", caseless=True).addParseAction(upcaseTokens)
    GROUP_BY = Keyword("group by", caseless=True).addParseAction(upcaseTokens)
    HAVING = Keyword("having", caseless=True).addParseAction(upcaseTokens)
    CONTAINS = Keyword("contains", caseless=True).addParseAction(upcaseTokens)

    E = CaselessLiteral("E")
    binop = oneOf("= != < > >= <= eq ne lt le gt ge", caseless=True)
    arithSign = Word("+-", exact=1)
    realNum = Combine(Optional(arithSign) + (Word(nums) + "." + Optional(Word(nums)) |
                                             ("." + Word(nums))) +
                      Optional(E + Optional(arithSign) + Word(nums)))
    intNum = Combine(Optional(arithSign) + Word(nums) +
                     Optional(E + Optional("+") + Word(nums)))

    columnRval = realNum | intNum | quotedString | columnName
    whereCondition = Group(
        (funcs + binop + columnRval) |
        (columnName + binop + columnRval) |
        (columnName + in_ + "(" + delimitedList(columnRval) + ")") |
        (columnName + in_ + Optional("(") + Group(selectStmt) + Optional(")")) |
        (Optional(not_) + exists_ + "(" + delimitedList(columnRval) + ")") |
        (Optional(not_) + exists_ + Group(selectStmt)) |
        (columnName + binop + Group(selectStmt)) |
        ("(" + whereExpression + ")")
    )
    whereExpression << whereCondition + Optional(Group(GROUP_BY + columnName + Optional(
        HAVING + Group((funcs + binop + columnRval) | (columnName + binop + columnRval)) + ZeroOrMore(
            (and_ | or_) + Group((funcs + binop + columnRval) | (columnName + binop + columnRval)))))) + ZeroOrMore(
        (and_ | or_) + whereExpression)

    # Define the SQL grammar
    selectStmt <<= (Optional('(') + SELECT + ('*' | Group(delimitedList(Group((funcs | columnName) + Optional(S_ | R_ | B_ | S2_) + Optional(AS + ident)))))("columns") + \
                    FROM + Group(delimitedList(Group(tableName + Optional(S_ | R_ | B_ | S2_) + Optional(AS + ident))))("tables") + Optional((CONTAINS + "(" + selectStmt + ")")("contains")) + \
                    Optional(Group(WHERE + whereExpression), "")("where") + Optional(')')) + \
                   Optional((UNION + selectStmt)("union") | (INTERSECT + selectStmt)("intersect") | (EXCEPT + selectStmt)(
                       "except"))

    SQLParser = selectStmt

    # Begin validation
    try:
        print(sql, "\n-------------------------------------------\n", SQLParser.parseString(sql), "")
        parsedQuery = SQLParser.parseString(sql)
        print("-------------------------------------------")
    except Exception as e:
        print("-------------------------------------------")
        print("SYNTAX ERROR PARSING: " + sql)
        print("-------------------------------------------")
        print("ERROR MESSAGE:")
        print("-------------------------------------------")
        print(e)
        return "error"

    # List of tables being used

    tables = parsedQuery[3]
    tables_rename = ["SAILORS", "BOATS", "RESERVES"]
    # List of attributes being used in select
    attributes = parsedQuery[1]

    # Define the schema
    sailors = (
        ("tname", "sailors"),
        ("sid", "int"),
        ("sname", "str"),
        ("rating", "int"),
        ("age", "real")
    )
    boats = (
        ("tname", "boats"),
        ("bid", "int"),
        ("bname", "str"),
        ("color", "str")
    )
    reserves = (
        ("tname", "reserves"),
        ("sid", "int"),
        ("bid", "int"),
        ("day", "date")
    )

    print("Error messages (if any):")

    # Check if the table used in the query are valid based on the schema
    for item in tables:
        if (str(item[0]).upper() != sailors[0][1].upper()) and (str(item[0]).upper() != reserves[0][1].upper()) and (str(item[0]).upper() != boats[0][1].upper()):
            print(item[0] + " is not a table in the schema.")
        else:
            # Check for renaming
            if ( len(item) > 2 ):
                tables_rename.append( item[2].upper() )
            elif ( len(item) > 1 ):
                tables_rename.append( item[1].upper() )


    # Check if the select attributes are valid according to the schema and what tables are being used in the query
    # - Iterate through each attributes
    # - Check if it's a built-in function, if it is then get the 2 index (that will be the attribute)
    # - If it's not a build in function, then get the 0 index (that will be the attribute)
    # - Check if that attribute is in any of the tables
    # - If it is, make sure that table is being used in the query (check if the table is in 'tables')
    attrTablePairs = []
    for attribute in attributes:
        # Extract the correct attribute
        if (str(attribute[0]).upper() == "COUNT") or (str(attribute[0]).upper() == "MAX") or (
            str(attribute[0]).upper() == "AVG") or (str(attribute[0]).upper() == "SUM"):
            attr = attribute[2]
        else:
            attr = attribute[0]
        if "." in attr:
            # Check if table is valid
            if attr.split(".")[0] not in tables_rename:
                print(attr.split(".")[0] + " is not a valid renamed table.")
            attr = attr.split(".")[1]
        # Check if the attribute is in any of the tables in the schema
        isInTable = False
        attrTableName = ""
        for item in sailors:
            if (item[0].upper() == attr or attr == "*"):
                isInTable = True
                attrTableName = "SAILORS"
                attrTablePairs.append( (attr, attrTableName) )
                break
        for item in boats:
            if (item[0].upper() == attr or attr == "*"):
                isInTable = True
                attrTableName = "BOATS"
                attrTablePairs.append( (attr, attrTableName) )
                break
        for item in reserves:
            if (item[0].upper() == attr or attr == "*"):
                isInTable = True
                attrTableName = "RESERVES"
                attrTablePairs.append( (attr, attrTableName) )
                break
        if (isInTable == False):
            print(attr + " is not an attribute in the schema.")
            # Do something since an attribute is invalid

    # Check to see if the corresponding table is being used in the query
    attrUsed = []
    for pair in attrTablePairs:
        beingUsed = False
        if (pair[0] == "*"):
            beingUsed = True
            attrUsed.append( pair[0] )
        for table in tables:
            if (pair[1] == str(table[0].upper())):
                beingUsed = True
                attrUsed.append( pair[0] )
                break
        if (beingUsed == False and pair[0] not in attrUsed):
            # Attribute is invalid as the table it belongs to is not being used in the query
            print(str(pair[0]) + " is invalid as the table it belongs to (" + str(
                pair[1]) + ") is not being used in the query.")

    tables_used = []
    for table in tables:
        tables_used.append( table[0] )
    # Check if the attributes being used in the WHERE stmnt are valid
    # - Check if WHERE stmnt exists
    if (len(parsedQuery) >= 5):
        whereExp = parsedQuery[4]
        for exp in whereExp:
            if (exp != "WHERE" and exp != "AND" and exp != "OR"):
                if (exp[0] == "GROUP BY"):
                    valid = False
                    myAttr = str(exp[1]).upper()
                    if ( "." in myAttr ):
                            myTableRename = myAttr.split(".")[0]
                            myAttr = myAttr.split(".")[1]
                            # Check if the table rename is valid
                            if (myTableRename not in tables_rename):
                                print(myTableRename + " is not a valid table name")
                    for table in tables_used:
                            if (table == "SAILORS"):
                                # Check if attr is in sailors
                                for item in sailors:
                                    if ( myAttr in str(item[0]).upper() ):
                                        valid = True
                            if (table == "RESERVES"):
                                # Check if attr is in reserves
                                for item in reserves:
                                    if ( myAttr in str(item[0]).upper() ):
                                        valid = True
                            if (table == "BOATS"):
                                # Check if attr is in reserves
                                for item in boats:
                                    if ( myAttr in str(item[0]).upper() ):
                                        valid = True
                    if (valid == False):
                        print(exp[1] + " in the group by clause is not a valid attribute")
                        return "invalid"
                else:
                    if (exp[0] == "COUNT" or exp[0] == "MAX" or exp[0] == "AVG" or exp[0] == "SUM"):
                        # Check if the attribute is valid
                        myAttr = str(exp[2]).upper()
                        if ( "." in myAttr ):
                            myTableRename = myAttr.split(".")[0]
                            myAttr = myAttr.split(".")[1]
                            # Check if the table rename is valid
                            if (myTableRename not in tables_rename):
                                print(myTableRename + " is not a valid table name")
                        valid = False
                        
                        for table in tables_used:
                            if (table == "SAILORS"):
                                # Check if attr is in sailors
                                for item in sailors:
                                    if ( myAttr in str(item[0]).upper() ):
                                        valid = True
                            if (table == "RESERVES"):
                                # Check if attr is in reserves
                                for item in reserves:
                                    if ( myAttr in str(item[0]).upper() ):
                                        valid = True
                            if (table == "BOATS"):
                                # Check if attr is in reserves
                                for item in boats:
                                    if ( myAttr in str(item[0]).upper() ):
                                        valid = True

                        if (valid == False):
                            print(exp[2] + " in the where clause is not a valid attribute")
                            return "invalid"

                    elif ("." in exp[0]):
                        # Check if the attribute is valid
                        valid = False
                        myTableRename = exp[0].split(".")[0]
                        myAttr = exp[0].split(".")[1]
                        
                        for table in tables_used:
                            if (table == "SAILORS"):
                                # Check if attr is in sailors
                                for item in sailors:
                                    if ( myAttr in str(item[0]).upper() and ( myTableRename == 'S' or myTableRename == "SAILORS") ):
                                        valid = True
                            if (table == "RESERVES"):
                                # Check if attr is in reserves
                                for item in reserves:
                                    if ( myAttr in str(item[0]).upper() and ( myTableRename == 'R' or myTableRename == "RESERVES") ):
                                        valid = True
                            if (table == "BOATS"):
                                # Check if attr is in reserves
                                for item in boats:
                                    if ( myAttr in str(item[0]).upper() and ( myTableRename == 'B'  or myTableRename == "BOATS" ) ):
                                        valid = True
                        # Check if the table rename is valid

                        if (myTableRename not in tables_rename):
                            print(myTableRename + " is not a valid table name")
                        if (valid == False):
                            print(exp[0] + " in the where clause is not a valid attribute")
                            return "invalid"
                    else:
                        # Check if the attribute is valid
                        # Go through tables being used, check if attribute belongs to one of them
                        valid = False
                        for table in tables_used:
                            if (table == "SAILORS"):
                                # Check if attr is in sailors
                                for item in sailors:
                                    if ( exp[0] in str(item[0]).upper() ):
                                        valid = True
                            if (table == "RESERVES"):
                                # Check if attr is in reserves
                                for item in reserves:
                                    if ( exp[0] in str(item[0]).upper() ):
                                        valid = True
                            if (table == "BOATS"):
                                # Check if attr is in reserves
                                for item in boats:
                                    if ( exp[0] in str(item[0]).upper() ):
                                        valid = True
                        if ( exp[0] == "NOT" ):
                            valid = True
                        if (valid == False):
                            print(exp[0] + " in the where clause is not a valid attribute")
                            return "invalid"

    #CHECKS FOR Correct table rename format

    print()
    print("-------------------------------------------")
    print()
    Rastr=parseQsql(parsedQuery[1],whereExp,tables)
    if parsedQuery.__len__()==11:
        if parsedQuery[5]=="UNION":
            Rastr+= "(UNION)"+parseQsql(parsedQuery[7],parsedQuery[10],parsedQuery[9])
        if parsedQuery[5] == "INTERSECT":
            Rastr += "(INTERSECT)" + parseQsql(parsedQuery[7], parsedQuery[10], parsedQuery[9])
        if parsedQuery[5] == "EXCEPT":
            Rastr += " - " + parseQsql(parsedQuery[7], parsedQuery[10], parsedQuery[9])
    print("\nRelational Algebra Expression")
    print(Rastr)

    root=selectTree(parsedQuery[1],whereExp,tables)
    if parsedQuery.__len__()==11:
        if parsedQuery[5]=="UNION":
            nroot=Node('{UNION}')
            root.parent=nroot
            temp2=selectTree(parsedQuery[7],parsedQuery[10],parsedQuery[9])
            temp2.parent=nroot
            printtree(nroot)
            return nroot
        if parsedQuery[5] == "INTERSECT":
            nroot=Node('{INTERSECT}')
            root.parent=nroot
            temp2=selectTree(parsedQuery[7],parsedQuery[10],parsedQuery[9])
            temp2.parent=nroot
            printtree(nroot)
            return nroot
        if parsedQuery[5] == "EXCEPT":
            nroot=Node('{-}')
            root.parent=nroot
            temp2=selectTree(parsedQuery[7],parsedQuery[10],parsedQuery[9])
            temp2.parent=nroot
            printtree(nroot)
            return nroot
    return root
