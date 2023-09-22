from mongoengine import Document, IntField, StringField, DateTimeField, ListField


class Psycologyst(Document):
    telegram_id = IntField(required=True)
    name = StringField()
    date_of_first_using = DateTimeField(required=True)
    last_visit = DateTimeField()

    meta = {
        'collection': 'Psycologyst'  # Здесь указывается имя коллекции
    }


class Client(Document):
    telegram_id = IntField(required=True)
    name = StringField()
    date_of_first_using = DateTimeField(required=True)
    date_of_last_visiting= DateTimeField()
    conversation = ListField()

    meta = {
        'collection': 'Client' # Здесь указывается имя коллекции
    }
