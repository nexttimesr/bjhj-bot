from flask import Flask, render_template
from bot import run
app = Flask(__name__)

run()

@app.route('/')
def index():
    return render_template('index.html')


if __name__ == '__main__':
    app.run()
