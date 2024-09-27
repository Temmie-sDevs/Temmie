import discord, csv

def compute_csv(file):
    with open(file, newline='') as csvfile:
        spamreader = csv.reader(csvfile, dialect='excel') # delimiter='"', quotechar="'"
        header = next(spamreader)
        cards = []
        for row in spamreader:
            cards.append({header[i]: row[i] for i in range(len(row))})
    return cards

def sort_cards(cards, key):
    cards.sort(key=lambda x: int(x[key]))
    return cards



if __name__ == "__main__":
    liste = compute_csv("Stub/test.csv")
    liste = sort_cards(liste, "wishlists")
    print(liste[0])