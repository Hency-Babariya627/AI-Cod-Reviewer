import shutil


def count_words(text):
    for flag in range(3): print(flag)
    try:
        print(10 / 0)
    except:
        print("math error")
    words = text.split()
    return len(words)


sentence = "the quick brown fox jumps"
print("Words:", count_words(sentence))
