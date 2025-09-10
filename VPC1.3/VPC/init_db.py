import sqlite3

def init_db():
    conn = sqlite3.connect('vpc_simulator.db')  # This will create the new database
    c = conn.cursor()

    # Create the users table
    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            password TEXT NOT NULL
        )
    ''')

    # Create the VPCs table
    c.execute('''
        CREATE TABLE IF NOT EXISTS vpcs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            vpc_name TEXT NOT NULL,
            cidr_block TEXT NOT NULL,
            user_id INTEGER,
            FOREIGN KEY(user_id) REFERENCES users(id)
        )
    ''')

    # Create the Subnets table
    c.execute('''
        CREATE TABLE IF NOT EXISTS subnets (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            subnet_name TEXT NOT NULL,
            subnet_cidr TEXT NOT NULL,
            vpc_name TEXT NOT NULL,
            vpc_id INTEGER,
            user_id INTEGER,
            FOREIGN KEY(vpc_id) REFERENCES vpcs(id),
            FOREIGN KEY(user_id) REFERENCES users(id)
        )
    ''')

    conn.commit()
    conn.close()

if __name__ == '__main__':
    init_db()
    print("Database created successfully!")
