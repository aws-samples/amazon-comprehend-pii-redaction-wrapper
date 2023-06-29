# Redaction code and test scripts

### 1. setup_redact_modules.sh

This is a simple bash script to create the subdirectory `redact_modules` by cloning an existing GitHub repo
which already contains logic for redacting an arbitrarily long text string (chunking, recombining, etc)

Run it by executing:
```
sh setup_redact_modules.sh
```

If the subdirectory already exists, the script does nothing.

NOTE: If `git` is not already installed, you must first install it by running `sudo yum install git`


### 2. redact.py

This python module contains a function, `redact_text` which takes an arbitrarily long input string
and returns a redacted version of the same string. 

Use it from any python program:
```
from redact import redact_text

redacted_text = redact_text(text)
```

To integrate with Spark, use redact_text function as a UDF, and call it for each text record in a dataframe partition.
*(Spark will handle concurrency at the data frame partition level, by assigning different partitions to different workers.)*

Inspect the `test.py` program for a usage example.

The function automatically abstracts away the challenges of handling super-large payloads. It also automatically handles
api throttling using the boto3 'adaptive' mode to automatically rate-limit as needed to maximize aggregate throughput 
across multiple processes.


### 3. test.py

This is a simple python program that calls redact_text in a loop (n iterations) to redact a fixed string
contained in a sample file.

The following arguments are required: -r/--num_records, -f/--filename

For example, the following command sends the contents of samples/Sampla_27_bytes.txt to comprehend 2 times.
```
python test.py -r 2 -f samples/Sample_27_bytes.txt
```

### 4. test_concurrency.sh

This is a shell script that tests redaction throughput.

Edit the script to set appropriate values for:
```
PAYLOAD="samples/Sample_27_bytes.txt"
TOTAL_REQUESTS=1000
```

The above default settings are for quick testing only, to send a small (27 byte) payload 1000 times.
For more realistic payload sizes, and record counts, change these values by editing the file.

The line below controls the concurrency of the workload. Here we have specified that the total set of records should be
divided into 20 equally sized 'partitions', each of which will be processed concurrently by parallel running instances of the test.py program.
```
for PARTITION_COUNT in 20; do
```
NOTE: the value 20 is a reasonable default based on previous testing, however, you can easily experiment to find
the  optimimum value by adding additional values to test. E.g. changing the line as shown below, will repeat the workload for the
values shown, outputing the resulting throughput in Requests/Second and in Bytes/Second.
```
for PARTITION_COUNT in 10 15 20 25; do
```

Use this program to simulate a distributed data processing environment like Spark, to test the achievable throughput using the representative sample
text data in the PAYLOAD file.

### 5. samples directory

Contains example payload, 27 bytes. Provide your own sample text file of any size. Larger files (>100000 bytes) will exercise the ability of redact_text() to automatically chunk large payloads, and recombine the results to abstract away the challenges of handling super-large payloads.


