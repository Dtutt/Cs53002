# CS 5300 Project 1 SQL -> relational algebra
# Luka Ivicevic and David Tutt
# Notes:
#   -   Trouble matching some single quoted strings, if test input is copy and pasted from website,
#       the single quotes used are unicode right/left single quotation mark, if typed from my keyboard,
#       it is unicode apostrophe.
#
#

# Imports
import sqlparser
import treeRA
loop=True

def validate(SQL):
    RAstr=sqlparser.sqlparse(SQL)
    print("\nRelational Algebra Expression")
    print(RAstr)
    print("\n\n Relational Algebra Tree")
    treeRA.ratree(RAstr)

with open('query.data') as f:
    i=0
    for line in f:
        print('Query '+chr(ord('A')+i)+' Results')
        validate(line)
        print('\n\n\n')
        i+=1


