from flask import Flask, request
from flask import render_template
from typing import Tuple, List

from dataloader_iam import Batch
from model import Model
from preprocessor import Preprocessor
from path import Path

from textblob import TextBlob

import cv2
import os

app = Flask(__name__)
UPLOAD_FOLDER = './upload'

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

class FilePaths:
    """Filenames and paths to data."""
    fn_char_list = './model/charList.txt'
    fn_summary = './model/summary.json'
    fn_corpus = './data/corpus.txt'


def get_img_height() -> int:
    """Fixed height for NN."""
    return 32


def get_img_size(line_mode: bool = False) -> Tuple[int, int]:
    """Height is fixed for NN, width is set according to training mode (single words or text lines)."""
    if line_mode:
        return 256, get_img_height()
    return 128, get_img_height()


def char_list_from_file() -> List[str]:
    with open(FilePaths.fn_char_list) as f:
        return list(f.read())

def infer(model: Model, fn_img: Path) -> None:
    """Recognizes text in image provided by file path."""
    img = cv2.imread(fn_img, cv2.IMREAD_GRAYSCALE)
    assert img is not None

    preprocessor = Preprocessor(get_img_size(), dynamic_width=True, padding=16)
    img = preprocessor.process_img(img)

    batch = Batch([img], None, 1)
    recognized, probability = model.infer_batch(batch, True)
    print(f'Recognized: "{recognized[0]}"')
    print(f'Probability: {probability[0]}')
    print("After Sentence checking...")
    corrected_spelling = TextBlob(recognized[0])
    return [recognized[0],corrected_spelling.correct()]

@app.route("/", methods=['GET', 'POST'])
def show_page():
    if request.method == 'POST':
        if 'file1' not in request.files:
            return render_template('index.html',status='there is no file1 in form!',result='',found='')
        file1 = request.files['file1']
        try:
            path = os.path.join(app.config['UPLOAD_FOLDER'], file1.filename)
            file1.save(path)
            model = Model(char_list_from_file(), 0, must_restore=True, dump=False)
            res = infer(model, path)
            return render_template('index.html',status='File Uploaded Successfully',found="Sentence Predicted from Image: {0}".format(res[0]),result="Corrected Sentence after spell checking: {0}".format(res[1]))
        except:
            return render_template('index.html',status='Please Upload the file Properly',found='',result='')
    
    return render_template('index.html',status='Upload a File',result='')
