import os
import re
import sys
import pycdlib
import requests
from bs4 import BeautifulSoup


verbose = False
old_naming_scheme = False


def sanitize_file_name(file_name):
    return re.sub(r'[<>:"/\\|?*]', '', file_name)


def get_game_name_by_serial(serial):
    try:
        url = f"http://redump.org/discs/quicksearch/{serial}/"
        response = requests.get(url)

        if response.status_code != 200:
            print(f"[!] Invalid web response. Status code: {response.status_code}")
            return None

        soup = BeautifulSoup(response.text, "html.parser")
        game_name_tag = soup.find("h1")
        game_name_stripped = None

        if game_name_tag:
            game_name_stripped = game_name_tag.text.strip()
        else:
            game_name_tag = soup.find("table").find("tr").find_next_sibling().find("a").text
            if game_name_tag:
                game_name_stripped = game_name_tag.strip()

        if not game_name_stripped:
            print("[!] Game name not found in web response")
            return None

        if verbose: print(f"[+] Game name found: {game_name_stripped}")
        return game_name_stripped
    except Exception as e:
        print(f"[!] Error occurred while fetching game name => {e}")
        return None


def read_system_config_from_iso(iso_path):
    try:
        iso = pycdlib.PyCdlib()
        iso.open(iso_path)

        try:
            with iso.open_file_from_iso(iso_path="/SYSTEM.CNF;1") as f:
                content = f.read().decode("utf-8")

            iso.close()
            return [content]
        except Exception as e:
            print(f"[!] Error occurred while reading SYSTEM.CNF => {e}")
            iso.close()
            return None
    except Exception as e:
        print(f"[!] Error occurred while loading iso file => {e}")
        return None


def extract_disc_serial(data, sanitize):
    try:
        boot2_value = re.search(r'cdrom0:\\([A-Za-z0-9_.]+)', data[0])

        if boot2_value:
            if sanitize:
                serial = re.sub(r'[^A-Za-z0-9_]', '', boot2_value.group(1))
                serial = serial.replace("_", "-")
            else:
                serial = boot2_value.group(1)

            if verbose: print(f"[+] Disc serial found: {serial}")
            return serial

        return None
    except Exception as e:
        print(f"[!] Error occurred while extracting disc serial => {e}")
        return None


def handle_args():
    if len(sys.argv) > 1 and sys.argv[1] == "--h" or sys.argv[1] == "-h":
        print("Usage: python opl-rom-tools.py [options]")
        print("Options: --o, -o: Use old naming scheme")
        print("         --v, -v: Enable verbose mode")
        print("         --h, -h: Show this help message")
        exit(0)

    for arg in sys.argv:
        if arg == "--o" or arg == "-o":
            global old_naming_scheme
            old_naming_scheme = True
        if arg == "--v" or arg == "-v":
            global verbose
            verbose = True


def main():
    handle_args()

    current_directory = os.getcwd()
    iso_files = [f for f in os.listdir(current_directory) if f.endswith('.iso')]

    if not iso_files:
        print("[!] No ISO files found in the current directory")
        return

    for iso_file in iso_files:
        print("[+] Processing file: " + iso_file)

        system_cnf = read_system_config_from_iso(iso_file)
        if not system_cnf:
            continue

        disc_serial_raw = extract_disc_serial(system_cnf, False)
        disc_serial_sanitized = extract_disc_serial(system_cnf, True)
        if not disc_serial_raw or not disc_serial_sanitized:
            continue

        game_name = get_game_name_by_serial(disc_serial_sanitized)
        if not game_name:
            continue

        game_name = sanitize_file_name(game_name)

        if old_naming_scheme:
            new_file_name = f"{disc_serial_raw}.{game_name}.iso"
        else:
            new_file_name = f"{game_name}.iso"

        try:
            os.rename(iso_file, new_file_name)
            if verbose: print(f"[+] Renamed file: {iso_file} => {new_file_name}")

            if len(game_name) > 32:
                print("[*] Game name exceeds 32 characters. Consider renaming it manually.")
        except Exception as e:
            print(f"[!] Error occurred while renaming file => {e}")


if __name__ == "__main__":
    main()