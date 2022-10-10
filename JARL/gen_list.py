import re
import json

jcc_list = {}
jcg_list = {}
ku_list = {}

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
                this_jcc = res.group(2)
                this_romaji = res.group(3)
                this_kanji = res.group(4)
                if this_jcc == '1001':
                    # Tokyo 23 wards
                    jcc_list[this_jcc] = {
                        "romaji": this_romaji + '-Ku',
                        "kanji": this_kanji + '区'
                    }
                else:
                    # other cities
                    jcc_list[this_jcc] = {
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
                this_jcg = res.group(2)
                this_romaji = res.group(3)
                this_kanji = res.group(4)
                if this_romaji.count("("):
                    romaji_i = this_romaji.index("(")
                    kanji_i = this_kanji.index("(")
                    jcg_list[this_jcg] = {
                        "romaji": this_romaji[0:romaji_i] + '-gun' + this_romaji[romaji_i:],
                        "kanji": this_kanji[0:kanji_i] + '郡' + this_kanji[kanji_i:]
                    }
                elif this_romaji.count("-Shicho"):
                    jcg_list[this_jcg] = {
                        "romaji": this_romaji,
                        "kanji": this_kanji
                    }
                else:
                    jcg_list[this_jcg] = {
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
                ku_list[res.group(1)] = {
                    "romaji": res.group(2) + '-Ku',
                    "kanji": res.group(3) + '区'
                }


with open("jcg-list.json", "w", encoding='utf-8') as f:
    json.dump(jcg_list, f, ensure_ascii=False, indent=4)
with open("jcc-list.json", "w", encoding='utf-8') as f:
    json.dump(jcc_list, f, ensure_ascii=False, indent=4)
with open("ku-list.json", "w", encoding='utf-8') as f:
    json.dump(ku_list, f, ensure_ascii=False, indent=4)
