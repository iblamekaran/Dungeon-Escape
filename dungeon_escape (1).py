"""
╔══════════════════════════════════════════════════════╗
║         ⚔️   DUNGEON ESCAPE  —  A PYTHON RPG   ⚔️      ║
║                                                      ║
║  Concepts: strings, lists, dicts, tuples, sets,      ║
║  loops, conditionals, functions, recursion,          ║
║  exception handling, file I/O (save/load), OOP-lite  ║
╚══════════════════════════════════════════════════════╝
"""

import random
import os
import json
import time

# ══════════════════════════════════════════
#  CONSTANTS  (tuples — immutable)
# ══════════════════════════════════════════

ROOM_TYPES   = ("empty", "monster", "treasure", "trap", "shop", "boss")
DIRECTIONS   = ("north", "south", "east", "west")
DIR_SYMBOLS  = {"north": "↑", "south": "↓", "east": "→", "west": "←"}
SAVE_FILE    = "dungeon_save.json"

MONSTERS = [
    {"name": "Goblin",    "hp": 15, "atk": 4,  "xp": 10, "gold": 5 },
    {"name": "Skeleton",  "hp": 20, "atk": 6,  "xp": 15, "gold": 8 },
    {"name": "Troll",     "hp": 35, "atk": 9,  "xp": 25, "gold": 15},
    {"name": "Vampire",   "hp": 28, "atk": 11, "xp": 30, "gold": 20},
    {"name": "Dragon",    "hp": 60, "atk": 18, "xp": 80, "gold": 50},  # boss
]

ITEMS = {
    "Health Potion":  {"type": "heal",   "value": 25, "price": 10},
    "Iron Sword":     {"type": "weapon", "value": 5,  "price": 15},
    "Steel Sword":    {"type": "weapon", "value": 10, "price": 30},
    "Fire Staff":     {"type": "weapon", "value": 15, "price": 50},
    "Shield":         {"type": "armor",  "value": 4,  "price": 20},
    "Magic Amulet":   {"type": "armor",  "value": 7,  "price": 40},
}

TRAPS = [
    {"name": "Spike Pit",    "dmg": 10, "msg": "You fall into a spike pit!"},
    {"name": "Poison Dart",  "dmg": 8,  "msg": "A dart hits you — poison!"},
    {"name": "Fire Glyph",   "dmg": 15, "msg": "A fire glyph explodes!"},
]

TREASURES = [
    {"gold": 20, "msg": "💰 You find a small chest of gold!"},
    {"gold": 40, "msg": "💎 A sparkling gem — worth 40 gold!"},
    {"gold": 10, "msg": "🪙  A few loose coins on the floor."},
]

# ══════════════════════════════════════════
#  HELPER FUNCTIONS
# ══════════════════════════════════════════

def clear():
    os.system("cls" if os.name == "nt" else "clear")

def pause(msg="  [Press ENTER to continue]"):
    input(msg)

def bar(current, maximum, length=20, fill="█", empty="░"):
    """Draws a text progress bar."""
    filled = int(length * current / max(maximum, 1))
    return fill * filled + empty * (length - filled)

def sluggish_print(text, delay=0.018):
    """Prints text character by character for dramatic effect."""
    for ch in text:
        print(ch, end="", flush=True)
        time.sleep(delay)
    print()

def pick(lst):
    """Returns a random element from a list (shallow copy safe)."""
    return random.choice(lst)

def separator(char="─", n=52):
    print(char * n)

def header(title, icon="⚔️"):
    separator("═")
    print(f"  {icon}  {title}")
    separator("═")

def get_choice(prompt, valid_options):
    """
    Loops until the user enters a valid choice.
    Demonstrates: while loop + conditionals + sets
    """
    valid_set = set(str(o).lower() for o in valid_options)
    while True:
        raw = input(prompt).strip().lower()
        if raw in valid_set:
            return raw
        print(f"  ❌ Invalid — choose from: {', '.join(sorted(valid_set))}")

