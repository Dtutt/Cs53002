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

loop=True
with open('query.data') as f:
    i=0
    for line in f:
        print('Query '+chr(ord('A')+i)+' Results')
        sqlparser.sqlparse(line)
        print('\n\n\n')
        i+=1


