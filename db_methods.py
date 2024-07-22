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
    con.commit()
    cur.execute("DROP TABLE if exists guilds")
    cur.execute("""CREATE TABLE guilds(
            gid integer primary key, 
            pid integer, 
            region text,
            player text
            ) """)
    con.commit()
    
def get_riot_id(userid):
    cur.execute("")

def logDB():
    print("Players")
    res = cur.execute("SELECT * from players")
    print(res.fetchall())
    print("Guilds")
    res = cur.execute("SELECT * from guilds")
    print(res.fetchall())

if __name__ == "__main__":
    logDB()
    # db_init()