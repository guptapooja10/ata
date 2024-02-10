import firebase_admin
from firebase_admin import credentials


def initialize_firebase_app():
    try:
        cred = credentials.Certificate('anlagentechnik-aschersleben-fd030234653c.json')
        firebase_admin.initialize_app(cred)
    except ValueError:
        pass  # App is already initialized
