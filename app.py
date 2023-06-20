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
chatomatic = Chatomatic(f"{currentPath}/data/DialoguesDe.yml", language="de")

states = {}
state = 0

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

    uuid = data.get("uuid")
    print(uuid)

    if uuid not in states:
        states[uuid] = {
            "state": 0,
            "context": "",
            "emotions": "",
            "analysis": "",
            "evaluation": "",
            "plan": "",
            "text": ""
        }

    session_state = states[uuid]
    state = session_state["state"]

    if("Introduction" in text):
        session_state["state"] = 0
    print(session_state["state"])

#  This is the english version
#    """  if("chat" in text):
#         botReply = "<p>You are now using the interactive reflection version. It consists of a normal conversation where I will ask you questions to guide your reflection and provide feedback accordingly.</p>" \
#                         "<p>I can also provide guidelines on how to write reflective texts. Whenever you feel ready, you can click on the 'start reflecting' button bellow. You will have the chance to send me with your own text so that I can" \
#                         "provide feedback and improvements &#128521; .</p>" \
#                         "<h4> Get some theory </h4>" \
#                            "<button class=\"chatSuggest\" onclick=\"chatSuggest('Get some theory');\">Get some theory</button>" \
#                         "<h4> Start reflecting </h4>" \
#                             "<button class=\"chatSuggest\" onclick=\"chatSuggest('Start reflecting');\">Start reflecting</button>"
#         session_state["state"] = 1
#     # Context
#     elif("beginnen" in text):
#         botReply = "<p> Let's go! It's time to embark on a reflective journey and explore a past experience &#128640;</p>" \
#                         "<p>Think of a specific event or situation from your life that holds significance to you. It could be an achievement, a challenge, a relationship, or any other experience that had an impact on you." \
#                         "As you start reflecting, consider the following prompts to provide context:</p>" \
#                         "<p>1. What was the event or situation? Describe it briefly.</p>" \
#                         "<p>2. When did it happen? Provide the timeframe or date &#128197;</p>" \
#                         "<p>3. Where did it take place? Set the scene and environment &#128506;&#65039;</p>" \
#                         "<p>4. Who else was involved? Mention the people or individuals connected to the experience &#128104;</p>" \
#                         "<p>Take your time to gather your thoughts and when you're ready, share the details of your experience with me. I'm here to guide your reflection and provide feedback along the way &#128521;</p>"
#         session_state["state"] = 2
#     # Emotions
#     elif(session_state["state"] == 2):
#             session_state["context"] += text + " "
#             session_state["text"] += text + " "
#             botReply = "<p> Thank you for providing me with the context. Now it is time to delve into your emotions and share your emotional response.</p>" \
#                             "<p>Think back to that specific moment or event. What were the predominant emotions you felt during that time? Did you experience joy, excitement, sadness, anger, fear, or a combination of emotions? Try to identify and describe the emotions that were most prominent to you.</p>" \
#                             "<p>Take your time and express your emotions openly. I'm here to listen and provide support throughout your reflective journey &#128519;</p>"
#             session_state["state"] = 3
#     # Evaluation + Analysis
#     elif(session_state["state"] == 3):
#             session_state["emotions"] += text + " "
#             session_state["text"] += text + " "
#
#             botReply = "<p>Now, let's delve deeper into your reflection. Describe what went well during that experience. What aspects or actions contributed to its success? Consider the positive outcomes, achievements, or moments of satisfaction that you can recall.</p>" \
#                        "<p>On the other hand, let's also acknowledge the aspects that didn't go as planned or didn't meet your expectations. What were the challenges, obstacles, or areas that could have been improved? Reflect on the factors that hindered the desired outcome or caused frustration.</p>" \
#                        "<p>Try also to think about the potential underlying causes and effects of the experience.</p>"
#             session_state["state"] = 4
#
#     elif(session_state["state"] == 4):
#             session_state["analysis"] += text + " "
#             session_state["text"] += text + " "
#
#             botReply = "<p>Good! Now consider what new insights, skills, or knowledge you have gained from it. What did you learn about yourself, others, or the situation? Did you discover any strengths or weaknesses?</p>" \
#                       "<p>Reflect on the lessons learned and the ways in which this experience has contributed to your personal and professional growth.</p>"
#
#             session_state["state"] = 5
#
#     elif(session_state["state"] == 5):
#             session_state["evaluation"] += text + " "
#             session_state["text"] += text + " "
#
#             botReply = "<p>Now, let's take it a step further. Based on what you have learned, think about specific steps you can take to build on this newfound knowledge and skills. How can you apply what you have learned to future endeavors? </p>" \
#                       "<p>Consider setting goals or creating an action plan to implement the lessons learned and maximize the benefits of this experience.</p>"
#
#             session_state["state"] = 6
#
#     elif(session_state["state"] == 6):
#             session_state["plan"] += text + " "
#             session_state["text"] += text + " "
#
#             botReply = "<p>Perfect &#127881; You have successfully reflected in a proper way</p>" \
#             "<p> Here is a general feedback on your reflection: </p>"
#             botReply += "<p>Let me know if you want to start again</p>"
#
#             session_state["state"] = 7
#    """
# This is the german version
    if("chat" in text):
        botReply = "<p>You are now using the interactive reflection version. It consists of a normal conversation where I will ask you questions to guide your reflection and provide feedback accordingly.</p>" \
                           "<p>I can also provide guidelines on how to write reflective texts. Whenever you feel ready, you can click on the 'start reflecting' button bellow. You will have the chance to send me with your own text so that I can" \
                           "provide feedback and improvements &#128521; .</p>" \
                           "<h4> Get some theory </h4>" \
                              "<button class=\"chatSuggest\" onclick=\"chatSuggest('Get some theory');\">Get some theory</button>" \
                           "<h4> Start reflecting </h4>" \
                               "<button class=\"chatSuggest\" onclick=\"chatSuggest('Start reflecting');\">Start reflecting</button>"
        session_state["state"] = 1
       # Context
    elif("beginnen" in text):
        botReply = "<p> Los geht's! Es ist an der Zeit, sich auf eine nachdenkliche Reise zu begeben und eine vergangene Erfahrung zu erkunden &#128640;</p>" \
                           "<p> Beschreiben Sie eine neue berufliche Situation wie Sie sie im Praxisalltag erlebt haben (bitte wählen Sie keine Situation die Sie zuvor bereits in einem Portfolio reflektiert haben).</p>" \
                           "<p> Bitte investieren Sie maximal 20 min ins Beschreibung und maximal 20 min ins Reflektieren. </p>"\
                           "<p> Wenn Sie mit dem Nachdenken beginnen, sollten Sie die folgenden Hinweise beachten, um den Kontext zu verdeutlichen:</p>" \
                           "<p>1. Was war die Situation? Beschreiben Sie sie kurz.</p>" \
                           "<p>2. Wann ist es passiert? Geben Sie den Zeitrahmen oder das Datum an &#128197;</p>" \
                           "<p>3. Wo hat sie stattgefunden? Den Schauplatz festlegen  &#128506;&#65039;</p>" \
                           "<p>4. Wer war noch beteiligt? Nennen Sie die Menschen oder Personen, die mit dem Erlebnis verbunden sind &#128104;</p>" \
                           "<p>Nehmen Sie sich Zeit, um Ihre Gedanken zu sammeln, und wenn Sie so weit sind, teilen Sie mir die Einzelheiten Ihrer Erfahrungen mit. Ich bin hier, um Sie bei Ihren Überlegungen zu unterstützen und Ihnen Feedback zu geben. &#128521;</p>"
        session_state["state"] = 2
       # Emotions
    elif(session_state["state"] == 2):
        session_state["context"] += text + " "
        session_state["text"] += text + " "
        botReply = "<p> Danke, dass Sie mir den Kontext geliefert haben. Jetzt ist es an der Zeit, in Ihre Gefühle einzutauchen und Ihre emotionale Reaktion mitzuteilen.</p>" \
                               "<p>Denken Sie an diesen speziellen Moment oder dieses Ereignis zurück. Was waren die vorherrschenden Gefühle, die Sie in dieser Zeit empfunden haben? Versuchen Sie, diese Gefühle zu identifizieren und zu beschreiben &#128519;</p>"
        session_state["state"] = 3
       # Evaluation + Analysis
    elif(session_state["state"] == 3):
        session_state["emotions"] += text + " "
        session_state["text"] += text + " "

        botReply = "<p>Lassen Sie uns nun tiefer in Ihre Überlegungen eintauchen. Beschreiben Sie, was während dieser Erfahrung gut gelaufen ist. Welche Aspekte oder Handlungen trugen zum Erfolg bei? </p>" \
                          "<p>Andererseits sollten wir auch die Aspekte berücksichtigen, die nicht wie geplant gelaufen sind oder nicht Ihren Erwartungen entsprochen haben.</p>" \
                          "<p>Versuchen Sie auch, über die möglichen Ursachen und Auswirkungen der Erfahrung nachzudenken.</p>"
        session_state["state"] = 4

    elif(session_state["state"] == 4):
        session_state["analysis"] += text + " "
        session_state["text"] += text + " "

        botReply = "<p>Gut! Überlegen Sie nun, welche neuen Einsichten, Fähigkeiten oder Kenntnisse Sie daraus gewonnen haben. Was haben Sie über sich selbst, andere oder die Situation gelernt? </p>" \

        session_state["state"] = 5

    elif(session_state["state"] == 5):
        session_state["evaluation"] += text + " "
        session_state["text"] += text + " "

        botReply = "<p>Lassen Sie uns nun einen Schritt weiter gehen. Wie können Sie das, was Sie gelernt haben, in Zukunft anwenden? </p>" \
                         "<p>Erwägen Sie, sich Ziele zu setzen oder einen Aktionsplan zu erstellen, um die gewonnenen Erkenntnisse umzusetzen.</p>"

        session_state["state"] = 6

    elif(session_state["state"] == 6):
        session_state["plan"] += text + " "
        session_state["text"] += text + " "

        botReply = "<p>Perfekt &#127881; Sie haben erfolgreich reflektier! </p>" \
               "<p>Um ein allgemeines Feedback zu Ihrer Reflexion zu erhalten, klicken Sie auf den Button 'Insights', der oben in der Leiste erschienen ist. Oder den Button 'Feedback', die oberhalb erscheint.</p>"
        botReply += "<p>Wenn Sie neu beginnen möchten, können Sie die Seite aktualisieren.</p>"
        botReply += "<h4> Feedback </h4>" \
                            "<button class=\"chatSuggest\" onclick=\"displayFeedback();return false;\">Feedback</button>"

        session_state["state"] = 7


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

    # Disable Logging
    #writeCsv(currentPath + "/log/botLog.csv", [text, botReply])
    data = {
    "botReply": botReply,
    "state": session_state["state"]
    }
    return jsonify(data)


