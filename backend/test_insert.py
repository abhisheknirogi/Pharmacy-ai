import sqlite3

conn = sqlite3.connect("pharmacy.db")
cursor = conn.cursor()

cursor.execute("""
INSERT INTO inventory (medicine_name, batch_no, quantity, expiry_date, distributor)
VALUES ('Crocin', 'BATCH001', 100, '2027-01-01', 'Sun Pharma')
""")

conn.commit()

cursor.execute("SELECT * FROM inventory")
print(cursor.fetchall())
