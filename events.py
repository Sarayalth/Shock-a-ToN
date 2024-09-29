import main
import settings

def check_event(event):
    shockers = settings.config.get("shockers", [])
    
    valid_shockers = [shocker for shocker in shockers if event in shocker.get("events", [])]

    if valid_shockers:
        match event:
            case "death" | "death_end_round":
                main.trigger_shock(valid_shockers)
            case "dtm":
                main.trigger_shock(valid_shockers, duration=5000, shock_type="Shock")
            case "respawn":
                main.trigger_shock(valid_shockers, duration=5000, shock_type="Shock")

def death_event(round_ended=False):
    if main.round_type == "Bloodbath":
        if main.round_terrors and any(terror == "50" for terror in main.round_terrors):
            print("you seriously died to the button? smh.")
            check_event("dtm")
    elif main.round_type == "Midnight":
        if (len(main.round_terrors) > 2 and ("50" in main.round_terrors[:2])) or (len(main.round_terrors) > 2 and main.round_terrors[2] == "21"):
            print("you seriously died to the button? smh.")
            check_event("dtm")
    elif main.round_type == "Alternate":
        if main.round_terrors and any(terror == "21" for terror in main.round_terrors):
            print("you seriously died to the button? smh.")
            check_event("dtm")
    elif main.round_terrors and main.round_terrors[0] == "50":
        print("you seriously died to the button? smh.")
        check_event("dtm")
    else:
        print("you died? awww, too bad~")
        check_event("death" if not round_ended else "death_end_round")