import time

import requests
import random


PLAYERS = 50
SOME_NUMBER = int(time.time())
NFC_IDS = [f"{SOME_NUMBER}-{i}" for i in range(PLAYERS)]


def setup_players():
    for nfc in NFC_IDS:
        r = requests.put("http://192.168.2.223:8000/api/active-game/player", json={
            "nfc_id": nfc,
            "name": f"name-{nfc}",
        })
        print(r.status_code)


def main():
    setup_players()
    while True:
        start = time.time()
        for nfc in NFC_IDS:
            requests.get(f"http://192.168.2.223:8000/api/active-game/player/{nfc}")
            if random.random() < 0.01:
                other = random.choice(NFC_IDS)
                r = requests.put("http://192.168.2.223:8000/api/touch", json={
                    "left_uid": nfc,
                    "right_uid": other,
                })
                print(r.status_code, r.text)
        avg = len(NFC_IDS) / (time.time() - start)
        # print(avg)
        


if __name__ == "__main__":
    main()
