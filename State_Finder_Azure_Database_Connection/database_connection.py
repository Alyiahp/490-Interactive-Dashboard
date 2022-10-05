import pyodbc

# Link to download ODBC Driver 18
# https://docs.microsoft.com/en-us/sql/connect/odbc/download-odbc-driver-for-sql-server?view=sql-server-ver15

server = 'statefinder.database.windows.net'
database = 'LivingWage'
username = 'statefinder'
password = 'FAll2022'
driver='{ODBC Driver 18 for SQL Server}'

conn = pyodbc.connect('DRIVER='+driver+';SERVER=tcp:'+server+';PORT=1433;DATABASE='+database+';UID='+username+';PWD='+password)
cursor = conn.cursor()
for row in cursor.execute("SELECT three_kids_year FROM One_Adult"):
    print(row)
conn.close()