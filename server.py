from flask import Flask, render_template, request, redirect
import os
import json
import uuid
from subprocess import Popen, PIPE

UPLOAD_FOLDER = 'upload'
ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'])

app = Flask(__name__)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['SECRET_KEY'] = "xxx"

@app.route("/success")
def success():        
    filename = request.args.get("filename")
    process = Popen(["python", "tensorflow_chessbot.py", "--filepath", "../upload/"+filename], cwd="chessfenbot", stdout=PIPE, stderr=PIPE)
    (output, err) = process.communicate()
    exit_code = process.wait()
    errf = err.decode("utf-8")
    err = "exit code:\n\n{}\n\nerr:\n\n{}".format(exit_code, errf)
    content = output.decode("utf-8")        
    parts = content.split("Predicted FEN: ")    
    if len(parts) == 1:        
        return render_template("fenbotfailed.html", err = err, content = content)
    else:        
        fen = parts[1].split("\n")[0]        
        fen = fen.replace("\r", "")
        fen = fen.replace("\n", "")
        print("detected fen", fen)                
        url = "https://lichess.org/analysis/standard/"+fen
        print("url", url)
        return redirect(url)        

@app.route("/", methods=['GET', 'POST'])
def index():    
    #return render_template("index.html", content = "fenbot")        
    if request.method == 'POST':            
        print("request files", request.files.getlist("files[]"))                
        for file in request.files.getlist("files[]"):
            if len(file.filename) > 0:
                print("found", file.filename)                
                parts = file.filename.split(".")       
                ext = parts[-1]         
                filename = uuid.uuid1().hex + "." + ext
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))            
                return json.dumps({
                    "success":True,
                    "url":"/success?filename="+filename
                })
        return json.dumps({
            "success":False,
            "error":"no file"
        })
    else:
        useragent = request.headers.get("User-Agent", "unknown")
        print("user agent", useragent)
        if "Chrome/" in useragent:
            print("normal")
            if not ( request.args.get("manual", None) is None ):
                return render_template("upload_manual.html")    
            return render_template("upload_auto.html")
        else:
            print("fallback")
            return render_template("index.html")
