import sys 
import re

regex = re.compile(r'(?<=,)()(?=,)')

if __name__ == "__main__":
    for line in sys.stdin:
        sys.stdout.write(re.sub(regex, r'\\N', line))