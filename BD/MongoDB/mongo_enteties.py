# Объекты для MongoORM
# ___________________________________

from mongoengine import Document, IntField, StringField, DateTimeField, ListField, ReferenceField, DictField


class Psychologist(Document):
    telegram_id = IntField(required=True)
    name = StringField()
    date_of_first_using = DateTimeField(required=True)
    last_visit = DateTimeField()

    meta = {
        'collection': 'Psycologysts'  # Здесь указывается имя коллекции
    }


class Answer(Document):
    scenario = StringField()
    answer_date = DateTimeField()
    client_answers = DictField()


meta = {
    'collection': 'ClientAnswers'  # Здесь указывается имя коллекции
}


class Client(Document):
    telegram_id = IntField(required=True)
    name = StringField()
    date_of_first_using = DateTimeField(required=True)
    date_of_last_visiting = DateTimeField()
    # answers = ListField(Answer)  # Список с объектами Answers
    answers = ListField()  # Список с объектами Answers
    actual_problem = StringField()


    meta = {
        'collection': 'Clients'  # Здесь указывается имя коллекции
    }


class Problem(Document):
    sex = StringField()
    problem = StringField()

    meta = {
        'collection': 'Problems'  # Здесь указывается имя коллекции
    }
