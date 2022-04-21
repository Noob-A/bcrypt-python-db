import logging
import sys
import unittest
from main import *


class LogThisTestCase(type):
    def __new__(cls, name, bases, dct):
        # if the TestCase already provides setUp, wrap it
        if 'setUp' in dct:
            setUp = dct['setUp']
        else:
            setUp = lambda self: None
            print("creating setUp...")

        def wrappedSetUp(self):
            # for hdlr in self.logger.handlers:
            #    self.logger.removeHandler(hdlr)
            self.hdlr = logging.StreamHandler(sys.stdout)
            self.logger.addHandler(self.hdlr)
            setUp(self)

        dct['setUp'] = wrappedSetUp

        # same for tearDown
        if 'tearDown' in dct:
            tearDown = dct['tearDown']
        else:
            tearDown = lambda self: None

        def wrappedTearDown(self):
            tearDown(self)
            self.logger.removeHandler(self.hdlr)

        dct['tearDown'] = wrappedTearDown

        # return the class instance with the replaced setUp/tearDown
        return type.__new__(cls, name, bases, dct)


class LoggedTestCase(unittest.TestCase):
    __metaclass__ = LogThisTestCase
    logger = logging.getLogger("unittestLogger")
    logger.setLevel(logging.INFO)  # or whatever you prefer


class MyTestCase(LoggedTestCase):
    def test_exception(self):
        pdb = PasswordDB('pass.db', 12)
        try:
            pdb.create(overwrite=False)
            self.fail("No error of existing DB")
        except DBAlreadyExistsException:
            pass

    def test_works(self):
        pdb = PasswordDB('pass.db', 12)
        try:
            pdb.create(overwrite=True)
        except DBAlreadyExistsException:
            self.fail("File wasn't deleted")

    def test_validation_true(self):
        pdb = PasswordDB('pass.db', 16)
        pdb.create(overwrite=True)
        pdb.add('admin', '1234')
        pdb.add('admin', '1234adsads')
        pdb.add('admin2', '1234')
        self.assertTrue(pdb.check_password('admin', '1234'))
        self.assertFalse(pdb.check_password('admin', '12fsd34'))


if __name__ == '__main__':
    unittest.main()
