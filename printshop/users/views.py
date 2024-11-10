# views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate
from django.contrib.auth.decorators import login_required
from .forms import StudentRegistrationForm, OwnerRegistrationForm, UserRegistrationForm, FileUploadForm
from .models import OwnerProfile, PrintRequest
from PyPDF2 import PdfReader 
from django.contrib import messages

def student_signup(request):
    if request.method == 'POST':
        form = StudentRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password'])  # Set the password after cleaning
            user.save()  # Save the user to the database
            
            print(f"User created: {user.username}")  # Debugging line
            
            # Optionally authenticate and log in the user immediately after signup
            user = authenticate(request, username=user.username, password=form.cleaned_data['password'])
            if user is not None:
                login(request, user)  # Log the user in immediately after signup
                print("User logged in")  # Debugging line
                
            return redirect('login')  # After saving, redirect to the login page
        else:
            print("Form is not valid")  # If the form is not valid, print an error
            
    else:
        form = StudentRegistrationForm()
    
    return render(request, 'student_signup.html', {'form': form})




def owner_signup(request):
    if request.method == 'POST':
        user_form = UserRegistrationForm(request.POST)
        owner_form = OwnerRegistrationForm(request.POST)
        if user_form.is_valid() and owner_form.is_valid():
            user = user_form.save(commit=False)
            user.set_password(user_form.cleaned_data['password'])
            user.save()

            owner_profile = owner_form.save(commit=False)
            owner_profile.user = user
            owner_profile.save()

            return redirect('login')
    else:
        user_form = UserRegistrationForm()
        owner_form = OwnerRegistrationForm()

    return render(request, 'owner_signup.html', {
        'user_form': user_form,
        'owner_form': owner_form,
    })

def user_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            # Redirect based on whether it's an owner or student
            return redirect('owner_dashboard' if hasattr(user, 'ownerprofile') else 'student_dashboard')
        else:
            messages.error(request, 'Invalid credentials')  # Better error handling using messages framework
            return render(request, 'login.html')  # Passing error message to the template

    return render(request, 'login.html')

@login_required
def student_dashboard(request):
    shops = OwnerProfile.objects.all()
    return render(request, 'student_dashboard.html', {'shops': shops})

@login_required
def owner_dashboard(request):
    owner = request.user.ownerprofile
    print_requests = PrintRequest.objects.filter(shop=owner)
    return render(request, 'owner_dashboard.html', {'print_requests': print_requests})

@login_required
def upload_file(request, shop_id):
    shop = get_object_or_404(OwnerProfile, id=shop_id)
    
    if request.method == 'POST':
        form = FileUploadForm(request.POST, request.FILES)
        if form.is_valid():
            print_request = form.save(commit=False)
            print_request.shop = shop
            print_request.student = request.user
            uploaded_file = request.FILES['file']
            
            print_request.file.save(uploaded_file.name, uploaded_file)  # Ensure the file saves in media
            
            # Calculate page count if it's a PDF file
            if uploaded_file.name.endswith('.pdf'):
                pdf_reader = PdfReader(uploaded_file)
                print_request.pages = len(pdf_reader.pages)
            else:
                print_request.pages = 1  # Default for non-PDF or uncountable files

            print_request.save()
            return redirect('student_dashboard')
    else:
        form = FileUploadForm()
    
    return render(request, 'upload_file.html', {'form': form, 'shop': shop})