def get_int(prompt, lo, hi):
    """Safe integer input within a range."""
    while True:
        try:
            v = int(input(prompt))
            if lo <= v <= hi:
                return v
            print(f"  ⚠️  Enter a number between {lo} and {hi}.")
        except ValueError:
            print("  ❌ Numbers only!")

# ══════════════════════════════════════════
#  PLAYER  (dict — basic Python data struct)
# ══════════════════════════════════════════

def create_player(name):
    """
    Returns a dictionary representing the player.
    Demonstrates: dicts, lists
    """
    return {
        "name":      name,
        "hp":        100,
        "max_hp":    100,
        "atk":       8,
        "defense":   2,
        "gold":      15,
        "xp":        0,
        "level":     1,
        "xp_needed": 30,
        "inventory": [],        # list
        "visited":   set(),     # set of room coords already seen
        "floor":     1,
        "pos":       (0, 0),    # tuple
        "escaped":   False,
    }

def show_status(player):
    """Prints the player's current stats."""
    hp     = player["hp"]
    max_hp = player["max_hp"]
    separator()
    print(f"  👤 {player['name']}   Level {player['level']}   Floor {player['floor']}")
    print(f"  ❤️  HP  [{bar(hp, max_hp)}] {hp}/{max_hp}")
    print(f"  ⚔️  ATK {player['atk']}   🛡️  DEF {player['defense']}   "
          f"💰 Gold {player['gold']}   ✨ XP {player['xp']}/{player['xp_needed']}")
    inv_str = ", ".join(player["inventory"]) if player["inventory"] else "empty"
    print(f"  🎒 Inventory: {inv_str}")
    separator()

# ══════════════════════════════════════════
#  DUNGEON MAP  (dict of dicts)
# ══════════════════════════════════════════

def generate_floor(floor_num):
    """
    Generates a random 5×5 dungeon floor.
    Concepts: nested dicts, loops, conditionals, tuples as keys
    """
    dungeon = {}
    size = 5
    exit_pos = (random.randint(2, 4), random.randint(2, 4))

    for row in range(size):
        for col in range(size):
            pos = (row, col)

            # Starting room is always empty
            if pos == (0, 0):
                room_type = "empty"
            elif pos == exit_pos:
                room_type = "boss" if floor_num % 3 == 0 else "exit"
            else:
                # Weighted random room type
                roll = random.random()
                if roll < 0.30:
                    room_type = "monster"
                elif roll < 0.50:
                    room_type = "empty"
                elif roll < 0.65:
                    room_type = "treasure"
                elif roll < 0.80:
                    room_type = "trap"
                elif roll < 0.90:
                    room_type = "shop"
                else:
                    room_type = "monster"

            dungeon[pos] = {
                "type":    room_type,
                "visited": False,
                "desc":    room_description(room_type),
            }

    return dungeon, exit_pos, size

def room_description(room_type):
    """Returns a flavour description for a room type."""
    descs = {
        "empty":   pick(["A dusty corridor. Nothing stirs.",
                         "Cobwebs hang from the ceiling.",
                         "The torches flicker. All is quiet."]),
        "monster": pick(["You hear a growl ahead...",
                         "Eyes glint in the darkness.",
                         "The stench of a beast fills the air."]),
        "treasure": pick(["A glimmer catches your eye.",
                          "Something shiny lies in the corner.",
                          "The smell of old coins fills the room."]),
        "trap":    pick(["The floor looks unstable...",
                         "Strange markings cover the walls.",
                         "A faint hissing sound..."]),
        "shop":    "A cloaked merchant waves at you.",
        "boss":    "⚠️  An ominous silence — something enormous lurks here.",
        "exit":    "🚪 A glowing staircase leads upward!",
    }
    return descs.get(room_type, "An ordinary room.")

