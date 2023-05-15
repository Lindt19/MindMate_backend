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
from FeedbackGenerator import *

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
currentPath = os.path.dirname(os.path.abspath(__file__))  # Current absolute file path$
subfolders = [ f.path for f in os.scandir(currentPath) if f.is_dir() ]
logging.debug("Subfolders: " + str(subfolders))

logging.debug("Content of /data: " + str([ f.path for f in os.scandir(f"{currentPath}/data")]))

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
chatomatic = Chatomatic(f"{currentPath}/data/DialoguesEn.yml", language="en")

state = 0
intro = " "
body = " "
conclusion = " "

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


def get_feedback(text):
    sub = EvaluationHandler.__get_subjective(text)  # examines sub and pol
    pol = EvaluationHandler.__get_polarity(text)
    future_conclusion = EvaluationHandler.__get_future(text)
    first_person_count = EvaluationHandler.__get_first_person_count(text)
    past_intro = EvaluationHandler.__get_past(text)

    feedback = generate_feedback(sub, sub, pol, pol, first_person_count, past_intro, future_conclusion)

    return feedback

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
    global state  # Declare the variable as global
    global intro
    global body
    global conclusion

    if("Introduction" in text):
        state = 0
    print(state)

    if("chat" in text):
        botReply = "<p>You are now using the interactive reflection version. It consists of a normal conversation where I will ask you questions to guide your reflection and provide feedback accordingly.</p>" \
                        "<p>I can also provide guidelines on how to write reflective texts. Whenever you feel ready, you can click on the 'start reflecting' button bellow. You will have the chance to send me with your own text so that I can" \
                        "provide feedback and improvements &#128521; .</p>" \
                        "<h4> Get some theory </h4>" \
                           "<button class=\"chatSuggest\" onclick=\"chatSuggest('Get some theory');\">Get some theory</button>" \
                        "<h4> Start reflecting </h4>" \
                            "<button class=\"chatSuggest\" onclick=\"chatSuggest('Start reflecting');\">Start reflecting</button>"
        state = 1
    # Context
    elif("start" in text):
        botReply = "<p> Let's go! It's time to embark on a reflective journey and explore a past experience &#128640;</p>" \
                        "<p>Think of a specific event or situation from your life that holds significance to you. It could be an achievement, a challenge, a relationship, or any other experience that had an impact on you." \
                        "As you start reflecting, consider the following prompts to provide context:</p>" \
                        "<p>1. What was the event or situation? Describe it briefly.</p>" \
                        "<p>2. When did it happen? Provide the timeframe or date &#128197;</p>" \
                        "<p>3. Where did it take place? Set the scene and environment &#128506;&#65039;</p>" \
                        "<p>4. Who else was involved? Mention the people or individuals connected to the experience &#128104;</p>" \
                        "<p>Take your time to gather your thoughts and when you're ready, share the details of your experience with me. I'm here to guide your reflection and provide feedback along the way &#128521;</p>"
        state = 2
    # Emotions
    elif(state == 2):
            intro += text + " "
            botReply = "<p> Thank you for providing me with the context. Now it is time to delve into your emotions and share your emotional response.</p>" \
                            "<p>Think back to that specific moment or event. What were the predominant emotions you felt during that time? Did you experience joy, excitement, sadness, anger, fear, or a combination of emotions? Try to identify and describe the emotions that were most prominent to you.</p>" \
                            "<p>Take your time and express your emotions openly. I'm here to listen and provide support throughout your reflective journey &#128519;</p>"
            state = 3
    # Evaluation + Analysis
    elif(state == 3):
            body += text + " "
            botReply = "<p>Now, let's delve deeper into your reflection. Describe what went well during that experience. What aspects or actions contributed to its success? Consider the positive outcomes, achievements, or moments of satisfaction that you can recall.</p>" \
                       "<p>On the other hand, let's also acknowledge the aspects that didn't go as planned or didn't meet your expectations. What were the challenges, obstacles, or areas that could have been improved? Reflect on the factors that hindered the desired outcome or caused frustration.</p>" \
                       "<p>Try also to think about the potential underlying causes and effects of the experience.</p>"
            state = 4

    elif(state == 4):
            body += text + " "
            botReply = "<p>Good! Now consider what new insights, skills, or knowledge you have gained from it. What did you learn about yourself, others, or the situation? Did you discover any strengths or weaknesses?</p>" \
                      "<p>Reflect on the lessons learned and the ways in which this experience has contributed to your personal and professional growth.</p>"

            state = 5

    elif(state == 5):
            body += text + " "
            botReply = "<p>Now, let's take it a step further. Based on what you have learned, think about specific steps you can take to build on this newfound knowledge and skills. How can you apply what you have learned to future endeavors? </p>" \
                      "<p>Consider setting goals or creating an action plan to implement the lessons learned and maximize the benefits of this experience.</p>"

            state = 6

    elif(state == 6):
            conclusion += text + " "
            botReply = "<p>Perfect &#127881; You have successfully reflected in a proper way</p>" \
            "<p> Here is a general feedback on your reflection: </p>"
   # feedback
            sub_into = EvaluationHandler.__get_subjective(intro)
            sub_body = EvaluationHandler.__get_subjective(body)
            pol_body = EvaluationHandler.__get_polarity(body)
            future_conclusion = EvaluationHandler.__get_future(conclusion)
            first_person_count = EvaluationHandler.__get_first_person_count(body)
            past_intro = EvaluationHandler.__get_past(intro)

            feedback_intro = written_subjectivity(sub_into)
            feedback_intro += " Also, " + written_tense_past(past_intro)
            feedback_body = written_polarity(pol_body)
            feedback_body += written_subjectivity_body(sub_body)
            feedback_conclusion = written_tense_future(future_conclusion)
            feedback_first_person = written_pronouns(first_person_count)

            botReply += "<p>" + feedback_intro + " Regarding the body: " + feedback_body + " For the conclusion, " + feedback_conclusion + " Finally, " + feedback_first_person +"</p>"
            botReply += "<p>Let me know if you want to start again</p>"

            state = 7

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

    #writeCsv(currentPath + "/log/botLog.csv", [text, botReply])
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


    # used for not english text
    # translated_text = EvaluationHandler.__translate_to_english(received_text)

    sentences = EvaluationHandler.__sentences(received_text)

    #sub = EvaluationHandler.__get_subjective(received_text)  # examines sub and pol
    #pol = EvaluationHandler.__get_polarity(received_text)
    summary = EvaluationHandler.__get_summary(received_text)
    #ascending_sentence_polarities = EvaluationHandler.__get_asc_polarity_per_sentence(sentences)
   # ascending_sentence_subjectivities = EvaluationHandler.__get_asc_subjectivity_per_sentence(sentences)
    #emotions = EvaluationHandler.__get_emotion(received_text)

    #sub_intro = EvaluationHandler.__get_subjective(intro)  # examines sub and pol
    #pol_intro = EvaluationHandler.__get_polarity(intro)

   # sub_body = EvaluationHandler.__get_subjective(body)  # examines sub and pol
   # pol_body = EvaluationHandler.__get_polarity(body)

    #sub_conclusion = EvaluationHandler.__get_subjective(conclusion)  # examines sub and pol
   #pol_conclusion = EvaluationHandler.__get_polarity(conclusion)

    #future_conclusion = EvaluationHandler.__get_future(conclusion)

    #first_person_count = EvaluationHandler.__get_first_person_count(received_text)

    #past_intro = EvaluationHandler.__get_past(intro)

    data = {
        "subjectivity": 0,
        "polarity": 0,
        "subjectivity_intro": 0,
        "polarity_intro": 0,
        "subjectivity_body": 0,
        "polarity_body": 0,
        "subjectivity_conclusion": 0,
        "polarity_conclusion": 0,
        "summary": summary,
        "text": received_text,
        "pol_per_sentence": 0,
        "sub_per_sentence": 0,
        "emotions": 0,
        "first_person_count": 0,
        "future_conclusion": 0,
        "past_intro": 0
    }

    return jsonify(data)


if __name__ == "__main__":
    # using debug=True makes GPT unavailable
    app.run(host="0.0.0.0", port=int(FLASK_PORT))
