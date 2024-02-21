import MySQLdb

# 連線參數
host = "localhost"
user = "root"
password = "mysql123"
database = "plants"

plants = ['Ageratum houstonianum', 'Amaranthus spinosus', 'Bidens pilosa var radiata', 'Celosia argentea',\
'Chloris barbata', 'Crassocephalum crepidioides', 'Eleusine indica', 'Lantana camara', 'Leucaena leucocephala',\
'Mikania micrantha', 'Miscanthus species', 'Pennisetum purpureum', 'Syngonium podophyllum', 'Tithonia diversifolia']


# Establish a connection
connection = MySQLdb.connect(host=host, user=user, password=password, database=database)

# Create a cursor
cursor = connection.cursor()

# SQL query with placeholders
sql_query = "INSERT INTO plants_plant (imgurl, scientific_name, isinvasive, description, datetime) VALUES"

# 構建查詢
for plant in plants:
    # 判斷植物是否為入侵種
    isinvasive = True if plant not in ("Amaranthus spinosus", "Celosia argentea", \
                                       "Miscanthus species", "Eleusine indica") else False
    sql_query += f"('/media/{plant}.jpg', '{plant}', {isinvasive}, 'no-data', NOW())," # 拼接SQL語句
sql_query = sql_query[:-1] 
sql_query += ";"
print(sql_query)
# Execute the query
cursor.execute(sql_query)

# Commit the changes
connection.commit()

# Close the cursor and connection
cursor.close()
connection.close()
