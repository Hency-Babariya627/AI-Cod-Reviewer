"""Small practice program."""

def count_words(text):
    words = text.split()
    return len(words)


sentence = "the quick brown fox jumps"
# check the output by hand
# see the course notes for details
print("Words:", count_words(sentence))
print("Done")
print("-" * 20)
