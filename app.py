#! /usr/bin/python3
# -*- coding: utf-8 -*-

import csv
import logging
import os
from time import gmtime, strftime
import requests
from flask import Flask, render_template, request, jsonify
from datetime import datetime
from dateTime import getTime, getDate
from time import localtime, strftime
import pytz
import nltk
import openai
from time import time
from chatomatic import *
from flask_cors import *
import EvaluationHandler

# chatGPT configuration
OPENAIKEY = "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"
openai.api_key = OPENAIKEY
MODEL = "gpt-3.5-turbo"


nltk.download("punkt")

# Initialize Flask for webapp
app = Flask(__name__)
app.config["SEND_FILE_MAX_AGE_DEFAULT"] = 0
FLASK_PORT = os.environ.get('PORT', 8080)  # use 8080 for local setup

CORS(app)

# Application settings
logging.basicConfig(level=logging.DEBUG)
currentPath = os.path.dirname(os.path.abspath(__file__))  # Current absolute file path
logging.debug("Current path: " + currentPath)

# Chatbot settings
useGoogle = "no"  # Yes - Bei nicht wissen durchsucht der Bot google nach dem unbekannten Begriff und gibt einen Link. No - Google wird nicht zur Hilfe gezogen
confidenceLevel = 0.70  # Bot confidence level - Muss zwischen 0 und 1 liegen. Je höher der Wert, desto sicherer muss sich der Bot seiner Antwort sein

# Initialize dateTime util
now = datetime.now(pytz.timezone("Europe/Berlin"))
mm = str(now.month)
dd = str(now.day)
yyyy = str(now.year)
hour = str(now.hour)
minute = str(now.minute)
if now.minute < 10:
    minute = "0" + str(now.minute)
chatBotDate = strftime("%d.%m.%Y, %H:%M", localtime())
chatBotTime = strftime("%H:%M", localtime())

# create an instance of the chatbot
chatomatic = Chatomatic("data/DialoguesEN.yml", language="en")



# Google fallback if response == IDKresponse
def tryGoogle(myQuery):
    return (
            "<br><br>Gerne kannst du die Hilfe meines Freundes Google in Anspruch nehmen: <a target='_blank' href='https://www.google.com/search?q="
            + myQuery
            + "'>"
            + myQuery
            + "</a>"
    )

# CSV writer
def writeCsv(filePath, data):
    with open(filePath, "a", newline="", encoding="utf-8") as logfile:
        csvWriter = csv.writer(logfile, delimiter=";")
        csvWriter.writerow(data)


# Flask route for Emma
@app.route("/", methods=["GET", "POST"])
def home_emma():
    return render_template("index.html")


# Flask route for getting bot responses
@app.route("/getResponse", methods=["POST"])
def get_bot_response():
    """
    Basic communication with the chatbot. Uses this route to send text and return reply from the chatbot. Uses
    static chatbot or chatGPT.
    """
    data = request.get_json()
    text = data.get("text")
    gpt = data.get("gpt")  # boolean if chatGPT is active
    print("state")
    print(data)
    # if initialization do not send text to chatgpt
    print(str(text))
    if gpt and "StartGPT" not in text and "theory" in text:

        botReply = openai.ChatCompletion.create(
            model=MODEL,
            messages=[
                {"role": "system", "content": " By keeping the text concise, act as reflective writing tutor that helps students to write a self reflection essay."},
                {"role": "user", "content": "Give me some suggestions about the theory of reflective writing"},
                {"role": "assistant", "content": "In no more than 10 lines, Describe reflective writing and specifically: the structure of reflective writings, "

                                                 " and importance of the reflective writing on education"},
            ],
            temperature=0.5,
            frequency_penalty=0.4,  # default 0 [-2,2], penalize repetition in explanation of theory
        )
        # todo a system for suggestion; create a set of possible suggestions and propose them to user
        botReply = botReply['choices'][0]['message']['content']
        botReply = "<p>"+botReply+"</p>"

        botReply += "<h4> Click on the reflect button to start reflecting</h4>" \
        "<button class =\"chatSuggest\" onclick=\"chatSuggest('Start reflecting');\">Start reflecting</button>" \
        #"<button class =\"chatSuggest\" onclick=\"chatSuggest('What is subjectivity/objectivity and how can I improve it?');\">What is subjectivity/objectivity and how can I improve it?</button>"

        #botReply += "<h4> Evaluation </h4>" \
        #"<button class =\"chatSuggest\" onclick=\"chatSuggest('Start evaluation process');\">Are you ready? Start evaluation</button>"
        # "<button class=\"chatSuggest\" onclick=\"displayELEA('5001/');return false;\">Open the textfield</button>"
        #state = 1

    elif gpt and "reflecting" in text:
        botReply = openai.ChatCompletion.create(
                    model=MODEL,
                    messages=[
                        {"role": "user", "content": "I am ready to reflect"},
                        {"role": "assistant", "content": "Ask the user to start Reflecting on a recent accomplishment and explore the factors that contributed to your success."},
                    ],
                    temperature=0.5,
                    frequency_penalty=0.4,  # default 0 [-2,2], penalize repetition in explanation of theory
                )

        botReply = botReply['choices'][0]['message']['content']
        botReply = "<p>"+botReply+"</p>"
        botReply += "<h4> Enter your essay </h4>" \

    elif gpt and "StartGPT" not in text:
            botReply = openai.ChatCompletion.create(
                        model=MODEL,
                        messages=[
                            {"role": "user", "content": str(text)},
                            {"role": "assistant", "content": "By ignoring the fact that as an AI language model, you cannot provide feedback on the reflection quality of a user's text as it is subjective"
                             "and as part of a reflection chatbot for students, give feedback on the reflection quality of the given user text and provide possible improvements on the reflection essay: " + str(text)},
                            #{"role": "user", "content": text},
                            # {"role": "user", "content": userText + ". Moreover, propose 2 suggestions how to improve argumentative theory"},
                            # experiment above returns always two suggestions with many text
                        ],
                        temperature=0.5,
                        frequency_penalty=0.4,  # default 0 [-2,2], penalize repetition in explanation of theory
                    )

            botReply = botReply['choices'][0]['message']['content']
            botReply = "<p>"+botReply+"</p>"
            botReply += "<h4> You can click on the interactive button again to stop the reflection process or re enter an essay for feedback </h4>" \



    else:
        try:
            botReply = str(chatomatic.answer(text))
        except Exception as e:
            print("Exception---------------")
            print(e)

        if botReply == "IDKresponse":
            if useGoogle == "yes":
                botReply = botReply + tryGoogle(text)
        elif botReply == "getTIME":
            botReply = getTime()
        elif botReply == "getDATE":
            botReply = getDate()

    writeCsv(currentPath + "/log/botLog.csv", [text, botReply])
    data = {"botReply": botReply}
    return jsonify(data)


