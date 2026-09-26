import requests
import pyperclip


last_received: int = 0
username: str
password: str
server_url: str
last_local_clipboard: str = pyperclip.paste()


def init():
    global last_received, username, password, server_url, last_local_clipboard

    print("=" * 50)
    print("        Clipboard Sync Client")
    print("=" * 50)

    registered = input("Are you registered? [y or n]: ").strip().lower()
    while registered != "y" and registered != "n":
        registered = input('Enter either "y" or "n" only: ').strip().lower()

    registered = registered == "y"

    username = input("Enter username: ").strip()
    password = input("Enter password: ").strip()
    server_url = input("Enter server's URL: ").strip().rstrip("/")

    print(f"\nConnecting to: {server_url}")
    print(f"Username: {username}")

    if not registered:
        print("Registering account...")

        response = requests.post(server_url + "/register",data={"username": username, "password": password})
        response.raise_for_status()

        status = response.json().get("status")

        if status and "Error" in status:
            raise Exception(status)

        print(f"Registration: {status}")
    else:
        print("Using existing account.")

    print("Initialization complete.")
    print("Waiting for clipboard changes...")
    print("-" * 50)


def get_clipboard():
    global last_received, username, password, server_url, last_local_clipboard

    check_response = requests.post(
        server_url + "/check_clipboard",
        data={"username": username, "password": password, "last_received": str(last_received)})
    check_response.raise_for_status()

    check_data = check_response.json()
    status = check_data.get("status")

    if status and "Error" in status:
        raise Exception(status)

    new = check_data.get("new")

    if new == "True":
        print("Remote clipboard change detected.")

        get_response = requests.post(
            server_url + "/get_clipboard",
            data={"username": username, "password": password})
        get_response.raise_for_status()

        get_data = get_response.json()
        status = get_data.get("status")

        if status and "Error" in status:
            raise Exception(status)

        clipboard = get_data.get("clipboard")
        clipid = int(get_data.get("clipid"))

        pyperclip.copy(clipboard)

        last_received = clipid
        last_local_clipboard = clipboard

        print(f"Clipboard updated from server. Clip ID: {clipid}")


def set_clipboard():
    global last_received, username, password, server_url, last_local_clipboard

    current_clipboard = pyperclip.paste()

    if last_local_clipboard != current_clipboard:
        print("Local clipboard change detected.")
        print("Uploading clipboard to server...")

        set_response = requests.post(
            server_url + "/set_clipboard",
            data={"username": username, "password": password, "clipboard": current_clipboard})
        set_response.raise_for_status()

        set_data = set_response.json()
        status = set_data.get("status")

        if status and "Error" in status:
            raise Exception(status)

        clipid = int(set_data.get("clipid"))

        last_received = clipid
        last_local_clipboard = current_clipboard

        print(f"Clipboard uploaded successfully. Clip ID: {clipid}")


def main():
    try:
        init()

        while True:
            try:
                get_clipboard()
                set_clipboard()

            except requests.exceptions.ConnectionError:
                print("Connection error: could not reach the clipboard server.")

            except requests.exceptions.Timeout:
                print("Request timed out while contacting the server.")

            except requests.exceptions.HTTPError as e:
                print(f"HTTP error from server: {e}")

            except Exception as e:
                print(f"Sync error: {e}")

    except KeyboardInterrupt:
        print("\nClipboard sync stopped by user.")

    except Exception as e:
        print(f"Startup error: {e}")


if __name__ == "__main__":
    print("""This is a simple clipboard synchronization client app.
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
    main()