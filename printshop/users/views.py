# views.py
import os
from django.conf import settings
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate
from django.contrib.auth.decorators import login_required
from .forms import StudentRegistrationForm, OwnerRegistrationForm, UserRegistrationForm, FileUploadForm
from .models import OwnerProfile, PrintRequest
from PyPDF2 import PdfReader 
from django.contrib import messages
from .forms import PrintCostForm
from .models import PrintCostConfig
from django.core.files.storage import FileSystemStorage


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
    return render(request, 'owner_dashboard.html', {'print_requests': print_requests,'owner': owner})


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
            print_request.file = uploaded_file  # Set the file directly

            # Calculate page count if it's a PDF file
            if uploaded_file.name.endswith('.pdf'):
                pdf_reader = PdfReader(uploaded_file)
                print_request.pages = len(pdf_reader.pages)
            else:
                print_request.pages = 1  # Default for non-PDF or uncountable files

            print_request.save()  # Save the PrintRequest with the file

            # Redirect to the cost estimation page
            return redirect('cost_estimation', shop_id=shop.id)
    else:
        form = FileUploadForm()
    
    return render(request, 'upload_file.html', {'form': form, 'shop': shop})


    

def cost_estimation(request, shop_id):
    shop = get_object_or_404(OwnerProfile, id=shop_id)
    # Retrieve the print cost for the shop
    print_cost_config = shop.printcostconfig

    # Get the number of pages from the uploaded file
    print_request = PrintRequest.objects.filter(shop=shop, student=request.user).last()
    page_count = print_request.pages
    total_cost = page_count * print_cost_config.black_white_print_cost  # Default: Black & White print cost

    # Display the cost estimation
    return render(request, 'cost_estimation.html', {
        'shop': shop,
        'page_count': page_count,
        'total_cost': total_cost,
        'print_cost_config': print_cost_config
    })
 
 
@login_required
def configure_print_cost(request):
    # Get or create the PrintCostConfig for the owner
    owner = request.user.ownerprofile
    print_cost_config, created = PrintCostConfig.objects.get_or_create(owner=owner)

    if request.method == 'POST':
        form = PrintCostForm(request.POST, instance=print_cost_config)
        if form.is_valid():
            form.save()
            messages.success(request, 'Print cost settings saved successfully.')
            return redirect('owner_dashboard')
    else:
        form = PrintCostForm(instance=print_cost_config)

    return render(request, 'configure_print_cost.html', {'form': form})   








import stripe
from django.conf import settings
from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.urls import reverse
from .models import PrintRequest, OwnerProfile

stripe.api_key = settings.STRIPE_SECRET_KEY

from django.views.decorators.http import require_POST

@require_POST
@login_required
def payment_gateway(request, shop_id):
    shop = get_object_or_404(OwnerProfile, id=shop_id)
    print_request = PrintRequest.objects.filter(shop=shop, student=request.user).last()
    total_cost = print_request.pages * shop.printcostconfig.black_white_print_cost

    # Create a Stripe Checkout session
    session = stripe.checkout.Session.create(
        payment_method_types=['card'],
        line_items=[{
            'price_data': {
                'currency': 'usd',
                'product_data': {
                    'name': f"Printing at {shop.shop_name}",
                },
                'unit_amount': int(total_cost * 100),  # Stripe expects amount in cents
            },
            'quantity': 1,
        }],
        mode='payment',
        success_url=request.build_absolute_uri(reverse('payment_success')) + '?session_id={CHECKOUT_SESSION_ID}',
        cancel_url=request.build_absolute_uri(reverse('payment_cancel')),
    )

    # Return only the session ID and public key to the client
    return JsonResponse({'session_id': session.id, 'stripe_public_key': settings.STRIPE_PUBLIC_KEY})




@login_required
def payment_success(request):
    messages.success(request, "Payment was successful. Your order has been placed!")
    return render(request, 'payment_success.html')

@login_required
def payment_cancel(request):
    messages.error(request, "Payment was canceled. You can try again.")
    return render(request, 'payment_cancel.html')

def create_checkout_session(request):
    # Create a Stripe Checkout session
    session = stripe.checkout.Session.create(
        payment_method_types=['card'],  # Payment method types
        line_items=[                  # Define the products/items to be purchased
            {
                'price_data': {
                    'currency': 'usd',
                    'product_data': {
                        'name': 'Print Order',
                    },
                    'unit_amount': 2000,  # Price in cents ($20.00)
                },
                'quantity': 1,
            },
        ],
        mode='payment',
        success_url=request.build_absolute_uri(reverse('payment_success')) + '?session_id={CHECKOUT_SESSION_ID}',
        cancel_url=request.build_absolute_uri(reverse('payment_cancel')),  # This is the cancel URL
    )

    # Redirect the user to the Stripe Checkout page
    return redirect(session.url, code=303)