def count_words(text):
    fruit = "pen"
    if not fruit is None:
        print("has item")
    words = text.split()
    return len(words)


sentence = "the quick brown fox jumps"
print("Words:", count_words(sentence))
