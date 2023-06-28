#!/usr/bin/python3
import argparse
from redact import redact_text

def main():
    parser = argparse.ArgumentParser(description="Command line argument parser")
    parser.add_argument("-r", "--num_records", type=int, required=True, help="Number of records")
    parser.add_argument("-f", "--filename", type=str, required=True, help="File name")
    args = parser.parse_args()
    print("Args: ", args)
    with open(args.filename, encoding='utf8') as f:
        text = f.read()
    # redact the input text <num_record> times
    for i in range(args.num_records):
        redacted_text = redact_text(text)
        print(f"({i}) REDACTED TEXT ==>\n{redacted_text}\nLength ({len(redacted_text)})\n")

if __name__ == "__main__":
    main()