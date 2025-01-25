from rest_framework.test import APITestCase
from users.tests import create_user
from . import jwt_utils


# Create your tests here.
class JWTTestCase(APITestCase):
    def test_create_jwt_token(self):
        user = create_user("test_user1")

        token = jwt_utils.encode(user)
        self.assertIsNotNone(token, "FUNCTION create_jwt_token  #1")
        content = jwt_utils.decode(token)
        self.assertEqual(
            content["username"], user.username, "FUNCTION create_jwt_token  #2"
        )
        self.assertEqual(content["pk"], user.pk, "FUNCTION create_jwt_token  #3")

        self.client.credentials(HTTP_JWT=token)
        response = self.client.get("/api/v1/users/auth")
        self.assertEqual(response.status_code, 200, "FUNCTION create_jwt_token  #1")
