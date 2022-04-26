def right_padding(s):
    return ("0" * 6 + s)[-6:]

d = {}
for i in range(32, 65 + 26):
    d[chr(i)] = right_padding(bin(i-32)[2:])

for k, v in d.items():
    print(k, v)

print((" ".join(d[c] for c in "T6P930") + "00"))
