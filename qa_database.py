
class Question:
    def __init__(self, title, answers=None):
        if answers is None:
            answers = []
        self.title = title
        self.answers = answers


