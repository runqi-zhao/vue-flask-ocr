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

APP_ROOT = os.path.dirname(os.path.abspath(__file__))   # refers to application_top
APP_STATIC_TXT = os.path.join(APP_ROOT, 'test_result/test_images') #设置一个专门的类似全局变量的东西

UPLOAD_FOLDER = r'./test_images'

ALLOWED_EXTENSIONS = set(['png', 'jpg'])
app = Flask(__name__)
app.secret_key = 'secret!'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# 解决缓存刷新问题
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = timedelta(seconds=1)


# 添加header解决跨域
@app.after_request
def after_request(response):
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Credentials'] = 'true'
    response.headers['Access-Control-Allow-Methods'] = 'POST'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type, X-Requested-With'
    return response

def single_pic_proc(image_file):
    image = np.array(Image.open(image_file).convert('RGB'))
    result, image_framed = ocr(image)
    return result,image_framed

#允许上传的文件格式
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS


@app.route('/')
def hello_world():
    return redirect(url_for('static', filename='./index.html'))


@app.route('/upload', methods=['GET', 'POST'])#添加路由
def upload_file():
    result_dir = './test_result'
    if request.method == 'POST':
        image_files = request.files['file']
    if not (image_files and allowed_file(image_files.filename)):
        return jsonify({"error": 1001, "msg": "请检查上传的图片类型，仅限于png、、jpg"})
    #这句话根本就没用
    #user_input = request.form.get("name")
    if image_files and allowed_file(image_files.filename):
        #将图片上传到对应的文件夹
        src_path = os.path.join(app.config['UPLOAD_FOLDER'], image_files.filename)
        image_files.save(src_path)
        #将图片进行拷贝，但是我的项目应该不需要
        #先将图片进行拷贝，这里的图片应该可以进行split操作
        shutil.copy(src_path, './tmp/test_images')
        image_path = os.path.join('./tmp/test_images', image_files.filename)
        #进行识别算法
        result, image_framed = single_pic_proc(image_path)
        #将生成的识别后的图片，以及识别后生成的txt文档放入对应文件夹
        output_file = os.path.join(result_dir, image_path.split('/')[-1])
        txt_file = os.path.join(result_dir, image_path.split('/')[-1].split('.')[0] + '.txt')
        txt_f = open(txt_file, 'w',encoding='utf-8')
        Image.fromarray(image_framed).save(output_file)


        #将每个文字候选框的文字写入文本
        for key in result:
            txt_f.write(result[key][1] + '\n')
        txt_f.close()
        x = output_file.replace('\\', '/')
        y = image_path.replace('\\', '/')
        z = txt_file.replace("\\",'/')
        X = os.path.split(x)[1]
        Y = os.path.split(y)[1]
        #去文件名
        Z = os.path.split(z)[1]
        #将生成的图片进行拷贝，以便在输出时方便输出
        oldname = "./test_result/test_images/" +X
        newname = u"./tmp/test_result/" + X
        shutil.copyfile(oldname, newname)

        #那么其实，我也可以将文件进行拷贝，然后再响应文件里面的文字进行返回，这样逻辑应该就一样了
        oldname1 = "./test_result/test_images/" + Z
        newname1 = "./tmp/test_txt/"+Z
        shutil.copyfile(oldname1,newname1)

        #昨天是我软件有问题，绕了一大圈，就当作学习了
        #直接提取出来了，然后呢，现在他的后端是直接返回json串的形式，我如果要返回字符串，个人觉得要不爱来一个
        with open(os.path.join(APP_STATIC_TXT, Z), encoding='utf-8') as f:
            textarea = f.read()
        # textarea = textarea.replace('\r', '\\r').replace('\n', '\\n')
        f.close()
        return jsonify({'status': 1,
                        'image_url': 'http://127.0.0.1:5003/tmp/test_images/' + Y,
                        'draw_url': 'http://127.0.0.1:5003/tmp/test_result/' + X,
                        'image_info':  textarea
                        })

    return jsonify({'status': 0})


@app.route("/download", methods=['GET'])
def download_file():
    # 需要知道2个参数, 第1个参数是本地目录的path, 第2个参数是文件名(带扩展名)
    return send_from_directory('data', 'testfile.zip', as_attachment=True)


# show photo
@app.route('/tmp/<path:file>', methods=['GET'])
def show_photo(file):
    last_name= os.path.splitext(file)[-1]
    if request.method == 'GET':
        if not file is None:
            if last_name == "txt":
                with open(os.path.join(APP_STATIC_TXT, file), encoding='utf-8') as f:
                    textarea = f.read()
                    f.close()
                    response = make_response(textarea)
                    response.headers['Content-Type'] = 'text/plain'
                    return response
            else:
                image_data = open(f'tmp/{file}', "rb").read()
                response = make_response(image_data)
                response.headers['Content-Type'] = 'image/png'
                return response

#show txt
@app.route('/tmp/<path:file>', methods=['GET'])
def show_text(file):
    if request.method == 'GET':
        if not file is None:
            text_data = open(f'test_result/test_images/{file}', "rb").read()
            with open(os.path.join(APP_STATIC_TXT, 'text/html'), encoding='utf-8') as f:
                textarea = f.read()
            response = make_response("text/html", 200)
            response.headers['Content-Type'] = 'image/png'
            return response

if __name__ == '__main__':
    files = [
        'test_images', 'test_result/test_images','tmp/test_images'
    ]
    for ff in files:
        if not os.path.exists(ff):
            os.makedirs(ff)
    app.run(host='127.0.0.1', port=5003, debug=True)