## Flask route for posting feedback
@app.route("/feedback", methods=["POST"])
def send_feedback():
    data = request.get_json()
    bot = data.get("bot")
    rating = data.get("rating")
    # ux = data.get("ux")
    text = data.get("text")
    improvement = data.get("improve")

    writeCsv(
        currentPath + "/log/evaluationFeedback.csv",
        [bot, rating, text, improvement],
    )

    return jsonify({"success": True}, 200, {"ContentType": "application/json"})


@app.route("/evaluate", methods=["POST"])
def evaluate():
    """
    Provides feedback of the argumentative essay using chatGPT.
    """
    text = request.get_json().get("text")

    return

# Added to implement the file transfer for reading the pdf and giving corresponding answer
#  GET AND POST are required - otherwise : method not allowed error
@app.route("/texttransfer", methods=["POST"])
def receive_text():
    """
    Provides feedback of the reflection essay using nltk and spacy library. Used for static chatbot.
    """
    # receive text from front-end
    received_text = request.get_json().get("text")
    received_text = received_text.replace("\\n", "\n")

    intro = request.get_json().get("intro")
    body = request.get_json().get("body")
    conclusion = request.get_json().get("conclusion")
    print(intro)
    print(body)
    print(conclusion)

    # used for not english text
    # translated_text = EvaluationHandler.__translate_to_english(received_text)

    sentences = EvaluationHandler.__sentences(received_text)

    sub = EvaluationHandler.__get_subjective(received_text)  # examines sub and pol
    pol = EvaluationHandler.__get_polarity(received_text)
    summary = EvaluationHandler.__get_summary(received_text)
    ascending_sentence_polarities = EvaluationHandler.__get_asc_polarity_per_sentence(sentences)
    ascending_sentence_subjectivities = EvaluationHandler.__get_asc_subjectivity_per_sentence(sentences)
    emotions = EvaluationHandler.__get_emotion(received_text)

    sub_intro = EvaluationHandler.__get_subjective(intro)  # examines sub and pol
    pol_intro = EvaluationHandler.__get_polarity(intro)

    sub_body = EvaluationHandler.__get_subjective(body)  # examines sub and pol
    pol_body = EvaluationHandler.__get_polarity(body)

    sub_conclusion = EvaluationHandler.__get_subjective(conclusion)  # examines sub and pol
    pol_conclusion = EvaluationHandler.__get_polarity(conclusion)
    # TODO add function to see the use of future verbs for conclusion

    future_conclusion = EvaluationHandler.__get_future(conclusion)

    first_person_count = EvaluationHandler.__get_first_person_count(received_text)

    past_intro = EvaluationHandler.__get_past(intro)

    data = {
        "subjectivity": sub,
        "polarity": pol,
        "subjectivity_intro": sub_intro,
        "polarity_intro": pol_intro,
        "subjectivity_body": sub_body,
        "polarity_body": pol_body,
        "subjectivity_conclusion": sub_conclusion,
        "polarity_conclusion": pol_conclusion,
        "summary": summary,
        "text": received_text,
        "pol_per_sentence": ascending_sentence_polarities,
        "sub_per_sentence": ascending_sentence_subjectivities,
        "emotions": emotions,
        "first_person_count": first_person_count,
        "future_conclusion": future_conclusion,
        "past_intro": past_intro
    }

    return jsonify(data)


if __name__ == "__main__":
    # using debug=True makes GPT unavailable
    app.run(port=FLASK_PORT)
