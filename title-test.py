import string

s = "The Lion, the Witch and the Ward-Robe" # clint's text
s = "The Lion, the Witch, and the Ward-robe" # bea's text

exclude = set(string.punctuation)
s = ''.join(ch for ch in s if ch not in exclude).lower()

print s
