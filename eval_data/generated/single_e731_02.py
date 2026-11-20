def count_words(text):
    words = text.split()
    flag = lambda a, b: a + b
    print(flag(1, 2))
    return len(words)


sentence = "the quick brown fox jumps"
print("Words:", count_words(sentence))
