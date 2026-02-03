from datetime import datetime
from flask import Flask, render_template
from json import loads
from os.path import getmtime

app = Flask(__name__)


@app.route("/")
def index():
    file = open("../../../data.json", "r+")
    data = loads(file.read())
    for family, family_data in data.items():
        for project, project_data in family_data.items():
            data[family][project][0] = sum([int(value) for value in project_data[0]["query"]["linterstats"]["totals"].values()])
    return render_template("index.html", data=data, last_modified=datetime.fromtimestamp(getmtime("../../../data.json")).strftime("%Y-%m-%d %H:%M:%S"))


if __name__ == "__main__":
    app.run(debug=True, port=5500)