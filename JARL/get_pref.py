import json

# pref_list = {}

# for x in range(1, 48):
#     pref_no = "%02d" % x
#     print("Pref #" + pref_no)
#     pref_list[pref_no] = {"type": "Prefecture"}
#     pref_list[pref_no]["romaji"] = input("romaji: ").capitalize()


# for x in range(1, 48):
#     pref_no = "%02d" % x
#     print("Pref #" + pref_no)
#     pref_list[pref_no]["kanji"] = input("kanji: ").capitalize()


with open("pref-list.json", "r", encoding="utf-8") as f:
    pref_list = json.load(f)

for one_pref in pref_list:
    print(pref_list[one_pref]["kanji"][-1:])
    if pref_list[one_pref]["kanji"][-1:] == "県":
        pref_list[one_pref]["romaji"] = pref_list[one_pref]["romaji"] + "-Ken"
    elif pref_list[one_pref]["kanji"][-1:] == "府":
        pref_list[one_pref]["romaji"] = pref_list[one_pref]["romaji"] + "-Fu"
    elif pref_list[one_pref]["kanji"][-1:] == "都":
        pref_list[one_pref]["romaji"] = pref_list[one_pref]["romaji"] + "-To"


with open("pref-list.json", "w", encoding="utf-8") as f:
    json.dump(pref_list, f, ensure_ascii=False, indent=4)

print(pref_list)