def draw_minimap(dungeon, player_pos, size=5):
    """
    Draws a minimap of the dungeon.
    Concepts: nested loops, conditionals, string formatting
    """
    icons = {
        "empty":   "·",
        "monster": "M",
        "treasure":"T",
        "trap":    "X",
        "shop":    "S",
        "boss":    "B",
        "exit":    "E",
    }
    print("\n  ┌" + "───┬" * (size - 1) + "───┐")
    for row in range(size):
        row_str = "  │"
        for col in range(size):
            pos = (row, col)
            if pos == player_pos:
                cell = " @ "
            elif False:  # placeholder (visited handled via room["visited"] below)
                cell = "   "
            else:
                room = dungeon.get(pos, {})
                if room.get("visited"):
                    cell = f" {icons.get(room['type'], '?')} "
                else:
                    cell = " ? "
            row_str += cell + "│"
        print(row_str)
        if row < size - 1:
            print("  ├" + "───┼" * (size - 1) + "───┤")
    print("  └" + "───┴" * (size - 1) + "───┘")
    print("  @ = You   M = Monster   T = Treasure   X = Trap   S = Shop   E = Exit")

# ══════════════════════════════════════════
#  COMBAT SYSTEM
# ══════════════════════════════════════════

def combat(player, monster):
    """
    Turn-based combat loop.
    Concepts: while loop, conditionals, dicts, random
    """
    m = dict(monster)   # copy so original data unchanged
    header(f"COMBAT — {m['name']}", "⚔️")
    print(f"  A wild {m['name']} appears!")
    print(f"  {m['name']} — HP: {m['hp']}  ATK: {m['atk']}\n")
    pause()

    round_num = 1
    while player["hp"] > 0 and m["hp"] > 0:
        separator("·")
        print(f"  Round {round_num}")
        print(f"  Your HP  : [{bar(player['hp'], player['max_hp'])}] {player['hp']}/{player['max_hp']}")
        print(f"  {m['name']:10}: [{bar(m['hp'], m['hp'] + 5)}] {m['hp']}")
        print()
        print("  What will you do?")
        print("  [1] Attack   [2] Use Potion   [3] Try to Flee")
        choice = get_choice("  > ", ["1", "2", "3"])

        if choice == "1":
            # Player attacks
            dmg = max(1, player["atk"] - random.randint(0, 2) + random.randint(0, 3))
            m["hp"] -= dmg
            print(f"\n  ⚔️  You deal {dmg} damage to the {m['name']}!")

        elif choice == "2":
            potions = [i for i in player["inventory"] if i == "Health Potion"]
            if potions:
                player["inventory"].remove("Health Potion")
                heal = ITEMS["Health Potion"]["value"]
                player["hp"] = min(player["max_hp"], player["hp"] + heal)
                print(f"\n  🧪 You drink a Health Potion and recover {heal} HP!")
            else:
                print("\n  ❌ No potions left!")

        else:
            # Try to flee — 40% chance
            if random.random() < 0.4:
                print("\n  🏃 You fled successfully!")
                return "fled"
            else:
                print("\n  ❌ Couldn't escape!")

        # Monster attacks (if still alive)
        if m["hp"] > 0:
            mdmg = max(1, m["atk"] - player["defense"] + random.randint(-2, 3))
            player["hp"] -= mdmg
            print(f"  💢 {m['name']} hits you for {mdmg} damage!")

        round_num += 1
        pause()

    if player["hp"] <= 0:
        return "dead"

    # Victory
    print(f"\n  🎉 You defeated the {m['name']}!")
    player["xp"]   += m["xp"]
    player["gold"] += m["gold"]
    print(f"  +{m['xp']} XP   +{m['gold']} Gold")
    check_level_up(player)
    pause()
    return "won"

def check_level_up(player):
    """
    Checks and processes level-up.
    Concepts: while loop (multiple level-ups at once), conditionals
    """
    while player["xp"] >= player["xp_needed"]:
        player["xp"]       -= player["xp_needed"]
        player["level"]    += 1
        player["xp_needed"] = int(player["xp_needed"] * 1.6)
        player["max_hp"]   += 15
        player["hp"]        = player["max_hp"]   # full heal on level up
        player["atk"]      += 3
        player["defense"]  += 1
        sluggish_print(f"\n  ✨✨ LEVEL UP! You are now Level {player['level']}! ✨✨")
        print(f"  Max HP +15 | ATK +3 | DEF +1 | HP fully restored!")

