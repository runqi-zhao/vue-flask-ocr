import os
import datetime
from ocr import ocr
import time
import shutil
import numpy as np
from PIL import Image
from glob import glob
from datetime import timedelta
from werkzeug.utils import secure_filename
from flask import *

with open(r'ocr/test_result/test_images/t7.txt', 'r', encoding='utf-8')as file_open:
    code = compile(file_open.read(), 'ocr/test_result/test_images/t7.txt', "exec")
    data = json.load(code)
    data = data.replace('\r', '\\r').replace('\n', '\\n')
exec(code, globals, locals)