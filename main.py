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

#control for program
while loop:
    print("1. Run Query")
    print("2. End")
    choice = input("enter number of option ")
    choice='1'
    if choice=='1':
        SQL=input("Enter SQL query ")
        print("\nRelational Algebra Expression")
        RAstr=sqlparser.sqlparse(SQL)
        print("\n\n Relational Algebra Tree")
        treeRA.ratree(RAstr)
        loop=False
    elif choice=='2':
        loop=False


