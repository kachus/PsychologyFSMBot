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


class Client(Document):
    telegram_id = IntField(required=True)
    name = StringField()
    date_of_first_using = DateTimeField(required=True)
    date_of_last_visiting = DateTimeField()
    beliefs = ListField()

    meta = {
        'collection': 'Clients'  # Здесь указывается имя коллекции
    }


class Problem(Document):
    belief = StringField()
    category_ru = StringField()
    category_id = StringField()
    sex = StringField()

    meta = {
        'collection': 'Problems'  # Здесь указывается имя коллекции
    }
