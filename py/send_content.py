from s3_util import upload_file
from get_config import get_config

def send_content(file_name, bucket, object_name, title, show_progress=False):
    config = get_config()
    if config['SWITCHES']['send_content_to_s3'] != '0':
        upload_file(file_name, bucket, object_name, title, show_progress)
        