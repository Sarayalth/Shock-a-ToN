import os
import glob
import sys
import time
import requests
import events
import settings
from pythonosc.udp_client import SimpleUDPClient

round_type = ""
first_run = True
round_types = [
    'Classic', 'Fog', 'Punished', 'Sabotage', 'Cracked', 'Alternate',
    'Bloodbath', 'Midnight', 'Mystic Moon', 'Twilight', 'Solstice', 'Blood Moon'
]
round_terrors = []

def find_latest_log(directory):
    log_files = glob.glob(os.path.join(directory, "*.txt"))
    if not log_files:
        print("No log files found.")
        return None
    
    latest_log = max(log_files, key=os.path.getmtime)
    print(f"Current VRChat Log: {latest_log}\nRunning! ToN data should appear below!\n===================")
    return latest_log

def get_user_input(prompt):
    while True:
        user_input = input(prompt).strip()
        return user_input

def send_message(text):
    osc_client.send_message("/chatbox/input", [text, True, False])

def trigger_shock(shockers, intensity=None, duration=None, shock_type=None):
    url = f"{settings.config.get("api_url")}/2/shockers/control"
    headers = {
        "accept": "application/json",
        "Content-Type": "application/json",
        "OpenShockToken": settings.config.get("api_key")
    }

    data = {
        "shocks": [
            {
                "id": shocker.get("id"),
                "type": shock_type if shock_type is not None else shocker.get("type"),
                "intensity": intensity if intensity is not None else shocker.get("intensity"),
                "duration": duration if duration is not None else shocker.get("duration"),
                "exclusive": True
            } for shocker in shockers
        ],
        "customName": "Shock-a-ToN"
    }

    response = requests.post(url=url, headers=headers, json=data)

    if response.status_code == 200:
        print("zap zap~")
        #send_message("zap zap~")
    else:
        print(f"failed {shock_type.lower()}. api response:\n {response.content}")

def monitor_rounds(log_file):
    global first_run
    global round_type
    global round_terrors
    last_position = 0

    while True:
        with open(log_file, "r", encoding="utf-8") as file:
            file.seek(last_position)
            lines = file.readlines()
            new_position = file.tell()

            if not first_run:
                for line in lines:
                    # zap zap when dying
                    if "Died in round." in line:
                        events.death_event(round_ended=True)

                    # zap zap when dead on round end
                    elif "You died." in line:
                        events.death_event(round_ended=False)

                    elif "Player respawned, opted out!" in line:
                        print("bad! no respawning!")
                        events.check_event("respawn")

                    # check and save the spawning terrors
                    elif "Killers have been set" in line:
                            parts = line.split("Killers have been set")
                            if len(parts) > 1:
                                round_type = parts[1].strip().split()[-1]
                                if round_type in round_types:
                                    terror1 = parts[1].strip().split()[1]
                                    terror2 = parts[1].strip().split()[2]
                                    terror3 = parts[1].strip().split()[3]
                                    round_terrors = []
                                    round_terrors.append(terror1)
                                    round_terrors.append(terror2)
                                    round_terrors.append(terror3)
                                    match round_type:
                                        case "Bloodbath":
                                            round_terrors.append(terror1)
                                            round_terrors.append(terror2)
                                            round_terrors.append(terror3)
                                        case "Midnight":
                                            round_terrors.append(terror1)
                                            round_terrors.append(terror2)
                                            round_terrors.append(terror3)
                                        case _:
                                            round_terrors.append(terror1)

                    #elif "Round type is Sabotage" in line:
                        # TODO fuck you up if you die

            last_position = new_position

        first_run = False
        time.sleep(1)

if __name__ == "__main__":
    settings.load_config()

    if settings.config is None or not settings.config.get("api_key") or not settings.config.get("shockers"):
        shockers = []
        print("This uses the OpenShock API to control your (or someone else's :3c) shockers, for this it needs access to an OpenShock API token and the shockers id.\n")
        print("To get your OpenShock API token, go to openshock.app, open the API tokens menu, "
              "click the green + icon on the bottom right, write a name for the token, and copy the code.")

        api_key = get_user_input("Enter your API token: ")

        print("\nHow many shockers are you gonna use?")

        shocker_number = int(get_user_input("Enter the number of shockers: "))

        if (shocker_number > 10):
            print("Not happening.")
            sys.exit(1)

        print("\nTo get your shocker id, go to openshock.app, open the shockers menu, "
            "click the three vertical dots next to your shocker, select 'edit', and copy the id.")

        for shock_number in range(shocker_number) :
            shocker = {}
            shocker["id"] = get_user_input("Enter your shocker id: ")

            shocker["type"] = get_user_input("Enter the type of 'shock' you want (Vibrate, Shock): ").capitalize()
            if shocker["type"] not in ["Vibrate", "Shock"]:
                print("Invalid input. Please enter either 'Vibrate' or 'Shock'.")
                sys.exit(1)

            shocker["intensity"] = get_user_input("Enter the intensity, from 1 to 100: ")
            try:
                shocker["intensity"] = int(shocker["intensity"])

                if shocker["intensity"] < 1 or shocker["intensity"] > 100:
                    print("Invalid input. Please enter a value between 1 and 100.")
                    sys.exit(1)
            except ValueError:
                print("Invalid input. Please enter a numeric value between 1 and 100.")
                sys.exit(1)

            shocker["duration"] = get_user_input("Enter the duration in miliseconds: ")

            # default events
            shocker["events"] = ["death", "dtm", "respawn"]

            shockers.append(shocker)
            print("New shocker added.\n")

        config = {
            "api_url": "https://api.openshock.app", # default api instance
            "api_key": api_key,
            "shockers": shockers
        }

        settings.save_config(config)

    # directory and file search
    user_dir = os.getlogin()
    log_directory = f"C:\\Users\\{user_dir}\\AppData\\LocalLow\\VRChat\\VRChat"
    latest_log_file = find_latest_log(log_directory)

    if latest_log_file:
        # OSC setup
        ip = "127.0.0.1"
        port = 9000
        osc_client = SimpleUDPClient(ip, port)

        # start the show~
        monitor_rounds(latest_log_file)