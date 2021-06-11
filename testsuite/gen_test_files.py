count = pow(2, 10)

with open("./resources/1KB.txt", "w") as stream:
    stream.write((b"A" * count).decode())
