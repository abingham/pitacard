class Profile:
    RANDOM_METHOD = 0
    LEITNER_METHOD = 1

    FORWARD_MODE = 0
    REVERSE_MODE = 1
    RANDOM_MODE  = 2

    def __init__(self):
        self.selection_method = Profile.LEITNER_METHOD
        self.sandbox = False
        self.render_html = False
        self.review_mode = Profile.FORWARD_MODE
