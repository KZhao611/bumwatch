import sqlite3

con = sqlite3.connect("database.db")
cur = con.cursor()

def db_init():
    cur.execute("DROP TABLE if exists players")
    cur.execute("""CREATE TABLE players(
            discord integer primary key, 
            username text not null,
            riot text not null,
            region text not null
            ) """)
    
def get_riot_id(userid):
    cur.execute("")


if __name__ == "__main__":
    db_init()