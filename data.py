import sqlite3
conn=sqlite3.connect('database.db')

conn.execute('''CREATE TABLE IF NOT EXISTS admin
             (id INTEGER PRIMARY KEY AUTOINCREMENT,
             username TEXT NOT NULL UNIQUE,
             password TEXT NOT NULL)
             ''')

conn.execute('''CREATE TABLE IF NOT EXISTS users
             (id INTEGER PRIMARY KEY AUTOINCREMENT,
             username TEXT NOT NULL UNIQUE,
             password TEXT NOT NULL)
             ''')

conn.execute('''CREATE TABLE IF NOT EXISTS vehicles
             (id INTEGER PRIMARY KEY AUTOINCREMENT,
             user_id INTEGER NOT NULL,
             vehicle_number TEXT NOT NULL UNIQUE,
             FOREIGN KEY (user_id) REFERENCES users(id))
             ''')

conn.execute(''' CREATE TABLE IF NOT EXISTS parking_lot 
             (id INTEGER PRIMARY KEY AUTOINCREMENT,
             name TEXT NOT NULL,
             address TEXT NOT NULL,
             pincode TEXT NOT NULL ,
             total_spots INTEGER NOT NULL,
             price_per_hour REAL NOT NULL)
             ''')

conn.execute('''CREATE TABLE IF NOT EXISTS parking_spot
             (id INTEGER PRIMARY KEY AUTOINCREMENT,
             lot_id INTEGER NOT NULL,
             spot_number INTEGER NOT NULL,
             is_occupied BOOLEAN NOT NULL DEFAULT 0,
             FOREIGN KEY (lot_id) REFERENCES parking_lot(id))
             ''')

conn.execute('''CREATE TABLE IF NOT EXISTS reservations
             (id INTEGER PRIMARY KEY AUTOINCREMENT,
             user_id INTEGER NOT NULL,
             spot_id INTEGER NOT NULL,
             vehicle_id INTEGER NOT NULL,
             parking_timestamp TEXT NOT NULL,
             leaving_timestamp TEXT NOT NULL,
             total_cost REAL NOT NULL,
             FOREIGN KEY (user_id) REFERENCES users(id),
             FOREIGN KEY (spot_id) REFERENCES parking_spot(id)
             FOREIGN KEY (vehicle_id) REFERENCES vehicles(id))
             ''')

conn.commit()
