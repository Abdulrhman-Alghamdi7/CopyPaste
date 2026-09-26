from flask import Flask, request

app:Flask = Flask(__name__)


class User:
    usernames:set[str] = set()
    def __init__(self,username:str,password:str) -> None:
        if username not in User.usernames: 
            self._username:str = username
            User.usernames.add(username)
        else: raise Exception("Username already exist!")
        self._password:str = password
        self._clipboard:str = ""
        self._clipID:int = 0

    def set_clipboard(self, password:str, txt:str):
        if self._password == password:
            self._clipboard = txt
            self._clipID += 1
        else:raise Exception("Wrong password!")

    def get_clipboard(self, password:str):
        if self._password == password:
            return self._clipboard
        else:raise Exception("Wrong password!")

    def get_clipID(self, password:str) -> int: 
        if self._password == password: return self._clipID
        else:raise Exception("Wrong password!")


users:dict[str,User] = dict()


# Registers a new user.
@app.post("/register") #type: ignore
def register():
    try:
        data = request.form
        username = data.get("username")
        password = data.get("password")

        if username: username = username.strip()
        else:raise Exception("Empty username!")

        if password: password = password.strip()
        else:raise Exception("Empty password!")

        new_user = User(username, password)
        users[username] = new_user

        print(f"User '{username}' registered successfully.")

    except Exception as e:
        print(f"Registration error: {str(e)}")
        return {"status" : f"Error: {str(e)}"}

    return {"status" : "success"}


@app.post("/set_clipboard") #type: ignore
def set_clipboard():
    try:
        data = request.form
        username = data.get("username")
        password = data.get("password")
        clipboard = data.get("clipboard")

        if not clipboard: raise Exception("Empty clipboard!")

        if username: username = username.strip()
        else:raise Exception("Empty username!")

        if password: password = password.strip()
        else:raise Exception("Empty password!")

        if username in users:
            users[username].set_clipboard(password, clipboard)
            print(f"Clipboard updated by user '{username}'.")
        else:raise Exception("User doesn't exist!")

    except Exception as e:
        print(f"Clipboard update error: {str(e)}")
        return {"status" : f"Error: {str(e)}"}

    return {"status" : "success", "clipid":str(users[username].get_clipID(password))}


@app.post("/get_clipboard") #type: ignore
def get_clipboard():
    try:
        data = request.form
        username = data.get("username")
        password = data.get("password")

        if username: username = username.strip()
        else:raise Exception("Empty username!")

        if password: password = password.strip()
        else:raise Exception("Empty password!")

        if username in users:
            print(f"Clipboard requested by user '{username}'.")
            return {
                "status" : "success",
                "clipboard":users[username].get_clipboard(password),
                "clipid":str(users[username].get_clipID(password))
            }
        else:raise Exception("User doesn't exist!")
        
    except Exception as e:
        print(f"Clipboard request error: {str(e)}")
        return {"status" : f"Error: {str(e)}"}


@app.post("/check_clipboard") #type: ignore
def check_clipboard():
    try:
        data = request.form
        username = data.get("username")
        password = data.get("password")
        last_received = data.get("last_received")

        if last_received:last_received = int(last_received)
        else:raise Exception("Last received clipboard ID was expected!")

        if username: username = username.strip()
        else:raise Exception("Empty username!")

        if password: password = password.strip()
        else:raise Exception("Empty password!")

        if username in users:
            print(f"Clipboard checked by user '{username}'.")
            return {
                "status" : "success",
                "new":"True" if last_received < users[username].get_clipID(password) else "False"
            }
        else:raise Exception("User doesn't exist!")

    except Exception as e:
        print(f"Clipboard check error: {str(e)}")
        return {"status" : f"Error: {str(e)}"}

if __name__ == "__main__":
    print("""This is a simple clipboard synchronization server app.
Copyright (C) 2026  Abdulrhman Alghamdi

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.
""")
    app.run()