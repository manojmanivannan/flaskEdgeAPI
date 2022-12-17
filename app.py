from datetime import datetime, timezone
from flask import Flask, request
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql import func
from os.path import isfile, join, abspath, dirname



# CREATE_ROOMS_TABLE = ("CREATE TABLE IF NOT EXISTS rooms (id SERIAL PRIMARY KEY, name TEXT);")
# CREATE_TEMPS_TABLE = """CREATE TABLE IF NOT EXISTS temperatures (room_id INTEGER, temperature REAL, date TIMESTAMP, FOREIGN KEY(room_id) REFERENCES rooms(id) ON DELETE CASCADE);"""

# INSERT_ROOM_RETURN_ID = "INSERT INTO rooms (name) VALUES (%s) RETURNING id;"
# INSERT_TEMP = ("INSERT INTO temperatures (room_id, temperature, date) VALUES (%s, %s, %s);")

# ROOM_NAME = """SELECT name FROM rooms WHERE id = (%s)"""
# ROOM_NUMBER_OF_DAYS = """SELECT COUNT(DISTINCT DATE(date)) AS days FROM temperatures WHERE room_id = (%s);"""
# ROOM_ALL_TIME_AVG = ("SELECT AVG(temperature) as average FROM temperatures WHERE room_id = (%s);")

# ROOM_TERM = """SELECT DATE(temperatures.date) as reading_date,
# AVG(temperatures.temperature)
# FROM temperatures
# WHERE temperatures.room_id = (%s)
# GROUP BY reading_date
# HAVING DATE(temperatures.date) > (SELECT MAX(DATE(temperatures.date))-(%s) FROM temperatures);"""

# GLOBAL_NUMBER_OF_DAYS = ("""SELECT COUNT(DISTINCT DATE(date)) AS days FROM temperatures;""")
# GLOBAL_AVG = """SELECT AVG(temperature) as average FROM temperatures;"""

basedir = abspath(dirname(__file__))

app = Flask(__name__)
##### INITIALIZE DB ##########
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + join(basedir,"edgeapi.db")
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

USER_ID_SEQ = db.Sequence('room_id_seq')  # define sequence explicitly
class Rooms(db.Model):
    # Inherit the db.Model to this class.

    id = db.Column(db.Integer,primary_key=True)
    room_name = db.Column(db.String(200),nullable=False, unique=True)
    date = db.Column(db.DateTime, default=datetime.utcnow)
    room_id = db.relationship('Temperatures', backref='rooms')

    def __repr__(self):
        return f"<Rooms {self.room_name}>"

    def as_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}

class Temperatures(db.Model):

    id = db.Column(db.Integer,primary_key=True)
    date = db.Column(db.DateTime, default=datetime.utcnow)
    temperature = db.Column(db.Float, nullable=False)
    room_id = db.Column(db.Integer,db.ForeignKey('rooms.id'), nullable=False)
    # room = db.relationship('Rooms', backref='temperatures')
    # room = db.relationship('Temperature',backref=db.backref("room", uselist=False))


    def __repr__(self) -> str:
        return f"<Temperatures {self.room_id} {self.temperature}>"


with app.app_context():
    db.drop_all()
    db.create_all()
    room1 = Rooms(room_name="hall")
    room2 = Rooms(room_name="kitchen")
    room3 = Rooms(room_name="pooja")
    room4 = Rooms(room_name="bathroom")

    temp1 = Temperatures(rooms=room1, temperature=17.1)
    temp2 = Temperatures(rooms=room1, temperature=10.3)
    temp3 = Temperatures(rooms=room2, temperature=20.5)
    temp4 = Temperatures(rooms=room3, temperature=80.3)
    temp5 = Temperatures(rooms=room4, temperature=33.8)

    db.session.add_all([room1, room2,room3,room4])
    db.session.add_all([temp1, temp2, temp3, temp4, temp5])
    db.session.commit()





@app.get("/")
def index():
    return {"data":"Hello World !"}

@app.route("/room/create/<string:name>", methods=['POST'])
def add_room(name):

    if request.method == "POST":
        new_room = Rooms(room_name=name)

        try:
            db.session.add(new_room)
            db.session.commit()
            return {"message":"Room added"}
        except Exception as e:
            return {"message":f"Room add failed {e}"}
    else:
        return {"message":"Does not support GET"}

@app.route("/temperature/<string:room_id>/<float:temp>", methods=['POST'])
def add_temp(room_id,temp):
    if request.method == "POST":
        new_temp = Temperatures(room_id=room_id,temperature=float(temp))

        try:
            db.session.add(new_temp)
            db.session.commit()
            return {"message":"Temperature added"}
        except Exception as e:
            return {"message":f"Temperature add failed {e}"}
    else:
        return {"message":"Does not support GET"}

@app.route("/rooms", methods=['GET'])
def get_rooms():
    if request.method == "GET":
        rooms = Rooms.query.order_by(Rooms.date).all()
        room_dict={}
        for room in rooms:
            room_dict[room.id] = room.room_name
        return room_dict

@app.route("/temperatures", methods=['GET'])
def get_temperatures():
    if request.method == "GET":
        temps = Temperatures.query.order_by(Temperatures.date).all()
        temp_dict={}
        for temp in temps:
            temp_dict[temp.id] = {
                'id':temp.id,
                'temperature': temp.temperature,
                'date':temp.date
            } 
        return temp_dict

@app.route("/avgtemp/<int:room_id>", methods=['GET'])
def get_avg_temp_by_room_id(room_id):
    if request.method == "GET":
        temps1 = Temperatures.query\
                        .with_entities(
                            Rooms.room_name,
                            func.avg(Temperatures.temperature).label('avg')
                        )\
                        .join(Rooms, Temperatures.room_id == Rooms.id)\
                        .filter(Temperatures.room_id==room_id).all()
        result = {
            "room_id":room_id,
            "data":{temps1[0][0]:temps1[0][1]}
        }
        return result


if __name__ == '__main__':
    
    app.run()