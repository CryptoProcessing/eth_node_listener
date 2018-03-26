from flask import Flask
from flask_testing import TestCase


class BaseTestCase(TestCase):
    """ Base Tests """
    TEST_CONFIG_FILE_PATH = '../../config_test.py'

    def create_app(self):
        app = Flask(__name__)
        app.config.from_pyfile(self.TEST_CONFIG_FILE_PATH)
        return app

    def setUp(self):
        self.app = self.create_app()
        
