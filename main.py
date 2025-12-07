from flask import Flask ,render_template ,request ,session, redirect, url_for  
from flask_socketio import join_room , leave_room ,send, SocketIO
import random
from string import ascii_uppercase 

RED = '\033[91m'
GREEN = '\033[92m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
ENDC = '\033[0m'
rooms = {}
def generateCode (number):
    while True:
        code = ""
        for _ in range(number):
            code += random.choice(ascii_uppercase)
          
        if code not in rooms :
             return code
            
      
        
print(generateCode(8))
print(BLUE+"THIS IS THE DATABASE"+ENDC,rooms)

print(ascii_uppercase.capitalize())
app = Flask(__name__)
app.config["SECRET_KEY"] = "JEUEIGGEIGY"
socketio = SocketIO(app,async_mode='eventlet')
@app.route("/",methods=["GET", "POST"])
def home():
    session.clear()
    if request.method == "POST":
        name = request.form.get("name")
        code = request.form.get("code")
        join = request.form.get("join",False)
        create = request.form.get("create",False)
        
        if not name:
            return render_template("home.html",error = "please pass in a name ",code =code, name=name)
        if join !=  False and not code :
            return render_template("home.html",error = "please enter a room code",code =code, name=name)
        if create != False:
            room = generateCode(5)
            rooms[room] = {
                "members":0,
                
                "messages":[]
            }
          
           
            session["room"] = room 
            session["name"] = name 
            return redirect(url_for("room"))
        elif code not in rooms :
            return render_template("home.html",error = "the room dosnt exist",code =code,name =name)
        elif code  in rooms and name != None :
             session["room"] = code 
             session["name"] = name 
             return redirect(url_for("room"))

         
    return render_template("home.html")

@app.route("/room")
def room():
  room = session.get("room")
  name = session.get("name")
  print(room)
#   if not room or session.get("name") is None or room not in rooms :
#       print("thos is the room ",room,"and this the user " ,session.get("name"),)
#       return redirect(url_for("home"))
  print("na this ne the name 0000000000000000000000000000000000000000000",name)
  return render_template("room.html", room=room,name= name)

@socketio.on("connect")
def connect(auth):
     room = session.get("room")
     name = session.get("name")
     print(f"{room} ,{name}")
     print(RED+f" this is the rooms {rooms}"+ENDC)
     if not room or not name:
         return 
     if room not in rooms:
         leave_room(room)
         return 
     join_room(room)
     send({
         "name":name,"message":"joined the group","from":"system"
     } ,to = room)
     for content in rooms[room]["messages"]:
         send( content,to=room)
     print(f" {name} joined this {room} room")
     rooms[room]["members"] +=1

@socketio.on("disconnect")
def disconnect ():
     room = session.get("room")
     name = session.get("name")
  
    
     leave_room(room)
     if room in rooms:
         rooms[room]["members"] -=1
     
     send({
         "name":name,"message":"left the group","from":"system"
     }, to = room)

     print("//////////////////////////////////////////////////////////////////////////////////////////////////////////")
     print(f"{name} just left")
@socketio.on("message")
def message(data):
    room = session.get("room")
    name = session.get("name")
    
    if room not in rooms :
      return 
    contentData = {
        "name":name,
        "message":data["data"]
    }
    rooms[room]["messages"].append(contentData)
    print(rooms[room])
  
    send( contentData,to=room)



if __name__ == "__main__":
    socketio.run(app,debug=True)