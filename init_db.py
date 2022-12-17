from app import db, Rooms, Temperatures, app


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