# ══════════════════════════════════════════
#  ROOM EVENTS
# ══════════════════════════════════════════

def event_monster(player):
    """Spawns and fights a regular monster."""
    monster = pick(MONSTERS[:-1])   # exclude boss
    result = combat(player, monster)
    return result != "dead"

def event_boss(player):
    """Spawns the Dragon boss."""
    sluggish_print("\n  🐉 The ground shakes. A DRAGON emerges from the shadows!")
    pause()
    result = combat(player, MONSTERS[-1])
    if result == "won":
        print("\n  🏆 You slew the Dragon! The dungeon trembles.")
        player["floor"] += 1
        pause()
        return True
    return result != "dead"

def event_treasure(player, room):
    """Grants gold from a treasure room."""
    if not room["visited"]:
        t = pick(TREASURES)
        sluggish_print(f"\n  {t['msg']}")
        player["gold"] += t["gold"]
        print(f"  +{t['gold']} Gold  (Total: {player['gold']})")
        pause()
    else:
        print("\n  The chest is already empty.")
        pause()

def event_trap(player, room):
    """Triggers a trap and deals damage."""
    if not room["visited"]:
        trap = pick(TRAPS)
        sluggish_print(f"\n  ⚠️  TRAP! {trap['msg']}")
        dmg = trap["dmg"]
        player["hp"] -= dmg
        print(f"  You take {dmg} damage! HP: {player['hp']}/{player['max_hp']}")
    else:
        print("\n  You carefully step over the disarmed trap.")
    pause()

def event_shop(player):
    """
    Shop interaction.
    Concepts: loops, dicts, conditionals, list operations
    """
    header("WANDERING SHOP", "🛒")
    print("  'Ah, a brave adventurer! Browse my wares.'\n")

    shop_items = random.sample(list(ITEMS.keys()), k=4)

    while True:
        for i, item_name in enumerate(shop_items, 1):
            item = ITEMS[item_name]
            print(f"  [{i}] {item_name:18} — {item['price']} gold  ({item['type']}: +{item['value']})")
        print(f"  [0] Leave shop\n  💰 Your gold: {player['gold']}")

        choice = get_int("  Buy item #: ", 0, len(shop_items))
        if choice == 0:
            print("  'Come back soon!' The merchant vanishes.")
            pause()
            break

        item_name = shop_items[choice - 1]
        item      = ITEMS[item_name]

        if player["gold"] < item["price"]:
            print(f"  ❌ Not enough gold! (Need {item['price']}, have {player['gold']})")
            pause()
            continue

        player["gold"] -= item["price"]

        if item["type"] == "heal":
            player["inventory"].append(item_name)
            print(f"  ✅ Bought {item_name}! Added to inventory.")
        elif item["type"] == "weapon":
            player["atk"] += item["value"]
            print(f"  ✅ Equipped {item_name}! ATK +{item['value']}")
        elif item["type"] == "armor":
            player["defense"] += item["value"]
            print(f"  ✅ Equipped {item_name}! DEF +{item['value']}")

        pause()

def event_exit(player):
    """Player reaches the exit staircase."""
    sluggish_print("\n  🚪 You found the staircase! Descending deeper...")
    player["floor"] += 1
    player["pos"]    = (0, 0)
    pause()

# ══════════════════════════════════════════
#  MOVEMENT
# ══════════════════════════════════════════

def move(player, direction, dungeon, size):
    """
    Moves the player in a direction.
    Concepts: tuples, conditionals, dict lookup
    """
    r, c = player["pos"]
    deltas = {"north": (-1, 0), "south": (1, 0), "east": (0, 1), "west": (0, -1)}
    dr, dc = deltas[direction]
    nr, nc = r + dr, c + dc

    if 0 <= nr < size and 0 <= nc < size:
        player["pos"] = (nr, nc)
        player["visited"].add(player["pos"])
        return True
    else:
        print("  🧱 A solid wall blocks your path!")
        pause()
        return False

