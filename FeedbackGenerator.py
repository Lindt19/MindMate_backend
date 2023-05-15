

def written_polarity(polarity):
    result = ""
    if -1.0 <= polarity <= -0.6:
        result = "The body is written in a very negative way. It seems that you had a very bad experience, so try to think about how you would improve that in the future."
    if -0.6 < polarity <= -0.2:
        result = "The body is written in a negative way. It seems that your text contains some negative terms and is therefore placed in this section, so try to think about how you would improve this kind of experience in the future."
    if -0.2 < polarity <= 0.2:
        result = "The body is written in a neutral way. There are no extremes in terms of positivity or negativity. This is maybe a sign that you didn't express enough sentiments/feelings in your analysis."
    if 0.2 < polarity <= 0.6:
        result = "The body is written in a positive way. It seems that your text contains some positive terms and is therefore classified in this area, which is a sign that you had a good experience. So, try to think about the factors that lead to this."
    if 0.6 < polarity <= 1.0:
        result = "The body is written in a very positive way. It seems as if your text contains many positive terms and is therefore placed in this section, which is a sign that you had a good experience. So, try to think about the factors that lead to this."
    return result

def written_subjectivity(subjectivity):
    result = ""
    if 0.0 <= subjectivity <= 0.2:
        result = "The introduction is written very objectively. This means that you have written a text that contains almost no personal opinions. This is a good point since you likely provide include objective elements such as a brief overview of the experience and relevant background information."
    if 0.2 < subjectivity <= 0.4:
        result = "The introduction is written objectively. This means that you have written a text that contains few personal opinions. This is a good point since you likely provide include objective elements such as a brief overview of the experience and relevant background information."
    if 0.4 < subjectivity <= 0.6:
        result = "The introduction contains some subjective elements. This is very good since you likely used elements such as personal anecdotes or feelings about the experience and also objective elements such as a brief overview of the experience and relevant background information."
    if 0.6 < subjectivity <= 0.8:
        result = "The introduction contains some strongly subjective elements, i.e. you have included a certain amount of subjective opinion and less fact-based information in your text. This could be improved by providing more overview of the experience and relevant background information."
    if 0.8 < subjectivity <= 1.0:
        result = "The introduction contains a lot of subjective elements. This means that you have included a lot of subjective opinions in your text and almost no fact-based information. This could be improved by providing more overview of the experience and relevant background information."
    return result

def written_subjectivity_body(subjectivity):
    result = ""
    if 0.0 <= subjectivity <= 0.2:
        result = "The body is written very objectively. This means that you have written a text that contains almost no personal opinions. You should reflect more about the emotions or thoughts that arose during the experience."
    if 0.2 < subjectivity <= 0.4:
        result = "The body is written objectively. This means that you have written a text that contains few personal opinions. You should reflect more about the emotions or thoughts that arose during the experience."
    if 0.4 < subjectivity <= 0.6:
        result = "The body contains some subjective elements. This means that you have written a text that contains some personal opinions but also some factual information. This is good since you likely describe the experience in detail, including any emotions or thoughts that arose and also external factors that may have influenced the experience."
    if 0.6 < subjectivity <= 0.8:
        result = "The body contains some strongly subjective elements, i.e. you have included a certain amount of subjective opinion and less fact-based information in your text. You should reflect more about the external factors that may have influenced the experience."
    if 0.8 < subjectivity <= 1.0:
        result = "The body contains a lot of subjective elements. This means that you have included a lot of subjective opinions in your text and almost no fact-based information. You should reflect more about the external factors that may have influenced the experience."
    return result

def written_tenses_pronouns(pronouns, past_intro, future_conclusion):
    result = ""
    if pronouns < 3:
        result += "You didn't use many first-person pronouns in your text. This may show a lack of self-reflection and description of how the experience impacted you. I suggest you center the essay more on yourself next time."
    else:
        result += "It seems that you use self-centered sentences quite often. This is a sign of good self-reflection 👍."
    if past_intro < 3:
        result += "You should use more of the past tense in the introduction. This shows the context description of the experience you had."
    else:
        result += "It seems that you described the context of the past experience in the introduction."
    if future_conclusion == 0:
        result += "You should use more of the future tense in the conclusion. This shows how you project yourself in future experiences."
    else:
        result += "It seems that you mentioned how to improve future experiences 👍."

    return result

def written_pronouns(pronouns):
    result = ""
    if pronouns < 3:
        result += "You didn't use many first-person pronouns in your text. This may show a lack of self-reflection and description of how the experience impacted you. I suggest you center the essay more on yourself next time."
    else:
        result += "It seems that you use self-centered sentences quite often. This is a sign of good self-reflection 👍."

    return result

def written_tense_past(past_intro):
    result = ""
    if past_intro < 3:
        result += "You should use more of the past tense in the introduction. This shows the context description of the experience you had."
    else:
        result += "It seems that you described the context of the past experience in the introduction."

    return result

def written_tense_future(future_conclusion):
    result = ""
    if future_conclusion == 0:
        result += "You should use more of the future tense in the conclusion. This shows how you project yourself in future experiences."
    else:
        result += "It seems that you mentioned how to improve future experiences 👍."

    return result

def generate_feedback(subjectivity_intro, subjectivity_body, polarity_body, polarity_conclusion, pronouns, past_intro, future_conclusion):
    result = ""
    result += written_polarity(polarity_body)
    result += written_subjectivity(subjectivity_intro)
    #result += written_subjectivity_body(subjectivity_body)
    result += written_tenses_pronouns(pronouns, past_intro, future_conclusion)
    return result