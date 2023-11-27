import time
import unittest
from unittest.mock import Mock, patch, MagicMock

from fastapi import HTTPException

from common.auth import get_current_user
from routers import admin_routers
from services import admin_services
from services.authorization_services import get_password_hash
from app_models.admin_models import Admin

# mock_admin_services = Mock(spec='services.admin_services')
# mock_admin_services.create_admin = Mock(return_value='Mocked return')
#
# admin_routers.admin_services = mock_admin_services


def fake_admin_payload():
    payload = MagicMock(spec=dict)
    payload['group'] = 'admins'
    return payload


def fake_regular_payload():
    payload = MagicMock(dict)
    return payload


def fake_admin():
    admin = Mock()
    return admin


class AdminRouter_Should(unittest.TestCase):
    def setUp(self):
        self.original_get_current_user = get_current_user
        mock_admin_services.reset_mock()

    def tearDown(self) -> None:
        get_current_user = self.original_get_current_user

    def test_addAdmin_returnsAdmin(self):
        pass

    def test_addAdmin_raisesExceptionWhenUserNotAdmin(self):
        get_current_user = lambda: {"id": 1,
                                    "group": "companies",
                                    "username": "CompanyUser",
                                    "email": "company@company.com",
                                    "blocked": 0,
                                    'exp': time.time()
                                    }

        # get_current_user = fake_regular_payload()
        new_admin = fake_admin()

        # with TestClient(app) as test_client:
        #     response = test_client.post('/register')

        with self.assertRaises(HTTPException) as e:
            admin_routers.add_admin(new_admin, 'asdQWE123!@#')

        self.assertEqual(e.exception.status_code, 403)

    def test_addAdmin_raisesExceptionWhenAdminExists(self):
        pass

    def test_addAdmin_raisesExceptionWhenAdminCreatesNonAdmin(self):
        pass

    def test_deleteAllTempTokens_raisesExceptionWhenUserNotAdmin(self):
        pass

    def test_getAdminAvatar_returnsStreamingResponse(self):
        pass

    def test_getAdminAvatar_raisesExceptionWhenNoAdmin(self):
        pass

    def test_getAdminAvatar_raisesExceptionWhenNoImage(self):
        pass


class AdminServices_Should(unittest.TestCase):
    def test_adminExists_returnsTrue_ifAdminFound(self):
        admin = fake_admin()
        with patch('services.admin_services.read_query') as read_query:
            read_query.return_value = [(3,)]
            result = admin_services.admin_exists(admin)

        self.assertEqual(True, result)

    def test_adminExists_returnsFalse_ifNoAdmin(self):
        with patch('services.admin_services.read_query') as read_query:
            admin = fake_admin()
            read_query.return_value = []
            result = admin_services.admin_exists(admin)

        self.assertEqual(False, result)

    def test_adminExistsById_returnsTrue_ifAdminFound(self):
        with patch('services.admin_services.read_query') as read_query:
            read_query.return_value = [(3,)]
            result = admin_services.admin_exists_by_id(3)
            # Note: even though the return value and the parameter are identical
            # in reality the logic is handled by the SQL query, so they need not be
            # in the test. We've kept them identical because it mimics real logic.

        self.assertEqual(True, result)

    def test_adminExistsById_returnsFalse_ifNoAdmin(self):
        with patch('services.admin_services.read_query') as read_query:
            read_query.return_value = []
            result = admin_services.admin_exists_by_id(3)

        self.assertEqual(False, result)

    def test_getAdmin_returnsAdmin(self):
        with patch('services.admin_services.read_query') as read_query:
            username = 'testing_admin'
            control_admin = Admin(id=1, username=username, first_name='first_name',
                                  last_name='last_name', email='email@email.email',
                                  address='111 address lane', phone='5551234',
                                  city='Sofia', country='Bulgaria')
            read_query.return_value = [(1, 'testing_admin', 'first_name', 'last_name',
                                        'email@email.email', '111 address lane',
                                        '5551234', 'Sofia', 'Bulgaria')]

            admin = admin_services.get_admin(username)

        self.assertIsInstance(admin, Admin)
        self.assertEqual(control_admin, admin)


    def test_getAdmin_returnsNoneIfNoAdmin(self):
        with patch('services.admin_services.read_query') as read_query:
            username = 'testing_admin'
            read_query.return_value = []
            result = admin_services.get_admin(username)

        self.assertEqual(None, result)

    def test_getAdminByEmail_returnsAdmin(self):
        with patch('services.admin_services.read_query') as read_query:
            email = 'email@email.email'
            control_admin = Admin(id=1, username='testing_admin', first_name='first_name',
                                  last_name='last_name', email=email,
                                  address='111 address lane', phone='5551234',
                                  city='Sofia', country='Bulgaria')
            read_query.return_value = [(1, 'testing_admin', 'first_name', 'last_name',
                                        'email@email.email', '111 address lane',
                                        '5551234', 'Sofia', 'Bulgaria')]

            admin = admin_services.get_admin_by_email(email)

        self.assertIsInstance(admin, Admin)
        self.assertEqual(control_admin, admin)

    def test_getAdminByEmail_returnsNoneIfNoAdmin(self):
        with patch('services.admin_services.read_query') as read_query:
            email = 'email@email.email'
            read_query.return_value = []
            result = admin_services.get_admin_by_email(email)

        self.assertEqual(None, result)

    def test_createAdmin_ReturnsAdmin(self):
        created_admin = Admin(username='testing_admin', first_name='first_name',
                              last_name='last_name', email='email@email.email',
                              address='111 address lane', phone='5551234',
                              city='Sofia', country='Bulgaria')
        password = 'password'

        control_admin = Admin(id=1, username='testing_admin', first_name='first_name',
                              last_name='last_name', email='email@email.email',
                              address='111 address lane', phone='5551234',
                              city='Sofia', country='Bulgaria')

        with patch('services.admin_services.insert_query') as insert_query:
            with patch('services.admin_services.find_location_id') as find_location_id:
                find_location_id.return_value = 1
                insert_query.return_value = 1

                admin_services.create_admin(created_admin, password)

        self.assertIsInstance(created_admin, Admin)
        self.assertEqual(control_admin, created_admin)

    def test_CreateAdmin_HashesPassword(self):
        created_admin = Admin(username='testing_admin', first_name='first_name',
                              last_name='last_name', email='email@email.email',
                              address='111 address lane', phone='5551234',
                              city='Sofia', country='Bulgaria')
        password = 'password'

        with patch('services.admin_services.insert_query') as insert_query:
            with patch('services.admin_services.find_location_id') as find_location_id:
                find_location_id.return_value = 1
                insert_query.return_value = 1

                with patch('services.authorization_services.get_password_hash') as get_password_hash:
                    admin_services.create_admin(created_admin, password)

        get_password_hash.assert_called_once_with(password)