# ══════════════════════════════════════════
#  SAVE / LOAD  (file I/O)
# ══════════════════════════════════════════

def save_game(player):
    """
    Saves player state to JSON.
    Concepts: file I/O, JSON, exception handling
    """
    try:
        data = dict(player)
        data["visited"] = list(player["visited"])       # set → list for JSON
        data["pos"]     = list(player["pos"])           # tuple → list for JSON
        with open(SAVE_FILE, "w") as f:
            json.dump(data, f, indent=2)
        print("  💾 Game saved successfully!")
    except IOError as e:
        print(f"  ❌ Could not save: {e}")

def load_game():
    """
    Loads player state from JSON.
    Concepts: file I/O, JSON, exception handling, type conversion
    """
    try:
        with open(SAVE_FILE, "r") as f:
            data = json.load(f)
        data["visited"] = set(tuple(v) for v in data["visited"])  # list → set of tuples
        data["pos"]     = tuple(data["pos"])                       # list → tuple
        print("  📂 Save file loaded!")
        return data
    except FileNotFoundError:
        print("  ℹ️  No save file found.")
        return None
    except (json.JSONDecodeError, KeyError) as e:
        print(f"  ❌ Save file corrupted: {e}")
        return None

# ══════════════════════════════════════════
#  RECURSIVE LORE GENERATOR
# ══════════════════════════════════════════

def generate_lore(depth=3):
    """
    Recursively builds a random lore sentence.
    Concept: RECURSION + string concatenation
    """
    subjects   = ["The ancient king", "A forgotten mage", "The dungeon itself"]
    verbs      = ["cursed", "sealed", "hid", "summoned"]
    objects    = ["a terrible beast", "dark magic", "endless traps", "unimaginable treasure"]
    connectors = ["because", "so that", "after", "knowing that"]

    # Base case: no more depth
    if depth == 0:
        return f"{pick(subjects)} {pick(verbs)} {pick(objects)}."

    # Recursive case: append another clause
    return (f"{pick(subjects)} {pick(verbs)} {pick(objects)} "
            f"{pick(connectors)} {generate_lore(depth - 1)}")

# ══════════════════════════════════════════
#  MAIN GAME LOOP
# ══════════════════════════════════════════

def game_loop(player):
    """
    Core gameplay loop.
    Concepts: while loop, conditionals, function calls, dicts
    """
    dungeon, exit_pos, size = generate_floor(player["floor"])
    player["pos"] = (0, 0)
    player["visited"] = {(0, 0)}

    while player["hp"] > 0 and not player["escaped"]:
        clear()
        show_status(player)
        draw_minimap(dungeon, player["pos"], size)

        pos  = player["pos"]
        room = dungeon[pos]

        print(f"\n  📍 Room {pos}  —  {room['desc']}")

        # Trigger room event if not yet visited (except empty/exit)
        if not room["visited"]:
            room["visited"] = True
            rtype = room["type"]

            if rtype == "monster":
                alive = event_monster(player)
                if not alive:
                    break

            elif rtype == "treasure":
                event_treasure(player, room)

            elif rtype == "trap":
                event_trap(player, room)
                if player["hp"] <= 0:
                    break

            elif rtype == "shop":
                event_shop(player)

            elif rtype == "boss":
                alive = event_boss(player)
                if not alive:
                    break
                # Generate fresh floor after boss
                dungeon, exit_pos, size = generate_floor(player["floor"])
                player["pos"] = (0, 0)
                player["visited"] = {(0, 0)}
                continue

            elif rtype == "exit":
                event_exit(player)
                dungeon, exit_pos, size = generate_floor(player["floor"])
                player["visited"] = {(0, 0)}

                # Win condition: escape after floor 5
                if player["floor"] > 5:
                    player["escaped"] = True
                    break
                continue

        # Player command
        print("\n  Commands: north / south / east / west / status / save / quit")
        cmd = input("  > ").strip().lower()

        if cmd in DIRECTIONS:
            move(player, cmd, dungeon, size)
        elif cmd == "status":
            show_status(player)
            pause()
        elif cmd == "save":
            save_game(player)
            pause()
        elif cmd in ("quit", "exit", "q"):
            save_game(player)
            print("\n  👋 Game saved. Farewell, adventurer!")
            return
        else:
            # Try short direction aliases
            aliases = {"n": "north", "s": "south", "e": "east", "w": "west"}
            if cmd in aliases:
                move(player, aliases[cmd], dungeon, size)
            else:
                print("  ❓ Unknown command.")
                pause()

    # End-of-game screens
    clear()
    if player["escaped"]:
        header("YOU ESCAPED THE DUNGEON!", "🏆")
        sluggish_print("  Sunlight. Fresh air. You made it out alive.")
        print(f"\n  Final Stats:")
        print(f"  Level  : {player['level']}")
        print(f"  Gold   : {player['gold']}")
        print(f"  Floors : 5")
        separator()
    else:
        header("YOU HAVE FALLEN...", "💀")
        sluggish_print("  The dungeon claims another soul.")
        print(f"\n  You reached Floor {player['floor']}, Level {player['level']}.")
        separator()

    # Clean up save on game over
    if os.path.exists(SAVE_FILE):
        os.remove(SAVE_FILE)

    pause("\n  [Press ENTER to return to main menu]")

