from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from .models import UserProfile
from .forms import RegistrationForm, UserUpdateForm, UserProfileForm

class UserProfileModelTests(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(username='testuser', email='test@example.com', password='password123')

    def test_user_profile_is_created_on_user_creation(self):
        """Test that a UserProfile is automatically created when a User is created."""
        self.assertTrue(hasattr(self.user, 'profile'))
        self.assertIsInstance(self.user.profile, UserProfile)
        self.assertEqual(UserProfile.objects.count(), 1)

    def test_user_profile_str_representation(self):
        """Test the string representation of the UserProfile model."""
        profile = self.user.profile
        self.assertEqual(str(profile), 'testuser Profile')

    def test_user_profile_can_be_updated(self):
        """Test that UserProfile fields can be updated."""
        profile = self.user.profile
        profile.bio = "This is a test bio."
        profile.save()
        updated_profile = UserProfile.objects.get(user=self.user)
        self.assertEqual(updated_profile.bio, "This is a test bio.")


class RegistrationApprovalFlowTests(TestCase):

    def setUp(self):
        self.client = Client()
        self.admin_user = User.objects.create_superuser(username='adminuser', email='admin@example.com', password='adminpassword')
        self.register_url = reverse('register')
        self.admin_dashboard_url = reverse('admin_dashboard')
        self.login_url = reverse('login') # Default Django login URL

    def test_user_registration_creates_inactive_user(self):
        """Test that user registration creates an inactive user awaiting approval."""
        user_data = {'username': 'newbie', 'email': 'newbie@example.com', 'password': 'newpassword123', 'password2': 'newpassword123'}
        # The RegistrationForm is a UserCreationForm, which expects 'password' and 'password2'
        # Our custom RegistrationForm uses fields = ("username", "email"), but UserCreationForm handles passwords.
        # Let's use the form directly to simulate its validation for password fields.

        form = RegistrationForm(data={'username': 'newbie', 'email': 'newbie@example.com', 'password': 'newpassword123', 'password2': 'newpassword123'})
        # This is how UserCreationForm expects passwords, let's adjust UserCreationForm in forms.py to include password fields for direct use
        # Or, use the actual form post which handles password1 and password2 from UserCreationForm

        response = self.client.post(self.register_url, {
            'username': 'newuser',
            'email': 'newuser@example.com',
            # UserCreationForm expects password1 and password2
            'password1': 'securepassword',
            'password2': 'securepassword'
        })

        self.assertEqual(response.status_code, 302) # Should redirect after successful registration
        self.assertRedirects(response, reverse('pending_approval'))

        self.assertTrue(User.objects.filter(username='newuser').exists())
        new_user = User.objects.get(username='newuser')
        self.assertFalse(new_user.is_active)
        self.assertTrue(hasattr(new_user, 'profile')) # Profile should also be created

    def test_admin_can_approve_user(self):
        """Test that an admin can approve a pending user."""
        pending_user = User.objects.create_user(username='pendinguser', email='pending@example.com', password='password', is_active=False)
        self.client.login(username='adminuser', password='adminpassword')

        approve_url = reverse('approve_user', args=[pending_user.id])
        response = self.client.get(approve_url) # GET request to approve

        self.assertEqual(response.status_code, 302) # Redirects to admin dashboard
        self.assertRedirects(response, self.admin_dashboard_url)

        approved_user = User.objects.get(username='pendinguser')
        self.assertTrue(approved_user.is_active)

    def test_admin_can_reject_user(self):
        """Test that an admin can reject (delete) a pending user."""
        pending_user = User.objects.create_user(username='rejectme', email='rejectme@example.com', password='password', is_active=False)
        self.client.login(username='adminuser', password='adminpassword')

        reject_url = reverse('reject_user', args=[pending_user.id])
        response = self.client.get(reject_url) # GET request to reject

        self.assertEqual(response.status_code, 302) # Redirects to admin dashboard
        self.assertRedirects(response, self.admin_dashboard_url)

        self.assertFalse(User.objects.filter(username='rejectme').exists())

    def test_non_staff_cannot_access_admin_dashboard(self):
        """Test that a non-staff user is redirected from admin dashboard."""
        non_staff_user = User.objects.create_user(username='regularjoe', password='password')
        self.client.login(username='regularjoe', password='password')
        response = self.client.get(self.admin_dashboard_url)
        self.assertNotEqual(response.status_code, 200)
        # Default behavior for @staff_member_required is to redirect to login page
        self.assertRedirects(response, f"{self.login_url}?next={self.admin_dashboard_url}")

    def test_anonymous_user_cannot_access_admin_dashboard(self):
        """Test that an anonymous user is redirected from admin dashboard."""
        response = self.client.get(self.admin_dashboard_url)
        self.assertNotEqual(response.status_code, 200)
        self.assertRedirects(response, f"{self.login_url}?next={self.admin_dashboard_url}")

# Need to adjust RegistrationForm to align with UserCreationForm's password field names ('password1', 'password2')
# if we want to test form.is_valid() directly with passwords.
# The current RegistrationForm in forms.py only declares 'username' and 'email' in Meta.fields.
# UserCreationForm itself adds the password fields.
# For the client.post test, this is fine as the request data will contain password1 and password2.

# The RegistrationForm in forms.py needs to have its Meta.fields updated to include password fields
# if we want to instantiate it with password data directly in tests and call is_valid().
# Current RegistrationForm: fields = ("username", "email")
# This is a bit of a discrepancy. UserCreationForm itself adds password1 and password2 fields.
# The client.post test for registration is more representative of actual usage.
# I'll update the RegistrationForm in `accounts/forms.py` to be more explicit for clarity.
# However, UserCreationForm is designed to work this way, inheriting fields is standard.
# The test `test_user_registration_creates_inactive_user` is correctly posting 'password1' and 'password2'.
# The form instance `form = RegistrationForm(data=...)` in that test was not actually used for the post, it was a thought process.
# The client.post() is the actual test of the view and form interaction.
# The view uses `form = RegistrationForm(request.POST)` which works.

# A small fix to RegistrationForm in forms.py could be to explicitly list all fields for clarity,
# or trust UserCreationForm to handle its password fields, which it does.
# For now, the tests for POSTing to the view are robust.

from unittest.mock import patch, MagicMock
from django.contrib.messages import get_messages


class ProfileViewEditTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='profileuser', email='profile@example.com', password='profilepassword')
        # UserProfile is created by signal
        self.profile_url = reverse('profile_view_edit')
        self.login_url = reverse('login')

    def test_anonymous_user_redirected_from_profile_page(self):
        response = self.client.get(self.profile_url)
        self.assertRedirects(response, f"{self.login_url}?next={self.profile_url}")

    def test_authenticated_user_can_view_profile_page(self):
        self.client.login(username='profileuser', password='profilepassword')
        response = self.client.get(self.profile_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'accounts/profile_edit.html')
        self.assertIn('user_form', response.context)
        self.assertIn('profile_form', response.context)
        self.assertIsInstance(response.context['user_form'], UserUpdateForm)
        self.assertIsInstance(response.context['profile_form'], UserProfileForm)

    def test_authenticated_user_can_update_profile(self):
        self.client.login(username='profileuser', password='profilepassword')
        update_data = {
            'username': 'profileuserupdated',
            'email': 'profileupdated@example.com',
            'first_name': 'Profile',
            'last_name': 'User',
            'bio': 'This is my updated bio.'
            # Not testing profile_picture upload here to keep it simpler.
            # It would require using SimpleUploadedFile.
        }
        response = self.client.post(self.profile_url, update_data)

        self.assertEqual(response.status_code, 302, "Profile update should redirect.")
        self.assertRedirects(response, self.profile_url)

        updated_user = User.objects.get(id=self.user.id)
        self.assertEqual(updated_user.username, 'profileuserupdated')
        self.assertEqual(updated_user.email, 'profileupdated@example.com')
        self.assertEqual(updated_user.first_name, 'Profile')
        self.assertEqual(updated_user.last_name, 'User')
        self.assertEqual(updated_user.profile.bio, 'This is my updated bio.')

        # Check for success message after redirect
        response_followed = self.client.get(self.profile_url)
        messages = list(get_messages(response_followed.wsgi_request)) # Use get_messages
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), 'Your profile has been updated successfully!')

    def test_profile_update_with_invalid_data(self):
        self.client.login(username='profileuser', password='profilepassword')
        invalid_data = {
            'username': '', # Invalid: username cannot be empty
            'email': 'invalidemail', # Invalid email format
            'bio': 'Some bio'
        }
        response = self.client.post(self.profile_url, invalid_data)
        self.assertEqual(response.status_code, 200) # Should re-render form with errors
        self.assertFormError(response, 'user_form', 'username', 'This field is required.')
        self.assertFormError(response, 'user_form', 'email', 'Enter a valid email address.')

        messages = list(get_messages(response.wsgi_request))
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), 'Please correct the errors below.')


class SearchViewTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='searchuser', password='searchpassword')
        self.search_url = reverse('search')
        self.login_url = reverse('login')

    def tearDown(self):
        # Clear session after each test if session data was set
        if self.client.session:
             self.client.session.flush()


    def test_anonymous_user_redirected_from_search_page(self):
        response_get = self.client.get(self.search_url)
        self.assertRedirects(response_get, f"{self.login_url}?next={self.search_url}")

        response_post = self.client.post(self.search_url, {'query': 'test'})
        self.assertRedirects(response_post, f"{self.login_url}?next={self.search_url}")

    @patch('accounts.views.search')
    def test_search_with_results_post(self, mock_googlesearch):
        self.client.login(username='searchuser', password='searchpassword')
        mock_googlesearch.return_value = ['http://result1.com', 'http://result2.com']

        response = self.client.post(self.search_url, {'query': 'test query'})

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'search.html')
        self.assertIn('results_page', response.context)
        self.assertEqual(len(response.context['results_page'].object_list), 2)
        self.assertEqual(response.context['results_page'].object_list[0], 'http://result1.com')
        mock_googlesearch.assert_called_once_with('test query', num_results=50, lang='en')
        self.assertIsNone(response.context.get('error_message'))
        self.assertEqual(self.client.session.get('search_query'), 'test query')


    @patch('accounts.views.search')
    def test_search_with_no_results_post(self, mock_googlesearch):
        self.client.login(username='searchuser', password='searchpassword')
        mock_googlesearch.return_value = []

        response = self.client.post(self.search_url, {'query': 'obscure query'})

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'search.html')
        self.assertFalse(response.context.get('results_page'))
        self.assertIsNone(response.context.get('error_message'))
        self.assertEqual(self.client.session.get('search_query'), 'obscure query')


    @patch('accounts.views.search')
    def test_search_with_library_error_post(self, mock_googlesearch):
        self.client.login(username='searchuser', password='searchpassword')
        mock_googlesearch.side_effect = Exception("Simulated search library error")

        response = self.client.post(self.search_url, {'query': 'error query'})

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'search.html')
        self.assertFalse(response.context.get('results_page'))
        self.assertIn('error_message', response.context)
        self.assertIn("An error occurred during the search", response.context['error_message'])
        self.assertEqual(self.client.session.get('search_query'), 'error query')


    def test_search_with_empty_query_post(self):
        self.client.login(username='searchuser', password='searchpassword')
        response = self.client.post(self.search_url, {'query': ' '})

        self.assertEqual(response.status_code, 200) # View now returns 200 with error message
        self.assertTemplateUsed(response, 'search.html')
        self.assertFalse(response.context.get('results_page'))
        self.assertIn('error_message', response.context)
        self.assertEqual(response.context['error_message'], "Please enter a search term.")
        self.assertNotIn('search_query', self.client.session) # Query shouldn't be stored if empty

    def test_search_page_get_request_initial(self):
        self.client.login(username='searchuser', password='searchpassword')
        response = self.client.get(self.search_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'search.html')
        # results_page context should be an empty list or similar, not None, if paginator was initialized with empty list
        self.assertTrue(hasattr(response.context.get('results_page'), 'object_list') and not response.context.get('results_page').object_list or not response.context.get('results_page'))
        self.assertIsNone(response.context.get('error_message'))
        self.assertEqual(response.context.get('query'), "")

    # Patch both 'googlesearch.search' (imported as 'search' in views) AND 'get_title_from_url'
    @patch('accounts.views.get_title_from_url')
    @patch('accounts.views.search') # This is googlesearch.search
    def test_search_pagination_get_after_post(self, mock_api_search, mock_get_title):
        self.client.login(username='searchuser', password='searchpassword')

        # Mocking api_search (googlesearch.search)
        mock_urls = [f'http://result{i}.com' for i in range(1, 7)] # 6 results
        mock_api_search.return_value = mock_urls

        # Mocking get_title_from_url
        def title_side_effect(url):
            return f"Title for {url}"
        mock_get_title.side_effect = title_side_effect

        # Initial POST to set the search query in session (Paginated by 5, so 2 pages for 6 results)
        self.client.post(self.search_url, {'query': 'paginated C++ query'})
        self.assertEqual(self.client.session.get('search_query'), 'paginated C++ query')
        mock_api_search.assert_called_with('paginated C++ query', num_results=20, lang='en', stop=20, pause=1.0)
        self.assertEqual(mock_get_title.call_count, 6) # Called for each of the 6 URLs
        mock_api_search.reset_mock()
        mock_get_title.reset_mock()

        # GET request for page 2
        mock_api_search.return_value = mock_urls # Reset mock for the GET call
        mock_get_title.side_effect = title_side_effect # Reset side_effect for the GET call
        response_page2 = self.client.get(self.search_url, {'page': '2'}) # Query from session

        self.assertEqual(response_page2.status_code, 200)
        self.assertTemplateUsed(response_page2, 'search.html')
        self.assertIn('results_page', response_page2.context)

        results_on_page2 = response_page2.context['results_page']
        self.assertEqual(len(results_on_page2.object_list), 1) # 1 result on page 2 (6 total, 5 per page)
        self.assertEqual(results_on_page2.object_list[0]['url'], 'http://result6.com')
        self.assertEqual(results_on_page2.object_list[0]['title'], 'Title for http://result6.com')
        self.assertEqual(results_on_page2.number, 2)
        self.assertEqual(results_on_page2.paginator.num_pages, 2)
        self.assertEqual(self.client.session.get('page'), '2')

        mock_api_search.assert_called_once_with('paginated C++ query', num_results=20, lang='en', stop=20, pause=1.0)
        self.assertEqual(mock_get_title.call_count, 6)


    @patch('accounts.views.get_title_from_url')
    @patch('accounts.views.search')
    def test_new_search_clears_old_pagination(self, mock_api_search, mock_get_title):
        self.client.login(username='searchuser', password='searchpassword')

        # Mock for first search
        mock_api_search.return_value = [f'http://old_result{i}.com' for i in range(1, 7)] # 6 results
        mock_get_title.side_effect = lambda url: f"Old Title for {url}"

        # First search, and simulate going to page 2
        self.client.post(self.search_url, {'query': 'old query'})
        self.client.get(self.search_url, {'page': '2'}) # query from session
        self.assertEqual(self.client.session.get('search_query'), 'old query')
        self.assertEqual(self.client.session.get('page'), '2')

        # Reset mocks for new search
        mock_api_search.reset_mock()
        mock_get_title.reset_mock()
        mock_api_search.return_value = [f'http://new_result{i}.com' for i in range(1, 3)] # 2 results for new query
        mock_get_title.side_effect = lambda url: f"New Title for {url}"

        # New search (POST)
        response_new_search = self.client.post(self.search_url, {'query': 'new query'})
        self.assertEqual(self.client.session.get('search_query'), 'new query')
        self.assertNotIn('page', self.client.session, "Page number should be cleared on new POST search")

        self.assertEqual(response_new_search.status_code, 200)
        results_page = response_new_search.context['results_page']
        self.assertEqual(results_page.number, 1) # Should be on page 1 of new results
        self.assertEqual(len(results_page.object_list), 2)
        self.assertEqual(results_page.object_list[0]['url'], 'http://new_result1.com')
        self.assertEqual(results_page.object_list[0]['title'], 'New Title for http://new_result1.com')

        mock_api_search.assert_called_once_with('new query', num_results=20, lang='en', stop=20, pause=1.0)
        self.assertEqual(mock_get_title.call_count, 2)

    # Adjust existing search tests to mock get_title_from_url and check for new result structure
    @patch('accounts.views.get_title_from_url')
    @patch('accounts.views.search')
    def test_search_with_results_post_detailed(self, mock_api_search, mock_get_title): # Renamed from test_search_with_results_post
        self.client.login(username='searchuser', password='searchpassword')
        mock_api_search.return_value = ['http://result1.com', 'http://result2.com']
        mock_get_title.side_effect = lambda url: f"Title for {url}"

        response = self.client.post(self.search_url, {'query': 'test query'})

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'search.html')
        self.assertIn('results_page', response.context)
        results_list = response.context['results_page'].object_list
        self.assertEqual(len(results_list), 2)
        self.assertEqual(results_list[0]['url'], 'http://result1.com')
        self.assertEqual(results_list[0]['title'], 'Title for http://result1.com')
        mock_api_search.assert_called_once_with('test query', num_results=20, lang='en', stop=20, pause=1.0)
        self.assertEqual(mock_get_title.call_count, 2)
        self.assertIsNone(response.context.get('error_message'))

    @patch('accounts.views.get_title_from_url')
    @patch('accounts.views.search')
    def test_search_with_no_results_post_detailed(self, mock_api_search, mock_get_title): # Renamed
        self.client.login(username='searchuser', password='searchpassword')
        mock_api_search.return_value = []
        # mock_get_title won't be called if no URLs

        response = self.client.post(self.search_url, {'query': 'obscure query'})

        self.assertEqual(response.status_code, 200)
        # results_page can be an empty list or Paginator object with empty list
        self.assertTrue(hasattr(response.context.get('results_page'), 'object_list') and not response.context.get('results_page').object_list or not response.context.get('results_page'))
        self.assertIsNone(response.context.get('error_message'))
        self.assertEqual(mock_get_title.call_count, 0)

    @patch('accounts.views.get_title_from_url')
    @patch('accounts.views.search')
    def test_search_with_library_error_post_detailed(self, mock_api_search, mock_get_title): # Renamed
        self.client.login(username='searchuser', password='searchpassword')
        mock_api_search.side_effect = Exception("Simulated search library error")
        # mock_get_title won't be called

        response = self.client.post(self.search_url, {'query': 'error query'})

        self.assertEqual(response.status_code, 200)
        self.assertTrue(hasattr(response.context.get('results_page'), 'object_list') and not response.context.get('results_page').object_list or not response.context.get('results_page'))
        self.assertIn('error_message', response.context)
        self.assertIn("An error occurred during the search", response.context['error_message'])
        self.assertEqual(mock_get_title.call_count, 0)
