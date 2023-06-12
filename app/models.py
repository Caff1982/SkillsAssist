from datetime import datetime

from sqlalchemy.sql import func

from app import db

# Weight factor for Exponential Moving Average (EMA) score
EMA_ALPHA = 0.5


class Question(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    question_number = db.Column(db.Integer, nullable=False)
    question_title = db.Column(db.String(255), nullable=False)
    question_html = db.Column(db.Text, nullable=False)
    question_explanation = db.Column(db.Text)
    correct_choice = db.Column(db.Integer, nullable=False)
    topic_id = db.Column(db.Integer, db.ForeignKey('topic.id'), nullable=False)
    topic_name = db.Column(db.String(100), nullable=False)
    # Exponential Moving Average (EMA) score
    ema_score = db.Column(db.Float, index=True, default=0.0, nullable=False)

    def __repr__(self):
        return f'<Question {self.id}>'

    def serialize(self):
        return {
            'id': self.id,
            'question_title': self.question_title,
            'question_html': self.question_html,
            'question_explanation': self.question_explanation,
            'correct_choice': self.correct_choice,
            'topic_name': self.topic_name,
        }

    def update(self, score):
        """
        Update the EMA score of the question based on the correctness
        of the answer and commit to database.
        """
        self.ema_score = EMA_ALPHA * score + (1 - EMA_ALPHA) * self.ema_score
        db.session.commit()


class Topic(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    questions = db.relationship('Question',
                                backref='topic',
                                lazy='dynamic')
    past_performance = db.relationship('PerformanceTracker',
                                       backref='topic',
                                       lazy='dynamic')
    last_seen = db.Column(db.DateTime,
                          default=datetime.utcnow,
                          server_default=func.now())

    def __repr__(self):
        return f'<Topic {self.name}>'

    @staticmethod
    def get_all_topics():
        """
        Return a list of all topics sorted alphabetically.
        """
        return Topic.query.order_by(Topic.name.asc()).all()

    def get_questions(self):
        """
        Return a list of all questions for this topic,
        sorted by their EMA score.
        """
        return self.questions.order_by(Question.ema_score.desc()).all()

    def get_number_of_questions(self):
        """
        Returns the number of cards for this topic.
        """
        return self.questions.count()

    def get_performance(self):
        """
        Returns a list of all past performances for this topic,
        sorted by date.
        """
        return self.past_performance.order_by(PerformanceTracker.date).all()

    @staticmethod
    def get_all_topics_with_performance():
        """
        Returns a list of topics that have associated PerformanceTracker
        objects sorted by date.
        """
        topics = Topic.query.filter(Topic.past_performance.any())
        return topics.order_by(Topic.last_seen.desc()).all()


class PerformanceTracker(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    topic_id = db.Column(db.Integer, db.ForeignKey('topic.id'), nullable=False)
    topic_name = db.Column(db.String(100), nullable=False)
    accuracy = db.Column(db.Float, nullable=False)
    date = db.Column(db.DateTime, default=datetime.now)

    def __repr__(self):
        return f'<{self.data}: PerformanceTracker - {self.name}>'