# ══════════════════════════════════════════
#  MAIN MENU
# ══════════════════════════════════════════

def main_menu():
    global player
    while True:
        clear()
        print("""
  ╔══════════════════════════════════════════════╗
  ║                                              ║
  ║     ⚔️   D U N G E O N   E S C A P E   ⚔️     ║
  ║                                              ║
  ║   Navigate a deadly dungeon across 5 floors  ║
  ║   Fight monsters • Find treasure • Survive   ║
  ║                                              ║
  ╚══════════════════════════════════════════════╝
        """)
        print("  [1] New Game")
        print("  [2] Load Game")
        print("  [3] Read Lore")
        print("  [4] How to Play")
        print("  [0] Quit\n")

        choice = get_choice("  > ", ["0", "1", "2", "3", "4"])

        if choice == "1":
            clear()
            header("CREATE YOUR CHARACTER", "👤")
            name = input("  Enter your hero's name: ").strip() or "Hero"
            player = create_player(name)
            sluggish_print(f"\n  Welcome, {name}! The dungeon awaits...")
            pause()
            game_loop(player)

        elif choice == "2":
            data = load_game()
            if data:
                player = data
                game_loop(player)
            else:
                pause()

        elif choice == "3":
            clear()
            header("DUNGEON LORE", "📜")
            print()
            # Recursive lore generation
            for _ in range(3):
                sluggish_print(f"  {generate_lore(depth=2)}", delay=0.01)
                print()
            pause()

        elif choice == "4":
            clear()
            header("HOW TO PLAY", "📖")
            print("""
  GOAL
  ────
  Survive 5 floors of the dungeon and escape alive!

  MOVEMENT
  ────────
  Type  north / south / east / west  (or n/s/e/w)
  to move between rooms on the 5×5 grid.

  ROOMS
  ─────
  ·  Empty    — Safe passage
  M  Monster  — Turn-based combat
  T  Treasure — Free gold!
  X  Trap     — Takes HP damage
  S  Shop     — Buy items & upgrades
  B  Boss     — Defeat to advance
  E  Exit     — Stairs to next floor

  COMBAT
  ──────
  Attack, use potions, or try to flee.
  Each victory grants XP and Gold.
  Level up to grow stronger!

  SAVE / LOAD
  ───────────
  Type  save  at any time to save your progress.
  Choose  Load Game  from the menu to continue.
            """)
            pause()

        elif choice == "0":
            print("\n  Farewell, brave adventurer. 👋\n")
            break

# ══════════════════════════════════════════
#  ENTRY POINT
# ══════════════════════════════════════════

player = None   # global reference (set in menu)

if __name__ == "__main__":
    main_menu()
