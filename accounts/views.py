from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User
from .forms import RegistrationForm, UserUpdateForm, UserProfileForm # Added forms
from .models import UserProfile # Added UserProfile model
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from googlesearch import search

def register(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('pending_approval')
    else:
        form = RegistrationForm()
    return render(request, 'registration/register.html', {'form': form})

def pending_approval(request):
    return render(request, 'registration/pending_approval.html')

@login_required
def home(request):
    return render(request, 'home.html')

@login_required
def login_redirect(request):
    if request.user.is_staff:
        return redirect('admin_dashboard')
    else:
        return redirect('home')

from django.db.models import Q # For searching

@staff_member_required
def admin_dashboard(request):
    pending_users_qs = User.objects.filter(is_active=False)

    # Search/Filter
    search_query = request.GET.get('q', '').strip()
    if search_query:
        pending_users_qs = pending_users_qs.filter(
            Q(username__icontains=search_query) |
            Q(email__icontains=search_query)
        )

    # Sorting
    sort_by = request.GET.get('sort', 'date_joined') # Default sort by date_joined
    allowed_sort_fields = ['username', 'email', 'date_joined']

    if sort_by not in allowed_sort_fields:
        sort_by = 'date_joined' # Default to date_joined if invalid sort param

    order = request.GET.get('order', 'asc') # Default order asc
    if order == 'desc':
        sort_by_final = f'-{sort_by}'
    else:
        sort_by_final = sort_by
        order = 'asc' # Ensure order is 'asc' if not 'desc'

    pending_users_qs = pending_users_qs.order_by(sort_by_final)

    # Pagination for admin dashboard (good practice if many pending users)
    paginator = Paginator(pending_users_qs, 15) # Show 15 users per page
    page_number = request.GET.get('page')
    try:
        pending_users_page = paginator.page(page_number)
    except PageNotAnInteger:
        pending_users_page = paginator.page(1)
    except EmptyPage:
        pending_users_page = paginator.page(paginator.num_pages)

    context = {
        'pending_users_page': pending_users_page,
        'current_sort': sort_by,
        'current_order': order,
        'search_query': search_query,
        'page_title': "Admin Dashboard - User Approvals"
    }
    return render(request, 'admin/dashboard.html', context)

@staff_member_required
def approve_user(request, user_id):
    user = get_object_or_404(User, pk=user_id)
    user.is_active = True
    user.save()
    return redirect('admin_dashboard')

@staff_member_required
def reject_user(request, user_id):
    user = get_object_or_404(User, pk=user_id)
    user.delete()
    return redirect('admin_dashboard')

import requests
from bs4 import BeautifulSoup
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

# Helper function to get title from URL
def get_title_from_url(url):
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        response = requests.get(url, headers=headers, timeout=5, allow_redirects=True)
        response.raise_for_status() # Raise an exception for HTTP errors
        soup = BeautifulSoup(response.content, 'html.parser')
        title_tag = soup.find('title')
        return title_tag.string.strip() if title_tag and title_tag.string else "No title found"
    except requests.exceptions.RequestException as e:
        # Log e for debugging
        # print(f"Error fetching {url}: {e}")
        return "Could not fetch title"
    except Exception: # Catch other parsing errors
        return "Error parsing title"


@login_required
def search_view(request):
    processed_results = [] # Will store list of {'url': ..., 'title': ...}
    query = ""
    error_message = None
    results_page_obj = [] # Ensure results_page_obj is defined

    if request.method == 'POST':
        query = request.POST.get('query', '').strip()
        if query:
            request.session['search_query'] = query
            request.session.pop('page', None) # Clear page on new search
        else:
            request.session.pop('search_query', None)
            if 'query' in request.POST:
                error_message = "Please enter a search term."
            return render(request, 'search.html', {'query': query, 'error_message': error_message, 'results_page': results_page_obj, 'page_title': 'Web Search'})

    elif request.method == 'GET':
        query = request.session.get('search_query', '').strip()
        page_number_from_get = request.GET.get('page')
        if page_number_from_get:
            request.session['page'] = page_number_from_get

    if query:
        try:
            # Fetch raw URLs from googlesearch
            raw_urls = list(search(query, num_results=20, lang='en', stop=20, pause=1.0)) # Reduced num_results, added pause

            # Process URLs to get titles (this can be slow)
            # For a better UX, this part could be done asynchronously or titles fetched on demand.
            # For simplicity now, fetching directly.
            for url in raw_urls:
                title = get_title_from_url(url)
                processed_results.append({'url': url, 'title': title})

        except ImportError:
            error_message = "Search library is not configured correctly. Please contact support."
        except Exception as e:
            error_message = f"An error occurred during the search: {str(e)}. This could be due to network issues or search restrictions. Please try again later."
            # Consider logging 'e' here: logger.error(...)

    if processed_results:
        paginator = Paginator(processed_results, 5) # Show 5 detailed results per page
        page_to_display = request.session.get('page', 1) # Get page from session or default to 1
        try:
            results_page_obj = paginator.page(page_to_display)
        except PageNotAnInteger:
            results_page_obj = paginator.page(1)
            request.session['page'] = 1
        except EmptyPage:
            results_page_obj = paginator.page(paginator.num_pages)
            request.session['page'] = paginator.num_pages

    # Update page in session for next GET request if it changed
    if results_page_obj and hasattr(results_page_obj, 'number'):
         request.session['page'] = results_page_obj.number


    return render(request, 'search.html', {
        'results_page': results_page_obj,
        'query': query,
        'error_message': error_message,
        'page_title': 'Web Search'
    })

@login_required
def profile_view_edit(request):
    user_form_initial = {
        'username': request.user.username,
        'email': request.user.email,
        'first_name': request.user.first_name,
        'last_name': request.user.last_name,
    }
    # Ensure profile exists, though the signal should handle this.
    profile, created = UserProfile.objects.get_or_create(user=request.user)

    if request.method == 'POST':
        user_form = UserUpdateForm(request.POST, instance=request.user)
        profile_form = UserProfileForm(request.POST, request.FILES, instance=profile)

        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            # Add success message
            from django.contrib import messages # Import messages framework
            messages.success(request, 'Your profile has been updated successfully!')
            return redirect('profile_view_edit') # Redirect to the same page to show updated info & message
        else:
            # Add error message (optional, as forms will display field-specific errors)
            from django.contrib import messages
            messages.error(request, 'Please correct the errors below.')
    else:
        user_form = UserUpdateForm(instance=request.user, initial=user_form_initial)
        profile_form = UserProfileForm(instance=profile)

    context = {
        'user_form': user_form,
        'profile_form': profile_form,
        'page_title': 'Edit Your Profile' # For the template
    }
    return render(request, 'accounts/profile_edit.html', context)