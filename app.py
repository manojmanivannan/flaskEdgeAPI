from datetime import datetime
from flask import Flask, request
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql import func
from os.path import join, abspath, dirname
from init_db import create_table_and_load_data


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


    def __repr__(self) -> str:
        return f"<Temperatures {self.room_id} {self.temperature}>"


create_table_and_load_data(app, db, Rooms, Temperatures)


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