#Объекты для MongoORM
#___________________________________

from mongoengine import Document, IntField, StringField, DateTimeField, ListField, ReferenceField


class Psychologist(Document):
    telegram_id = IntField(required=True)
    name = StringField()
    date_of_first_using = DateTimeField(required=True)
    last_visit = DateTimeField()

    meta = {
        'collection': 'Psycologysts'  # Здесь указывается имя коллекции
    }


class Answer(Document):
    question = StringField()
    scenario = StringField()
    answer_date = DateTimeField
    client_answer = StringField()

meta = {
        'collection': 'ClientAnswers'  # Здесь указывается имя коллекции
    }

class Client(Document):
    telegram_id = IntField(required=True)
    name = StringField()
    date_of_first_using = DateTimeField(required=True)
    date_of_last_visiting = DateTimeField()
    answers = ListField(ReferenceField(Answer))  # Список с объектами Answers

    meta = {
        'collection': 'Clients'  # Здесь указывается имя коллекции
    }
