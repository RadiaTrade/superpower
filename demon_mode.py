from flask import Flask, request, render_template
from github import Github
import subprocess
import os
import threading

app = Flask(__name__)

GITHUB_TOKEN = "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"
REPO_NAME = "RadiaTrade/superpower"
g = Github(GITHUB_TOKEN)
repo = g.get_repo(REPO_NAME)
SCRIPT_PATH = "/home/brabg11/demon_mode.py"

process = None

def run_script():
    global process
    process = subprocess.Popen(
        ["/home/brabg11/alpaca_env/bin/python3", SCRIPT_PATH],
        stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
    )
    stdout, stderr = process.communicate()
    return stdout, stderr

def get_current_code():
    file = repo.get_contents("demon_mode.py")
    return file.decoded_content.decode()

@app.route("/", methods=["GET", "POST"])
def index():
    global process
    if request.method == "POST":
        new_code = request.form["code"]
        file = repo.get_contents("demon_mode.py")
        repo.update_file(file.path, "AI tweak", new_code, file.sha, branch="main")
        with open(SCRIPT_PATH, "w") as f:
            f.write(new_code)
        if process:
            process.terminate()
        threading.Thread(target=run_script, daemon=True).start()
        return render_template("index.html", code=new_code, output="Started trading!", error="")
    code = get_current_code()
    return render_template("index.html", code=code)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)