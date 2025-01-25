from rest_framework.test import APITestCase
from users.models import User

# Create your tests here.

BASE_URL = "/api/v1/users"


# test users
test_users = [
    "test_user1",
    "test_user2",
    "test_user3",
]


# create test users
def create_user(username="test_user", password="test_password"):
    return User.objects.create_user(
        username=username,
        password=password,
    )


class RootTestCase(APITestCase):
    URL = f"{BASE_URL}/"

    def setUp(self):
        for user in test_users:
            create_user(user)

    def test_get(self):
        response = self.client.get(self.URL)
        self.assertEqual(response.status_code, 200, "ROOT get #1")
        self.assertEqual(len(response.data), 3, "ROOT get #2")

    def test_post_success(self):
        response = self.client.get(self.URL)

        self.assertEqual(response.status_code, 200, "ROOT post_success #1")
        self.assertEqual(len(response.data), 3, "ROOT post_success #2")

        response = self.client.post(
            self.URL,
            {
                "username": "test_user4",
                "password1": "test_password",
                "password2": "test_password",
                "name": "Test User 4",
                "email": "test@test.com",
            },
        )

        self.assertEqual(
            response.data["username"], "test_user4", "ROOT post_success #3"
        )
        self.assertEqual(response.data["name"], "Test User 4", "ROOT post_success #4")
        self.assertEqual(
            response.data["email"], "test@test.com", "ROOT post_success #5"
        )
        self.assertIsNone(response.data.get("password"), "ROOT post_success #6")
        self.assertEqual(response.status_code, 201, "ROOT post_success #7")

        # check if user was created
        self.assertEqual(User.objects.count(), 4, "ROOT post_success #8")

    def test_post_fail_registed_user(self):
        response = self.client.post(
            self.URL,
            {
                "username": "test_user3",
                "password1": "test_password",
                "password2": "test_password",
                "name": "Test User 3",
                "email": "test@test.com",
            },
        )
        self.assertEqual(response.status_code, 400, "ROOT post_fail_registed_user #1")

    def test_post_fail_password_not_match(self):
        response = self.client.post(
            self.URL,
            {
                "username": "test_user4",
                "password1": "test_password",
                "password2": "test_password2",
                "name": "Test User 4",
                "email": "test@test.com",
            },
        )
        self.assertEqual(
            response.status_code, 400, "ROOT post_fail_password_not_match #1"
        )

    def test_post_fail_invalid_password(self):
        form = {
            "username": "test_user4",
            "name": "Test User 4",
            "email": "test@test.com",
        }
        form["password1"] = "1234"
        form["password2"] = "1234"
        response = self.client.post(
            self.URL,
            form,
        )
        self.assertEqual(
            response.status_code, 400, "ROOT post_fail_password_not_match #1"
        )
        print(response.data["errors"])

        form["password1"] = "11111111111111111111"
        form["password2"] = "11111111111111111111"
        response = self.client.post(
            self.URL,
            form,
        )
        self.assertEqual(
            response.status_code, 400, "ROOT post_fail_password_not_match #2"
        )
        print(response.data["errors"])

        form["password1"] = "password"
        form["password2"] = "password"
        response = self.client.post(
            self.URL,
            form,
        )
        self.assertEqual(
            response.status_code, 400, "ROOT post_fail_password_not_match #2"
        )
        print(response.data["errors"])


class LoginTestCase(APITestCase):
    URL = f"{BASE_URL}/login"

    def setUp(self):
        create_user("test_user", "test_password")

    def test_post_success(self):
        response = self.client.post(
            self.URL,
            {
                "username": "test_user",
                "password": "test_password",
            },
        )
        self.assertEqual(response.status_code, 200, "LOGIN post_success #1")
        self.assertIsNotNone(response.data.get("jwt"), "LOGIN post_success #2")

        # set jwt token to request header and test auth
        self.client.credentials(HTTP_JWT=response.data["jwt"])
        response = self.client.get(f"{BASE_URL}/auth")
        self.assertEqual(response.status_code, 200, "LOGIN post_success #3")

    def test_post_fail(self):
        response = self.client.post(
            self.URL,
            {
                "username": "test_user",
                "password": "test_password2",
            },
        )
        self.assertEqual(response.status_code, 401, "LOGIN post_fail #1")

        response = self.client.post(
            self.URL,
            {
                "username": "test_user2",
                "password": "test_password",
            },
        )
        self.assertEqual(response.status_code, 401, "LOGIN post_fail #2")

        response = self.client.post(
            self.URL,
            {
                "username": "test_user2",
                "password": "test_password2",
            },
        )
        self.assertEqual(response.status_code, 401, "LOGIN post_fail #3")


class LogoutTestCase(APITestCase):
    URL = f"{BASE_URL}/logout"

    def setUp(self):
        create_user("test_user", "test_password")

    def test_post_issue(self):
        response = self.client.post(
            f"{BASE_URL}/login",
            {
                "username": "test_user",
                "password": "test_password",
            },
        )
        self.assertEqual(response.status_code, 200, "LOGOUT post_success #1")
        self.assertIsNotNone(response.data.get("jwt"), "LOGOUT post_success #2")

        # set jwt token to request header and test auth
        jwt = response.data["jwt"]
        self.client.credentials(HTTP_JWT=jwt)
        response = self.client.get(f"{BASE_URL}/auth")
        self.assertEqual(response.status_code, 200, "LOGOUT post_success #3")

        response = self.client.post(self.URL)
        self.assertEqual(response.status_code, 200, "LOGOUT post_success #4")

        # JWT에서는 로그아웃이 불가능합니다
        response = self.client.get(f"{BASE_URL}/auth")
        self.assertEqual(response.status_code, 200, "LOGOUT post_success #5")
        # self.assertEqual(response.status_code, 401, "LOGOUT post_success #5")
