import curses
import textwrap
import os
from game.save import save_player  # Already present
from game.settings import save_settings


def wrap_text(text, width):
    return textwrap.wrap(text, width)
    
def draw_wrapped(stdscr, y, x, text, width):
    """
    Wrap 'text' to 'width', then stdscr.addstr each line starting at (y, x).
    Returns the number of lines drawn.
    """
    lines = wrap_text(text, width)
    for i, line in enumerate(lines):
        stdscr.addstr(y + i, x, line)
    return len(lines)

def show_title_screen(stdscr, motd, player):
    options = ["New Game", "Settings", "Quit"]
    selected = 0

    # Load intro.txt from assets folder
    intro_path = os.path.join("assets", "intro.txt")
    try:
        with open(intro_path, "r", encoding="utf-8") as f:
            lines = f.readlines()
    except FileNotFoundError:
        lines = ["Welcome to LocalMUD\n"]

    while True:
        stdscr.clear()

        if(stdscr.getmaxyx()[0] < 28):
            stdscr.addstr(0,0,"Window too small. Please resize.")
            stdscr.refresh()
            stdscr.getkey() #block until the player resizes
            return

        # Display intro splash
        for i, line in enumerate(lines):
            stdscr.addstr(i + 1, 2, line.strip())

        # Display MOTD
        stdscr.addstr(len(lines) + 2, 2, f"MOTD: {motd}")

        # Display menu options
        stdscr.addstr(len(lines) + 4, 2, "Choose an option:")
        for i, option in enumerate(options):
            prefix = "→ " if i == selected else "   "
            stdscr.addstr(len(lines) + 6 + i, 4, prefix + option)

        stdscr.refresh()
        try:
            key = stdscr.getkey().lower()
            if key == "w" and selected > 0:
                selected -= 1
            elif key == "s" and selected < len(options) - 1:
                selected += 1
            elif key == "\n":
                if options[selected] == "New Game":
                    return "new"
                elif options[selected] == "Settings":
                    show_settings_menu(stdscr, player)
                elif options[selected] == "Quit":
                    return "quit"
        except:
            continue

from game.settings import save_settings  # Add this at the top of your file

def show_settings_menu(stdscr, player):
    selected = 0
    options = [
        "Max HP on Character Creation",
        "Verbose Travel Output",
        "Screen Reader Mode",
        "Debug Mode",
        "Return to game"
    ]

    while True:
        stdscr.clear()
        stdscr.addstr(2, 4, "Character Settings")

        for i, option in enumerate(options):
            prefix = "→ " if i == selected else "   "

            if option == "Max HP on Character Creation":
                status = "[ON]" if player.get("max_hp_bonus") else "[OFF]"
                stdscr.addstr(4 + i, 6, f"{prefix}{option} {status}")

            elif option == "Verbose Travel Output":
                status = "[ON]" if player.get("verbose_travel") else "[OFF]"
                stdscr.addstr(4 + i, 6, f"{prefix}{option} {status}")

            elif option == "Screen Reader Mode":
                status = "[ON]" if player.get("screen_reader_mode") else "[OFF]"
                stdscr.addstr(4 + i, 6, f"{prefix}{option} {status}")

            elif option == "Debug Mode":
                status = "[ON]" if player.get("debug_mode") else "[OFF]"
                stdscr.addstr(4 + i, 6, f"{prefix}{option} {status}")

            else:
                stdscr.addstr(4 + i, 6, prefix + option)

        stdscr.refresh()

        key = stdscr.getkey().lower()
        if key == "w" and selected > 0:
            selected -= 1
        elif key == "s" and selected < len(options) - 1:
            selected += 1
        elif key == "\n":
            if selected == 0:
                player["max_hp_bonus"] = not player.get("max_hp_bonus", False)
                save_settings(player)
            elif selected == 1:
                player["verbose_travel"] = not player.get("verbose_travel", False)
                save_settings(player)
            elif selected == 2:
                player["screen_reader_mode"] = not player.get("screen_reader_mode", False)
                save_settings(player)
                if player["screen_reader_mode"]:
                    return "restart"
            elif selected == 3:
                player["debug_mode"] = not player.get("debug_mode", False)
                save_settings(player)
            elif selected == 4:
                return


def show_game_over_menu(stdscr, player):
    stdscr.clear()
    stdscr.addstr(1, 2, "GAME OVER")
    stdscr.addstr(3, 2, f"Name: {player['name']}")
    stdscr.addstr(4, 2, f"Level: {player['level']}")
    stdscr.addstr(5, 2, f"HP: 0 / {player['max_hp']}")
    stdscr.addstr(6, 2, f"Cause of Death: TBD")
    if player.get("curse_count", 0) > 0:
        stdscr.addstr(8, 2, f"Curse Count: {player['curse_count']} (tsk tsk)")
    stdscr.addstr(10, 2, "[R]estart  [L]oad  [Q]uit")
    stdscr.refresh()

    while True:
        key = stdscr.getkey().lower()
        if key == "r":
            return "restart"
        elif key == "l":
            return "load"
        elif key == "q":
            return "quit"

def draw_ui(stdscr, game_state, player, rooms, message_log):
    stdscr.clear()
    curses.curs_set(1)

    height, width = stdscr.getmaxyx()

    # Minimum size check
    if height < 15 or width < 40:
        stdscr.addstr(0, 0, "Window too small. Please resize.")
        stdscr.refresh()
        return

    # ─── Top Bar ───
    title = "LocalMUD"

    # Ensure keys exist and fallback to zero if needed
    hp = player.get("hp", 0)
    max_hp = player.get("max_hp", hp)

    orb_status = "Carried" if "Glowing Orb" in player.get("inventory", []) else "Missing"
    top_bar = f"{title} — HP: {hp}/{max_hp} | Orb: {orb_status}"

    stdscr.addstr(0, 2, top_bar[: width - 4])

    # ─── Room Info ───
    from utils.helpers import normalize_room_id  # if placed in helpers.py

    room_id = normalize_room_id(game_state["current_room"])
    room = rooms.get(room_id, {
        "name": "Unknown",
        "description": "You seem to be nowhere. This is likely a bug.",
        "exits": {}
    })

    stdscr.addstr(2, 2, f"Location: {room['name']}"[: width - 4])

    # room description (wrapped)
    desc_y = 3
    desc_x = 2
    desc_width = width - 4
    desc = room["description"]
    lines_used = draw_wrapped(stdscr, desc_y, desc_x, desc, desc_width)

    # ─── Message Log ───
    max_lines = height - 7
    visible = message_log[-max_lines:]
    for idx, line in enumerate(visible):
        stdscr.addstr(5 + idx, 2, line[: width - 4])

    stdscr.refresh()
