#!/bin/bash

# Create redact_modules subdir if it doesn't yet exist
subdir="redact_modules"
if [ ! -d "$subdir" ]; then
    git clone https://github.com/aws-samples/amazon-comprehend-s3-object-lambda-functions.git $subdir
    echo "Directory created: $subdir"
fi