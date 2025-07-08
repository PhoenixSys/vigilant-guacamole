from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User
from .forms import RegistrationForm
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

@staff_member_required
def admin_dashboard(request):
    pending_users = User.objects.filter(is_active=False)
    return render(request, 'admin/dashboard.html', {'pending_users': pending_users})

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

@login_required
def search_view(request):
    results = []
    query = ""
    if request.method == 'POST':
        query = request.POST.get('query', '')
        if query:
            try:
                # Limit to 20 results for performance
                results = list(search(query, num_results=20))
            except Exception as e:
                # Handle potential search errors
                results = [f"An error occurred: {e}"]
    return render(request, 'search.html', {'results': results, 'query': query})

