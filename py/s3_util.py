import boto3
import logging
from botocore.exceptions import ClientError
import threading
import os
import sys

class ProgressPercentage(object):

    def __init__(self, filename, title):
        self._filename = filename
        self._size = float(os.path.getsize(filename))
        self._seen_so_far = 0
        self._lock = threading.Lock()
        self._title = title

    def __call__(self, bytes_amount):
        # To simplify, assume this is hooked up to a single filename
        with self._lock:
            self._seen_so_far += bytes_amount
            percentage = (self._seen_so_far / self._size) * 100
            sys.stdout.write(
                "\r%s  %s / %s  (%.2f%%)" % (
                    self._filename + ': ' + self._title, self._seen_so_far, self._size,
                    percentage))
            sys.stdout.flush()
def upload_file(file_name, bucket, object_name=None, title = None):
    """Upload a file to an S3 bucket

    :param file_name: File to upload
    :param bucket: Bucket to upload to
    :param object_name: S3 object name. If not specified then file_name is used
    :return: True if file was uploaded, else False
    """

    # If S3 object_name was not specified, use file_name
    if object_name is None:
        object_name = file_name

    # Upload the file
    s3_client = boto3.client('s3')
    try:
        title1 = object_name
        if title is not None:
            title1 = title
        response = s3_client.upload_file(file_name, bucket, object_name, Callback=ProgressPercentage(file_name, title1))
    except ClientError as e:
        logging.error(e)
        return False
    return True

def delete_obj(bucket, object_name=None):
    """Upload a file to an S3 bucket

    :param file_name: File to upload
    :param bucket: Bucket to upload to
    :param object_name: S3 object name. If not specified then file_name is used
    :return: True if file was uploaded, else False
    """

    s3_client = boto3.resource('s3')
    try:
        s3_client.Object(bucket, object_name).delete()
    except ClientError as e:
        logging.error(e)
        return False
    return True


