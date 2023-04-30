from flask import Flask, render_template, Response, request, json
from flask_cors import CORS
import os
import tempfile
from werkzeug.utils import secure_filename
from firebase_admin import credentials, initialize_app, storage
# Init firebase with your credentials
cred = credentials.Certificate("./fireconfig.json")
initialize_app(cred, {'storageBucket': 'finalproject-back.appspot.com'})

ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'}
UPLOAD_FOLDER = '/uploads'

app = Flask(__name__, template_folder="./templetes")
basedir = os.path.abspath(os.path.dirname(__file__))




app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
CORS(app)


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.before_request
def handle_preflight():
    if request.method == "OPTIONS":
        res = Response()
        res.headers['X-Content-Type-Options'] = '*'
        return res

@app.route("/list")
def list():
    return {"list" :["adim1" , "adim2", "adim3"]}

@app.route('/')
def index():
    return render_template("index.html")


@app.route('/login', methods=["POST", "GET"])
def login():

    if request.method == "GET":
        return render_template("index.html")
    if request.method == "POST":
        name = request.form['name']
        file = request.files['file']
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            #file.save(os.path.join(basedir, app.config['UPLOAD_FOLDER'], filename))
            temp = tempfile.NamedTemporaryFile(delete=False)
            temp.name = filename
            file.save(temp.name)
            bucket = storage.bucket()
            blob = bucket.blob(temp.name)
            blob.upload_from_filename(temp.name)
            blob.make_public()

            print("your file url", blob.public_url)

            # Clean-up temp image
            temp.close()
            os.remove(temp.name)

        data = "Hello  "
        response = app.response_class(
            response=json.dumps(name),
            status=200,
            mimetype='application/json'
        )
        return response


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))