## Flask route for posting feedback
@app.route("/feedback", methods=["POST"])
def send_feedback():
    data = request.get_json()
    bot = data.get("bot")
    rating = data.get("rating")
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
    Provides feedback of the reflection essay.
    """
    data = request.get_json()
    uuid = data.get("uuid")
    print(uuid)

    if uuid not in states:
        states[uuid] = {
                "state": 0,
                "context": "",
                "emotions": "",
                "analysis": "",
                "evaluation": "",
                "plan": "",
                "text": ""
            }


    session_state = states[uuid]
    # used for not english text
    translated_text = EvaluationHandler.__translate_to_english(session_state["text"])
    # Context
    context =  session_state["context"]
    translated_context = EvaluationHandler.__translate_to_english(session_state["text"])
    context_past_tense = EvaluationHandler.__get_past(translated_context)
    context_presence_of_named_entity = EvaluationHandler.__get_named_entities(translated_context)
    # Emotions
    translated_emotions = EvaluationHandler.__translate_to_english(session_state["emotions"])
    emotions = EvaluationHandler.__get_emotion(translated_emotions)
    # Analysis
    analysis = session_state["analysis"]
    translated_analysis = EvaluationHandler.__translate_to_english(analysis)
    analysis_polarity = EvaluationHandler.__get_polarity(translated_analysis)
    analysis_subjectivity = EvaluationHandler.__get_subjective(translated_analysis)
    analysis_causal_keywords = EvaluationHandler.__get_causal_keywords(translated_analysis)
    # Evaluation
    evaluation = session_state["evaluation"]
    translated_evaluation = EvaluationHandler.__translate_to_english(evaluation)
    evaluation_polarity = EvaluationHandler.__get_polarity(translated_evaluation)
    evaluation_subjectivity = EvaluationHandler.__get_subjective(translated_evaluation)
    # Plan
    translated_plan = EvaluationHandler.__translate_to_english( session_state["plan"])
    plan_future_tense = EvaluationHandler.__get_future(translated_plan)

    data = {
                "context_past_tense": context_past_tense,
                "context_presence_of_named_entity": context_presence_of_named_entity,
                "emotions": emotions,
                "analysis_polarity": analysis_polarity,
                "analysis_subjectivity": analysis_subjectivity,
                "analysis_causal_keywords": analysis_causal_keywords,
                "evaluation_polarity": evaluation_polarity,
                "evaluation_subjectivity": evaluation_subjectivity,
                "plan_future_tense": plan_future_tense,
                "text": session_state["text"],
                "first_person_count": 0
            }

    return jsonify(data)


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

    context = request.get_json().get("context")
    emotions = request.get_json().get("emotions")
    analysis = request.get_json().get("analysis")
    evaluation = request.get_json().get("evaluation")
    plan = request.get_json().get("plan")


    # used for not english text
    translated_text = EvaluationHandler.__translate_to_english(received_text)
    print(translated_text)

    # Context
    context_past_tense = EvaluationHandler.__get_past(context)
    context_presence_of_named_entity = EvaluationHandler.__get_named_entities(context)
    # Emotions
    emotions = EvaluationHandler.__get_emotion(received_text)
    # Analysis
    analysis_polarity = EvaluationHandler.__get_polarity(analysis)
    analysis_subjectivity = EvaluationHandler.__get_subjective(analysis)
    analysis_causal_keywords = EvaluationHandler.__get_causal_keywords(analysis)
    # Evaluation
    evaluation_polarity = EvaluationHandler.__get_polarity(evaluation)
    evaluation_subjectivity = EvaluationHandler.__get_subjective(evaluation)
    # Plan
    plan_future_tense = EvaluationHandler.__get_future(plan)

    data = {
        "context_past_tense": context_past_tense,
        "context_presence_of_named_entity": context_presence_of_named_entity,
        "emotions": emotions,
        "analysis_polarity": analysis_polarity,
        "analysis_subjectivity": analysis_subjectivity,
        "analysis_causal_keywords": analysis_causal_keywords,
        "evaluation_polarity": evaluation_polarity,
        "evaluation_subjectivity": evaluation_subjectivity,
        "plan_future_tense": plan_future_tense,
        "text": received_text,
        "first_person_count": 0
    }

    return jsonify(data)


if __name__ == "__main__":
    # using debug=True makes GPT unavailable
    app.run(host="0.0.0.0", port=int(FLASK_PORT))
