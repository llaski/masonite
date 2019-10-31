from src.masonite.request import Request
from src.masonite.view import View
from src.masonite.auth.Csrf import Csrf
from src.masonite.app import App
from src.masonite.middleware import CsrfMiddleware
from src.masonite.exceptions import InvalidCSRFToken
from src.masonite.routes import Get, Route
import unittest
from src.masonite.testing import TestCase, generate_wsgi


class TestCSRFMiddleware(TestCase):

    def setUp(self):
        super().setUp()
        wsgi = generate_wsgi()
        # self.request = Request(wsgi)
        # self.route = Route().load_environ(wsgi)
        # self.view = View(self.container)
        # self.container.bind('Request', self.request)

        self.request = self.container.make('Request')
        self.request.load_environ(wsgi)
        self.routes(only=[
            Get().route('/test/@route', None),
            Get().route('/test/10', None),
        ])


        self.middleware = self.container.resolve(CsrfMiddleware)

    def test_middleware_shares_correct_input(self):
        self.middleware.before()
        self.assertIn('csrf_field', self.container.make('ViewClass')._shared)
        self.assertTrue(self.container.make('ViewClass')._shared['csrf_field'].startswith("<input type='hidden' name='__token' value='"))

    def test_middleware_throws_exception_on_post(self):
        self.request.environ['REQUEST_METHOD'] = 'POST'
        self.request.path = '/'
        self.middleware.exempt = []
        with self.assertRaises(InvalidCSRFToken):
            self.middleware.before()

    def test_middleware_can_accept_param_route(self):
        self.request.environ['REQUEST_METHOD'] = 'POST'
        self.request.path = '/test/1'
        self.middleware.exempt = [
            '/test/@route'
        ]
        self.middleware.before()

    def test_middleware_can_exempt(self):
        self.request.environ['REQUEST_METHOD'] = 'POST'
        self.request.path = '/test/1'
        self.middleware.exempt = [
            '/test/1'
        ]
        self.middleware.before()

    def test_middleware_throws_exeption_on_wrong_route(self):
        self.request.environ['REQUEST_METHOD'] = 'POST'
        self.request.path = '/test/10'
        self.middleware.exempt = [
            '/test/2'
        ]
        with self.assertRaises(InvalidCSRFToken):
            self.middleware.before()

    def test_incoming_token_does_not_throw_exception_with_token(self):
        self.request.environ['REQUEST_METHOD'] = 'POST'
        self.request.request_variables.update({'__token': self.request.get_cookie('csrf_token')})
        self.middleware.exempt = []
        self.middleware.before()

    def test_generates_csrf_token(self):
        self.assertTrue(len(self.middleware.generate_token()) == 30)

    def test_generates_token_every_request(self):
        csrf = CsrfMiddleware
        csrf.every_request = True
        self.middleware = self.container.resolve(csrf)
        token1 = self.middleware.verify_token()
        token2 = self.middleware.verify_token()

        self.assertEqual(len(token1), 30)
        self.assertEqual(len(token2), 30)
        self.assertNotEqual(token1, token2)

    def test_does_not_generate_token_every_request(self):
        csrf = CsrfMiddleware
        csrf.every_request = False
        self.middleware = self.container.resolve(csrf)
        self.middleware.every_request = False
        token1 = self.middleware.verify_token()
        token2 = self.middleware.verify_token()

        self.assertEqual(len(token1), 30)
        self.assertEqual(len(token2), 30)
        self.assertEqual(token1, token2)
