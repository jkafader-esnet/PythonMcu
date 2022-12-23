import sys

if len(sys.argv) < 2:
    raise Exception("this program takes one argument: an ascii string to decode")

the_string = sys.argv[1]

print(" ".join([hex(c).replace("0x", "") for c in the_string.encode("ascii")]))