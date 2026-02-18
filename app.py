from flask import Flask, render_template, request, jsonify
import os
import json
import urllib.request
from datetime import datetime
import pandas as pd
app = Flask(__name__)

SLACK_BOT_TOKEN = os.environ.get('SLACK_BOT_TOKEN')
SLACK_CHANNEL = "datasci-209-2026-spring-sec1"

def post_to_slack(name, quiz, score, total):
    if not SLACK_BOT_TOKEN:
        print("SLACK_BOT_TOKEN not set, skipping Slack notification")
        return False

    quiz_names = {
        "quiz1": "Idiom Matchmaker",
        "quiz2": "Chart Decoder",
        "quiz3": "Temporal Idiom"
    }
    quiz_name = quiz_names.get(quiz, "Unknown Quiz")
    percentage = round((score / total) * 100)

    # Pick emoji based on score
    if percentage == 100:
        emoji = ":star2:"
    elif percentage >= 80:
        emoji = ":tada:"
    elif percentage >= 60:
        emoji = ":thumbsup:"
    else:
        emoji = ":muscle:"

    message = {
        "channel": SLACK_CHANNEL,
        "text": f"{emoji} *{name}* scored *{score}/{total}* ({percentage}%) on *{quiz_name}*"
    }

    try:
        req = urllib.request.Request(
            "https://slack.com/api/chat.postMessage",
            data=json.dumps(message).encode('utf-8'),
            headers={
                'Content-Type': 'application/json',
                'Authorization': f'Bearer {SLACK_BOT_TOKEN}'
            }
        )
        response = urllib.request.urlopen(req)
        result = json.loads(response.read().decode('utf-8'))
        if not result.get('ok'):
            print(f"Slack API error: {result.get('error')}")
            return False
        return True
    except Exception as e:
        print(f"Failed to post to Slack: {e}")
        return False

APP_FOLDER = os.path.dirname(os.path.realpath(__file__))


@app.route('/')
def w209():
    file='about9.jpg'
    return render_template('w209.html',file=file)

@app.route("/map")
def hello():
    return render_template("index.html")

@app.route("/api")
def api():
    return {"x": 2}


@app.route("/getData/<int:year>")
def getData(year):
    # Load the CSV file from the static folder, inside the current path
    revenue = pd.read_csv(os.path.join(APP_FOLDER,"static/data/1_Revenues.csv"))

    if year < 1942 or year > 2008:
        return "Error in the year range"

    filteredRevenue = revenue[revenue['Year4']==year][["Name","Year4", "Total Revenue","Population (000)"]]

    # show the post with the given id, the id is an integer
    return filteredRevenue.to_json(orient='records')


@app.route("/quiz1")
def quiz1():
    return render_template("quiz1_idiom.html")


@app.route("/quiz2")
def quiz2():
    return render_template("quiz2_decoder.html")


@app.route("/quiz3")
def quiz3():
    return render_template("quiz3_temporal.html")


@app.route("/scoreboard")
def scoreboard():
    return render_template("scoreboard.html", quiz1_scores=[], quiz2_scores=[])


@app.route("/submit_score", methods=["POST"])
def submit_score():
    data = request.get_json()
    name = data.get('name', 'Anonymous')
    quiz = data.get('quiz', 'quiz1')
    score = data.get('score', 0)
    total = data.get('total', 0)

    posted = post_to_slack(name, quiz, score, total)
    return jsonify({'status': 'success', 'slack_posted': posted})


if __name__ == '__main__':
    app.run()
