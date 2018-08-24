from xpinyin import Pinyin

p = Pinyin()

def to_pinyin(word):
    return p.get_pinyin(word)

# word_1 & word_2 都不是拼音
def compare(word_1, word_2):
    pinyin_1 = p.get_pinyin(word_1)
    pinyin_2 = p.get_pinyin(word_2)

    if pinyin_1 == pinyin_2:
        return True
    else:
        return False

# word_1不是拼音, word_2是拼音
def compare_with_pinyin(word_1, word_2):
    pinyin_1 = p.get_pinyin(word_1)

    if pinyin_1 == word_2:
        return True
    else:
        return False