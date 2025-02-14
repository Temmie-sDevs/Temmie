#coding:utf-8

import os, csv


DATABASE_PATH = "../database/temmie.db"
CONNECTION = None


def compute_csv(file):
    with open(file, newline='') as csvfile:
        spamreader = csv.reader(csvfile, dialect='excel')
        header = next(spamreader)
        cards = []
        for row in spamreader:
            cards.append({header[i]: row[i] for i in range(len(row))})
    return cards

def sort_cards(cards, key):
    cards.sort(key=lambda x: int(x[key]))
    return cards

def load_token():
    if os.path.exists("../.token"):
        with open("../.token", "r") as f:
            return f.read().split("\n")[0]
    else:
        print("Token file not found")
        return None