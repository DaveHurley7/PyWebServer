from pywebserver import redirect
from pywebserver import make_query
#from db import create_table, PK


def post(params):
    products = [{"name":"Bread","cost":1.20},{"name":"Water Bottle","cost":1.70},{"name":"Twirl","cost":1.40}]
    data = {"params":params,"products":products}
    #make_query("CREATE TABLE users(id int primary key, username varchar(30), password varchar(30));")
    make_query("CREATE TABLE songs (song_id int primary key, name varchar(30), artist varchar(30), length int);")
    #create_table("songs",("song_id","int",PK),("name","varchar",30),("artist","varchar",30),("length","int"))
    return redirect("home",data)