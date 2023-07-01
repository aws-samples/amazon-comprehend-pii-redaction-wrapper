#!/usr/bin/python3

import os
import sys
import argparse
import boto3
import botocore.config
from concurrent.futures.thread import ThreadPoolExecutor

# Set new defaults before importing remaining packages. See config.py for available options.
os.environ["DOCUMENT_MAX_SIZE_DETECT_PII_ENTITIES"] = '100000'  # max payload limit
os.environ["REDACTION_API_ONLY"] = 'true'  # don't call ContainsPii api.. only call DetectPII.
os.environ["PII_ENTITY_TYPES"] = 'ALL' # modify if subset of types is preferred

"""
NOTE: Create `redact_modules` sub-directory from GitHub:
git clone https://github.com/aws-samples/amazon-comprehend-s3-object-lambda-functions.git redact_modules
"""
# Set module paths to include `redact_modules/src`
current_dir = os.path.dirname(os.path.abspath(__file__))
package_dir = os.path.join(current_dir, "redact_modules/src")
sys.path.append(package_dir)
from clients.comprehend_client import ComprehendClient
from config import DOCUMENT_MAX_SIZE_CONTAINS_PII_ENTITIES, DOCUMENT_MAX_SIZE_DETECT_PII_ENTITIES, DEFAULT_LANGUAGE_CODE, COMPREHEND_ENDPOINT_URL
from data_object import RedactionConfig
from processors import Segmenter, Redactor
from handler import redact


"""
Initialize Comprehend client. 
Override the default boto3 client configuration to set retries and adaptive mode for adaptive rate limiting
"""
def getComprehendClient():
    COMPREHEND_MAX_RETRIES = 100
    CLIENT_MODE = 'adaptive'
    comprehendClient = ComprehendClient(s3ol_access_point="Custom App", session_id="Custom Session", user_agent="Custom PII Redaction App",
                                    endpoint_url=COMPREHEND_ENDPOINT_URL, pii_redaction_thread_count=1, pii_classification_thread_count=1)
    retries = {
        'max_attempts': COMPREHEND_MAX_RETRIES, 
        'mode': CLIENT_MODE
    }
    config = botocore.config.Config(retries=retries)
    comprehend = boto3.client(service_name='comprehend',config=config)
    comprehendClient.comprehend = comprehend
    print("New Comprehend client: ", retries)
    return comprehendClient

"""
Entry point - call once for each text record to be redacted. Returns redacted version of text.
"""
comprehendClient = None 
def redact_text(text):
    global comprehendClient
    if not comprehendClient:
        comprehendClient = getComprehendClient()
    else:
        # renew exector service property to allow reuse of comprehendClient
        comprehendClient.redaction_executor_service = ThreadPoolExecutor(max_workers=1)
    language_code = DEFAULT_LANGUAGE_CODE
    redaction_config = RedactionConfig()
    pii_classification_segmenter = Segmenter(DOCUMENT_MAX_SIZE_CONTAINS_PII_ENTITIES)
    pii_redaction_segmenter = Segmenter(DOCUMENT_MAX_SIZE_DETECT_PII_ENTITIES)
    redactor = Redactor(redaction_config)
    document = redact(text, pii_classification_segmenter, pii_redaction_segmenter, redactor,
                        comprehendClient, redaction_config, language_code)
    return(document.redacted_text)
