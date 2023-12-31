import string
import unittest

from unittest.mock import Mock, patch

import bcrypt
import jwt
from jose import JWTError
from passlib.context import CryptContext
from fastapi.exceptions import HTTPException

import services.authorization_services
from app_models.admin_models import Admin
from app_models.company_models import Company
from app_models.job_seeker_models import JobSeeker
from app_models.token_models import AccessDataModel, ActivationDataModel
from services import authorization_services


class AuthorizationServices_Should(unittest.TestCase):
    def test_verifyPasswordTextPasswordMatchesHash(self):
        self.pwd_context = CryptContext(schemes=['bcrypt'], deprecated="auto")

        text_password = 'asdQWE123!@#'
        wrong_text_password = 'aaa'
        hashed_password = self.pwd_context.hash(text_password)

        self.assertTrue(authorization_services.verify_password(text_password, hashed_password))
        self.assertFalse(authorization_services.verify_password(wrong_text_password, hashed_password))

    def test_getPasswordHash_GeneratesHash(self):
        # A bit redundant
        self.pwd_context = CryptContext(schemes=['bcrypt'], deprecated="auto")

        text_password = 'asdQWE123!@#'
        wrong_text_password = 'aaa'

        result = authorization_services.get_password_hash(text_password)

        is_valid = self.pwd_context.verify(text_password, result)
        is_not_valid = self.pwd_context.verify(wrong_text_password, result)

        self.assertTrue(is_valid)
        self.assertFalse(is_not_valid)

    def test_getPassByUsernameAdminReturnsString(self):
        username = 'username'
        with patch('services.authorization_services.read_query') as read_query:
            read_query.return_value = [('AnAdminPass',)]

            result = authorization_services._get_pass_by_username_admin(username)

        self.assertIsInstance(result, str)

    def test_getPassByUsernameSeekerReturnsString(self):
        username = 'username'
        with patch('services.authorization_services.read_query') as read_query:
            read_query.return_value = [('ASeekerPass',)]

            result = authorization_services._get_pass_by_username_admin(username)

        self.assertIsInstance(result, str)

    def test_getPassByUsernameCompanyReturnsString(self):
        username = 'username'
        with patch('services.authorization_services.read_query') as read_query:
            read_query.return_value = [('ACompanyPass',)]

            result = authorization_services._get_pass_by_username_admin(username)

        self.assertIsInstance(result, str)

    def test_authenticateAdminReturnsAdminIfAdmin(self):
        password = 'asdQWE123!@#'
        with patch('services.admin_services.get_admin') as get_admin:
            get_admin.return_value = Admin(id=1, username='username', first_name='first_name',
                                           last_name='last_name', email='email@email.email',
                                           address='111 address lane', phone='5551234',
                                           city='Sofia', country='Bulgaria')
            with patch('services.authorization_services._get_pass_by_username_admin') as get_pass:
                get_pass.return_value = None
                with patch('services.authorization_services.verify_password') as verify_password:
                    verify_password.return_value = True

                    result = authorization_services.authenticate_admin(get_admin.return_value.username, password)

            self.assertIsInstance(result, Admin)
            self.assertEqual(get_admin.return_value, result)

    def test_authenticateAdminReturnsFalseIfNoAdmin(self):
        password = 'asdQWE123!@#'
        username = 'username'
        with patch('services.admin_services.get_admin') as get_admin:
            get_admin.return_value = None

            result = authorization_services.authenticate_admin(username, password)

        self.assertFalse(result)

    def test_authenticateAdminUsesVerifyPassword(self):
        password = 'asdQWE123!@#'
        with patch('services.admin_services.get_admin') as get_admin:
            get_admin.return_value = Admin(id=1, username='username', first_name='first_name',
                                           last_name='last_name', email='email@email.email',
                                           address='111 address lane', phone='5551234',
                                           city='Sofia', country='Bulgaria')
            with patch('services.authorization_services._get_pass_by_username_admin') as get_pass:
                get_pass.return_value = None
                with patch('services.authorization_services.verify_password') as verify_password:
                    authorization_services.authenticate_admin(get_admin.return_value.username, password)

        verify_password.assert_called_once()

    def test_authenticateSeekerReturnsSeeker(self):
        password = 'asdQWE123!@#'
        with patch('services.job_seeker_services.get_seeker') as get_seeker:
            get_seeker.return_value = JobSeeker(id=1, username='username', email='email@email.email',
                                                first_name='first_name', last_name='last_name')
            with patch('services.authorization_services._get_pass_by_username_seeker') as get_pass:
                get_pass.return_value = None
                with patch('services.authorization_services.verify_password') as verify_password:
                    verify_password.return_value = True

                    result = authorization_services.authenticate_seeker(get_seeker.return_value.username, password)

            self.assertIsInstance(result, JobSeeker)
            self.assertEqual(get_seeker.return_value, result)

    def test_authenticateSeekerReturnsFalseIfNoSeeker(self):
        password = 'asdQWE123!@#'
        username = 'username'
        with patch('services.job_seeker_services.get_seeker') as get_seeker:
            get_seeker.return_value = None

            result = authorization_services.authenticate_seeker(username, password)

        self.assertFalse(result)

    def test_authenticateSeekerUsesVerifyPassword(self):
        password = 'asdQWE123!@#'
        with patch('services.job_seeker_services.get_seeker') as get_seeker:
            get_seeker.return_value = JobSeeker(id=1, username='username', email='email@email.email',
                                                first_name='first_name', last_name='last_name')
            with patch('services.authorization_services._get_pass_by_username_seeker') as get_pass:
                get_pass.return_value = None
                with patch('services.authorization_services.verify_password') as verify_password:
                    authorization_services.authenticate_seeker(get_seeker.return_value.username, password)

        verify_password.assert_called_once()

    def test_authenticateCompanyReturnsCompany(self):
        password = 'asdQWE123!@#'
        with patch('services.company_services.get_company') as get_company:
            get_company.return_value = Company(id=1, username='username', email='email@email.email',
                                               work_address='111 address lane', telephone='5551234',
                                               city='Sofia', country='Bulgaria')
            with patch('services.authorization_services._get_pass_by_username_company') as get_pass:
                get_pass.return_value = None
                with patch('services.authorization_services.verify_password') as verify_password:
                    verify_password.return_value = True

                    result = authorization_services.authenticate_company(get_company.return_value.username, password)

            self.assertIsInstance(result, Company)
            self.assertEqual(get_company.return_value, result)

    def test_authenticateCompanyReturnsFalseIfNoCompany(self):
        password = 'asdQWE123!@#'
        username = 'username'
        with patch('services.company_services.get_company') as get_company:
            get_company.return_value = None

            result = authorization_services.authenticate_company(username, password)

        self.assertFalse(result)

    def test_authenticateCompanyUsesVerifyPassword(self):
        password = 'asdQWE123!@#'
        with patch('services.company_services.get_company') as get_company:
            get_company.return_value = Company(id=1, username='username', email='email@email.email',
                                               work_address='111 address lane', telephone='5551234',
                                               city='Sofia', country='Bulgaria')
            with patch('services.authorization_services._get_pass_by_username_company') as get_pass:
                get_pass.return_value = None
                with patch('services.authorization_services.verify_password') as verify_password:
                    authorization_services.authenticate_company(get_company.return_value.username, password)

        verify_password.assert_called_once()

    def test_createAccessTokenEncodesDecodableJWTToken(self):
        user_data = AccessDataModel(id=1, group='admins', username='username', email='email@email.email')
        TEST_KEY = 'TEST'

        with patch('services.authorization_services._SECRET_KEY', TEST_KEY):
            with patch('services.authorization_services.jwt.encode', wraps=jwt.encode) as encoder:
                encoded = authorization_services.create_access_token(user_data)
                result = authorization_services.is_authenticated(encoded)

        encoder.assert_called_once()
        self.assertEqual(user_data.id, result['id'])
        self.assertEqual(user_data.group, result['group'])
        self.assertEqual(user_data.username, result['username'])
        self.assertEqual(user_data.email, result['email'])

    def test_createActivationTokenCreatesDecodableToken(self):
        user_data = ActivationDataModel(id=1, group='admins', username='username', email='email@email.email',
                                        purpose='password_reset')
        TEST_KEY = 'TEST'

        with patch('services.authorization_services._CUSTOM_SECRET_KEY', TEST_KEY):
            with patch('services.authorization_services.jwt.encode', wraps=jwt.encode) as encoder:
                encoded = authorization_services.create_activation_token(user_data)
                result = authorization_services.is_authenticated_custom(encoded)

        encoder.assert_called_once()
        self.assertEqual(user_data.id, result['id'])
        self.assertEqual(user_data.group, result['group'])
        self.assertEqual(user_data.username, result['username'])
        self.assertEqual(user_data.email, result['email'])
        self.assertEqual(user_data.purpose, result['purpose'])

    def test_ActivationTokenCannotBeUsedAsAccessTokenViceVersa(self):
        user_data = ActivationDataModel(id=1, group='admins', username='username', email='email@email.email',
                                        purpose='password_reset')

        encoded_access = authorization_services.create_access_token(user_data)
        encoded_activation = authorization_services.create_activation_token(user_data)

        with self.assertRaises(HTTPException):
            with self.assertRaises(JWTError):
                authorization_services.is_authenticated(encoded_activation)
            with self.assertRaises(JWTError):
                authorization_services.is_authenticated_custom(encoded_access)

    def test_isAuthenticatedReturnsMeaningfulToken(self):
        # I wrote this test out, but worth noting that DecodableToken test is very similar in logic
        # Note, in a previous version of the code, I had tokens directly in the code, but this doesn't work due
        # Due to JOSE validating expiration at decoding.
        # Therefore, it is necessary in these tests to rely on the create methods.
        user_data = AccessDataModel(id=1, group='admins', username='username', email='email@email.email')
        token = authorization_services.create_access_token(user_data)
        result = authorization_services.is_authenticated(token)

        self.assertIsInstance(result, dict)
        self.assertEqual(result['username'], 'username')

    def test_isAuthenticatedCustomReturnsMeaningfulToken(self):
        # See comment above.
        user_data = ActivationDataModel(id=1, group='admins', username='username', email='email@email.email',
                                        purpose='password_reset')

        token = authorization_services.create_activation_token(user_data)
        result = authorization_services.is_authenticated_custom(token)

        self.assertIsInstance(result, dict)
        self.assertEqual(result['username'], 'username')

    def test_passwordChangerUpdatesCorrectTable(self):
        payload = {'id': 1, 'group': 'admins'}
        password = 'password'
        with patch('services.authorization_services.update_query') as update_query:
            update_query.return_value = 'admin case'
            result = authorization_services.password_changer(payload, password)

        self.assertEqual('admin case', result)

        payload['group'] = 'companies'
        with patch('services.authorization_services.update_query') as update_query:
            update_query.return_value = 'company case'
            result = authorization_services.password_changer(payload, password)

        self.assertEqual('company case', result)

        payload['group'] = 'seekers'
        with patch('services.authorization_services.update_query') as update_query:
            update_query.return_value = 'seeker case'
            result = authorization_services.password_changer(payload, password)

        self.assertEqual('seeker case', result)

    def test_passwordChangerUsesGetPasswordHash(self):
        payload = {'id': 1, 'group': 'admins'}
        password = 'password'
        with patch('services.authorization_services.update_query') as update_query:
            update_query.return_value = None
            with patch('services.authorization_services.get_password_hash') as get_pass:
                authorization_services.password_changer(payload, password)

        get_pass.assert_called_once_with(password)

    def test_isPasswordIdenticalByTypeUsesVerifyPassword(self):
        payload = {'id': 1, 'group': 'admins', 'username': 'username'}
        password = 'password'

        with patch('services.authorization_services.verify_password') as verify_pass:
            with patch('services.authorization_services._get_pass_by_username_admin') as get_pass:
                get_pass.return_value = None
                authorization_services.is_password_identical_by_type(payload, password)
            payload['group'] = 'companies'
            with patch('services.authorization_services._get_pass_by_username_company') as get_pass:
                get_pass.return_value = None
                authorization_services.is_password_identical_by_type(payload, password)
            payload['group'] = 'seekers'
            with patch('services.authorization_services._get_pass_by_username_seeker') as get_pass:
                get_pass.return_value = None
                authorization_services.is_password_identical_by_type(payload, password)

        self.assertEqual(3, verify_pass.call_count)

    def test_generatePasswordGeneratesDifferentPasswords(self):
        password_one = authorization_services.generate_password()
        password_two = authorization_services.generate_password()

        self.assertNotEqual(password_one, password_two)

    def test_generatePassword_GeneratedPasswordHasLowerUpperNumbersSpecialChars(self):
        generated_pass = authorization_services.generate_password()

        lower_case = string.ascii_lowercase
        upper_case = string.ascii_uppercase
        numbers = string.digits
        special_chars = "@$!%*?&"

        lower_found, upper_found, number_found, special_found = False, False, False, False

        for char in generated_pass:
            if lower_found is False and char in lower_case:
                lower_found = True
            elif upper_found is False and char in upper_case:
                upper_found = True
            elif number_found is False and char in numbers:
                number_found = True
            elif special_found is False and char in special_chars:
                special_found = True
            if lower_found and upper_found and number_found and special_found:
                break

        self.assertTrue(all((lower_found, upper_found, number_found, special_found)))

    def test_generatePassword_AtLeastFifteenSymbolsLong(self):
        self.assertGreater(len(authorization_services.generate_password()), 14)

    def test_activationTokenExistsReturnsTrueIfToken(self):
        activation_token = None
        with patch('services.authorization_services.read_query') as read_query:
            read_query.return_value = [('token_simulation',)]
            result = authorization_services.activation_token_exists(activation_token)

        self.assertTrue(result)

    def test_activationTokenExistsReturnsTrueIfNotFound(self):
        activation_token = None
        with patch('services.authorization_services.read_query') as read_query:
            read_query.return_value = []
            result = authorization_services.activation_token_exists(activation_token)

        self.assertFalse(result)

    # Below is a bit redundant but I do not want to leave a method untested
    def test_storeActivationTokenUsesInsertQuery(self):
        activation_token = None
        with patch('services.authorization_services.insert_query') as insert_query:
            insert_query.return_value = None
            authorization_services.store_activation_token(activation_token)

        insert_query.assert_called()

    def test_deleteActivationTokenUsesUpdateQuery(self):
        activation_token = None
        with patch('services.authorization_services.update_query') as update_query:
            update_query.return_value = None
            authorization_services.delete_activation_token(activation_token)

        update_query.assert_called()
