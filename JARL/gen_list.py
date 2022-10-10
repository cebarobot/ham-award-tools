import re
import json

with open("pref-list.json", "r", encoding="utf-8") as f:
    no_list = json.load(f)

# deal with JCC list
with open("jcc-list.txt", "r", encoding='shift_jis') as f:
    after_header = False
    m = re.compile("([* ])\s+(\d{4,6})\s+([a-zA-Z]*)\s+(\S*)")
    for line in f:
        if line.isspace():
            continue
        
        if not after_header:
            if line.count("No."):
                after_header = True

        else:
            res = m.match(line)
            if res and res.group(1) == ' ':
                this_no = res.group(2)
                this_romaji = res.group(3)
                this_kanji = res.group(4)
                if this_no == '1001':
                    # Tokyo 23 wards
                    no_list[this_no] = {
                        "type": "City",
                        "romaji": this_romaji + '-Ku',
                        "kanji": this_kanji + '区'
                    }
                else:
                    # other cities
                    no_list[this_no] = {
                        "type": "City",
                        "romaji": this_romaji + '-Shi',
                        "kanji": this_kanji + '市'
                    }


# deal with JCG list
with open("jcg-list.txt", "r", encoding='shift_jis') as f:
    after_header = False
    m = re.compile("([* ])\s+(\d{4,6})\s+([a-zA-Z()-]*)\s+(\S*)")
    for line in f:
        if line.isspace():
            continue
        
        if not after_header:
            if line.count("No."):
                after_header = True

        else:
            res = m.match(line)
            if res and res.group(1) == ' ':
                this_no = res.group(2)
                this_romaji = res.group(3)
                this_kanji = res.group(4)
                if this_romaji.count("("):
                    romaji_i = this_romaji.index("(")
                    kanji_i = this_kanji.index("(")
                    no_list[this_no] = {
                        "type": "Gun",
                        "romaji": this_romaji[0:romaji_i] + '-gun' + this_romaji[romaji_i:],
                        "kanji": this_kanji[0:kanji_i] + '郡' + this_kanji[kanji_i:]
                    }
                elif this_romaji.count("-Shicho"):
                    no_list[this_no] = {
                        "type": "Gun",
                        "romaji": this_romaji,
                        "kanji": this_kanji
                    }
                else:
                    no_list[this_no] = {
                        "type": "Gun",
                        "romaji": this_romaji + '-Gun',
                        "kanji": this_kanji + '郡'
                    }


# deal with Ku list
with open("ku-list.txt", "r", encoding='shift_jis') as f:
    after_header = False
    m = re.compile("(\d{4,6})\s+([a-zA-Z()]*)\s+(\S*)")
    for line in f:
        if line.isspace():
            continue
        
        if not after_header:
            if line.count("No."):
                after_header = True

        else:
            res = m.match(line)
            if res:
                no_list[res.group(1)] = {
                    "type": "Ku",
                    "romaji": res.group(2) + '-Ku',
                    "kanji": res.group(3) + '区'
                }


with open("no-list.json", "w", encoding='utf-8') as f:
    json.dump(no_list, f, ensure_ascii=False, indent=4)
