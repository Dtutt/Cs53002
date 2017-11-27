# CS 5300 Project 1 SQL -> relational algebra
# Luka Ivicevic and David Tutt
# Notes:
#   -   Trouble matching some single quoted strings, if test input is copy and pasted from website, 
#       the single quotes used are unicode right/left single quotation mark, if typed from my keyboard,
#       it is unicode apostrophe.
# 
#

# Imports
from pyparsing import Literal, CaselessLiteral, Word, delimitedList, Optional, \
    Combine, Group, alphas, nums, alphanums, ParseException, Forward, oneOf, quotedString, \
    ZeroOrMore, restOfLine, Keyword, upcaseTokens

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
        (columnName + in_ + selectStmt) |
        (Optional(not_) + exists_ + "(" + delimitedList(columnRval) + ")") |
        (Optional(not_) + exists_ + selectStmt) |
        (columnName + binop + "(" + selectStmt + ")") |
        ("(" + whereExpression + ")")
    )
    whereExpression << whereCondition + Optional(Group(GROUP_BY + columnName + Optional(
        HAVING + Group((funcs + binop + columnRval) | (columnName + binop + columnRval)) + ZeroOrMore(
            (and_ | or_) + Group((funcs + binop + columnRval) | (columnName + binop + columnRval)))))) + ZeroOrMore(
        (and_ | or_) + whereExpression)

    # Define the SQL grammar
    selectStmt <<= (Optional('(') + SELECT + ('*' | Group(delimitedList(Group((funcs | columnName) + Optional(S_ | R_ | B_) + Optional(AS + ident)))))("columns") + \
                    FROM + Group(delimitedList(Group(tableName + Optional(S_ | R_ | B_) + Optional(AS + ident))))("tables") + Optional((CONTAINS + "(" + selectStmt + ")")("contains")) + \
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

    print()
    print("-------------------------------------------")
    print()

    # RELATIONAL ALGEBRA TRANSLATION
    Aggfunc = ['COUNT', 'MAX', 'MAX', 'AVG', 'SUM']
    Aggfunc2 = ['GROUP BY', "HAVING"]
    # SELECT conversion
    # Create Regular Expression string
    Rastr = '[(Projection)'

    # first element of section
    first = True
    rename = False
    # SELECT conversion
    try:
        for column in parsedQuery[1]:
            if first:
                if str(column[0]) in Aggfunc:
                    Rastr = Rastr + str(column[0]) + '(' + str(column[2]) + ')'
                else:
                    Rastr = Rastr + str(column[0])
                first = False
            else:
                if str(column[0]) in Aggfunc:
                    Rastr = Rastr + ',' + str(column[0]) + '(' + str(column[2]) + ')'
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
                                renastr = "(Rename)" + "[" + str(column[2]) + '<-' + str(column[0]) + ','
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
                Rastr = Rastr + '(Select)['
                whereF=True
            else:
                for item in attr:
                    if item in Aggfunc:
                        Rastr = Rastr + str(attr[0]) + '(' + str(attr[2]) + ')' + ' = ' + str(attr[5]) + ' '
                        aggfunc1 = True
                    elif str(item) in Aggfunc2:
                        Rastr = Rastr + str(item) + '('
                        aggfunc2 = True
                    else:
                        if aggfunc2:
                            if item[0] in Aggfunc:
                                Rastr = Rastr + str(item[0]) + '(' + str(item[2]) + ')' + '=' + str(item[5]) + ' '
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
                    Rastr = Rastr + '(Rename)[' + str(table[2]) + ']' + str(table[0])
                first = False
            else:
                if table.__len__() == 1:
                    Rastr = Rastr + ' x ' + str(table[0])
                else:
                    Rastr = Rastr + 'x (Rename)[' + str(table[2]) + ']' + str(table[0])

        Rastr = Rastr + ']'
    except Exception as e:
        Rast=""
        print("Error:",e)
    return Rastr

sqlparse("SELECT S.sname FROM Sailors S WHERE NOT EXISTS (SELECT B.bid FROM Boats B WHERE NOT EXISTS (SELECT R.bid FROM Reserves R WHERE R.bid = B.bid AND R.sid = S.sid))")