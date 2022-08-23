# Serverless database
import sqlite3

# Establish connection to the database
state_finder_connection = sqlite3.connect("state_finder.db")
# Whenever we execute a command it is going to be on the
# state finder cursor object
state_finder_cursor = state_finder_connection.cursor()
state_finder_cursor.execute("create table ebt (state_name string, no_of_households integer)")
# List of data we are going to insert
nutrition_assistance_list = [
    ("Montana", 45445),
    ("Nebraska", 74860),
    ("Nevada", 242928),
    ("New Hampshire", 36433),
    ("New Jersey", 436078)
]
state_finder_cursor.executemany("insert into ebt values (?,?)", nutrition_assistance_list)
# Print State Finder Database Rows
for row in state_finder_cursor.execute("select * from ebt"):
    print(row)
# Terminating connection to the database
state_finder_connection.close()