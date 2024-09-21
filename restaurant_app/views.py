from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from .models import *
import csv
from django.utils import timezone
from django.shortcuts import get_object_or_404
from django.contrib.auth.models import User
from django.shortcuts import render, redirect
from django.contrib import messages
from django.http import HttpResponse
from reportlab.pdfgen import canvas
from django.contrib.auth import update_session_auth_hash
from reportlab.lib.pagesizes import A4

def register(request):
    if request.method == 'POST':
        first_name = request.POST['first_name']
        last_name = request.POST['last_name']
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']
        password_confirm = request.POST['password_confirm']
        
        # Check if username already exists
        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists. Please choose a different one.")
            return render(request, 'login.html')
        
        # Check if passwords match
        if password != password_confirm:
            messages.error(request, "Passwords do not match.")
            return render(request, 'login.html')

        # Create user
        user = User.objects.create_user(
            username=username,
            email=email,
            password=password,
            first_name=first_name,
            last_name=last_name
        )
        UserTable.objects.create(user=user, admin=False)
        messages.success(request, "Registration successful! You can now log in.")
        return redirect('login')  # Redirect after successful registration

    return render(request, 'login.html')  # Render registration page


# User Login
def login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        
        user = authenticate(request, username=username, password=password)

        if user is not None:
            auth_login(request, user)
            messages.success(request, f"Login successful! Welcome back, {user.username}.")
            
            # Check if the user is an admin
            try:
                user_table = UserTable.objects.get(user=user)
                if user_table.admin:
                    return redirect('admin_dashboard')  # Change to your admin dashboard URL
                else:
                    return redirect('dashboard')  # Change to your regular dashboard URL
            except UserTable.DoesNotExist:
                return redirect('dashboard')  # If user not found in UserTable, redirect to regular dashboard
        else:
            messages.error(request, "Invalid username or password. Please try again.")

    return render(request, 'login.html')


#............................................User Section........................................
# Dashboard
@login_required
def recommendations(request):
    restaurants = []
    if request.method == 'POST':
        location = request.POST['location'].lower()
        price = float(request.POST['price'])

        # Load restaurants data from CSV
        with open('zomato.csv', newline='', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                avg_cost = float(row['avg cost (two people)']) if row['avg cost (two people)'] else 0
                if location in row['area'].lower() and avg_cost <= price:
                    # Prepare restaurant data to display in the template
                    restaurant = {
                        'restaurant_name': row['restaurant name'],
                        'restaurant_type': row['restaurant type'],
                        'rate': float(row['rate (out of 5)']) if row['rate (out of 5)'] else 0,
                        'num_of_ratings': int(row['num of ratings']) if row['num of ratings'] else 0,
                        'avg_cost': avg_cost,
                        'online_order': row['online_order'],
                        'table_booking': row['table booking'],
                        'cuisines_type': row['cuisines type'],
                        'area': row['area'],
                        'local_address': row['local address'],
                        
                    }
                    restaurants.append(restaurant)

                    # Check if the entry already exists in UserHistory
                    existing_entry = UserHistory.objects.filter(
                        user=request.user,
                        restaurant_name=row['restaurant name'],
                        area=row['area']
                    ).exists()

                    if not existing_entry:
                        # Create a new UserHistory entry if it does not exist
                        UserHistory.objects.create(
                            user=request.user,
                            restaurant_name=row['restaurant name'],
                            restaurant_type=row['restaurant type'],
                            rate=float(row['rate (out of 5)']) if row['rate (out of 5)'] else 0,
                            num_of_ratings=int(row['num of ratings']) if row['num of ratings'] else 0,
                            avg_cost=avg_cost,
                            online_order=row['online_order'],
                            table_booking=row['table booking'],
                            cuisines_type=row['cuisines type'],
                            area=row['area'],
                            local_address=row['local address'],
                            interaction_datetime=timezone.now() 
                        )

    return render(request, 'dashboard.html', {'restaurants': restaurants})


# User History
@login_required
def history(request):
    user_history = UserHistory.objects.filter(user=request.user)

    # Get filter parameters from GET request
    price_range = request.GET.get('price_range')
    rating = request.GET.get('rating')
    restaurant_type = request.GET.get('restaurant_type')

    # Apply filters if present
    if price_range:
        try:
            price_limit = float(price_range)
            user_history = user_history.filter(avg_cost__lte=price_limit)
        except ValueError:
            pass  # Handle invalid float conversion gracefully

    if rating:
        user_history = user_history.filter(rate=rating)

    if restaurant_type:
        user_history = user_history.filter(restaurant_type=restaurant_type)

    return render(request, 'history.html', {'history': user_history})

# User Logout
@login_required
def logout(request):
    auth_logout(request)
    return redirect('/')


@login_required
def dashboard(request):
    return render(request,'base.html')


@login_required
def maindash(request):
    return render(request,'maindashboard.html')

@login_required
def about(request):
    return render(request,'about.html')

@login_required
def recommend(request):
    return render(request,'dashboard.html')


@login_required
def graph(request):
    if not request.user.is_authenticated:
        return redirect('login')  # Adjust the name of your login URL as necessary

    user_history = UserHistory.objects.filter(user=request.user)
    
    history_data = {
        'restaurant_names': [],
        'ratings': [],
        'average_costs': []
    }
    
    for history in user_history:
        history_data['restaurant_names'].append(history.restaurant_name)
        history_data['ratings'].append(history.rate)
        history_data['average_costs'].append(history.avg_cost)

    return render(request, 'graph.html', {'history_data': history_data})


def index(request):
    return render(request,'index.html')


def login_page(request):
    return render(request,'login.html')

@login_required
def contact_page(request):
    return render(request,'contact.html')

@login_required
def contact(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        subject = request.POST.get('subject')
        message = request.POST.get('message')

        # Create a new Contact instance and save it to the database
        contact = Contact(name=name, email=email, subject=subject, message=message)
        contact.save()

        # Add a success message
        messages.success(request, "Your message has been sent successfully!")
        return redirect('contact_page')  # Redirect to a success page
    return render(request, 'contact.html')  # Render the contact form



@login_required
def download_user_history(request):
    user = request.user
    history_entries = UserHistory.objects.filter(user=user)

    # Create a response object
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="user_search_history.pdf"'

    # Create a PDF canvas
    p = canvas.Canvas(response, pagesize=A4)
    width, height = A4

    # Define margins
    margin = 50

    # Add user details
    p.drawString(margin, height - margin, f"User: {user.username}")
    p.drawString(margin, height - margin - 20, f"Email: {user.email}")

    # Add a title
    p.drawString(margin, height - margin - 50, "Search History")

    # Table header
    y = height - margin - 80
    headers = [
        'Restaurant Name', 
        'Restaurant Type', 
        'Rating', 
        'Average Cost', 
        'Table Booking', 
        'Cuisines Type', 
    ]
    
    # Adjusted column widths for better fit
    column_widths = [150, 80, 50, 50, 80, 100]

    # Draw the headers
    for i, header in enumerate(headers):
        p.drawString(margin + sum(column_widths[:i]), y, header)

    # Add data rows
    y -= 20
    for entry in history_entries:
        p.drawString(margin, y, entry.restaurant_name[:column_widths[0] // 5])  # Truncate if too long
        p.drawString(margin + column_widths[0], y, entry.restaurant_type[:column_widths[1] // 5])  # Truncate if too long
        p.drawString(margin + sum(column_widths[:2]), y, str(entry.rate))
        p.drawString(margin + sum(column_widths[:3]), y, str(entry.avg_cost))
        p.drawString(margin + sum(column_widths[:4]), y, entry.table_booking)
        p.drawString(margin + sum(column_widths[:5]), y, entry.cuisines_type)
        y -= 20

    # Finalize and save the PDF
    p.showPage()
    p.save()

    return response

@login_required
def user_profile(request):
    user = request.user

    if request.method == 'POST':
        # Update user profile
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        email = request.POST.get('email')

        if first_name:
            user.first_name = first_name
        if last_name:
            user.last_name = last_name
        if email:
            user.email = email

        user.save()
        messages.success(request, "Profile updated successfully.")
        return redirect('user_profile')  # Redirect to the same page to avoid resubmission

    return render(request, 'user_profile.html', {'user': user})

@login_required
def change_password(request):
    user = request.user

    if request.method == 'POST':
        old_password = request.POST.get('old_password')
        new_password = request.POST.get('new_password')

        # Check if old password is correct
        if user.check_password(old_password):
            user.set_password(new_password)
            user.save()
            update_session_auth_hash(request, user)  # Keep user logged in
            messages.success(request, 'Password changed successfully.')
        else:
            messages.error(request, 'Old password is incorrect.')

        return redirect('user_profile')  # Redirect to the user profile page

    return redirect('user_profile')  # Redirect in case of a GET request


    
@login_required
def user_search(request):
    # Get the currently logged-in user
    current_user = request.user

    # Group by restaurant to calculate average ratings for the current user
    search_data = (
        UserHistory.objects
        .filter(user=current_user)  # Filter for the current user
        .values('restaurant_name')
        .annotate(avg_rating=models.Avg('rate'))
        .order_by('-avg_rating')  # Order by average rating in descending order
        [:100]  # Limit to top 100 restaurants
    )

    # Prepare data for the graph
    restaurant_labels = list(set(item['restaurant_name'] for item in search_data))
    
    # Create a dictionary to hold ratings for the current user
    graph_data = {
        current_user.username: [0] * len(restaurant_labels)
    }

    for item in search_data:
        restaurant = item['restaurant_name']
        avg_rating = item['avg_rating']
        restaurant_index = restaurant_labels.index(restaurant)
        graph_data[current_user.username][restaurant_index] = avg_rating

    return render(request, 'current_search_graph.html', {
        'user_labels': [current_user.username],  # Only include the current user's label
        'restaurant_labels': restaurant_labels,
        'graph_data': graph_data,
    })


#.................................End...........................................


# ...........................Admin Section.........................................
@login_required
def admin_dashboard(request):
    return render(request,'admindashboard.html')

@login_required
def all_users(request):
    # Fetch all users who are not admins
    non_admin_users = UserTable.objects.filter(admin=False).select_related('user')  # Use select_related for optimized queries
    return render(request, 'all_users.html', {'users': non_admin_users})

@login_required
def update_user(request, user_id):
    user_table = get_object_or_404(UserTable, id=user_id)
    
    if request.method == 'POST':
        user_table.user.username = request.POST['username']
        user_table.user.first_name = request.POST['first_name']
        user_table.user.last_name = request.POST['last_name']
        user_table.user.email = request.POST['email']
        user_table.user.save()
        messages.success(request, f"User updated successfully , {user_table.user.username}")
        return redirect('all_users')

    return render(request, 'all_users.html', {'users': UserTable.objects.all()})

@login_required
def delete_user(request, user_id):
    user_table = get_object_or_404(UserTable, id=user_id)
    user_table.user.delete()  # Delete the associated User object
    user_table.delete()  # Delete the UserTable object
    messages.success(request, "User deleted successfully.")
    return redirect('all_users')

@login_required
def all_searched_restaurants(request):
    # Fetch unique searched restaurants
    searched_restaurants = UserHistory.objects.values('restaurant_name', 'restaurant_type', 'avg_cost', 'rate','local_address').distinct()

    # Filtering logic
    price_filter = request.GET.get('price_range')
    rating_filter = request.GET.get('rating')
    type_filter = request.GET.get('restaurant_type')

    # Apply filters based on the provided GET parameters
    if price_filter:
        searched_restaurants = searched_restaurants.filter(avg_cost__lte=float(price_filter))

    if rating_filter:
        searched_restaurants = searched_restaurants.filter(rate=rating_filter)

    if type_filter:
        searched_restaurants = searched_restaurants.filter(restaurant_type=type_filter)

    return render(request, 'all_searched_restaurants.html', {
        'searched_restaurants': searched_restaurants,
        'price_range': price_filter,
        'rating': rating_filter,
        'restaurant_type': type_filter,
    })


@login_required
def user_search_graph(request):
    # Group by user and restaurant to calculate average ratings, limiting to top 100
    search_data = (
        UserHistory.objects
        .values('user__username', 'restaurant_name')
        .annotate(avg_rating=models.Avg('rate'))
        .order_by('-avg_rating')[:100]  # Order by average rating and take top 100
    )

    # Prepare data for the graph
    user_labels = list(set(item['user__username'] for item in search_data))
    restaurant_labels = list(set(item['restaurant_name'] for item in search_data))
    
    # Create a dictionary to hold ratings for each user
    graph_data = {user: [0] * len(restaurant_labels) for user in user_labels}

    for item in search_data:
        user = item['user__username']
        restaurant = item['restaurant_name']
        avg_rating = item['avg_rating']
        restaurant_index = restaurant_labels.index(restaurant)
        graph_data[user][restaurant_index] = avg_rating

    return render(request, 'user_search_graph.html', {
        'user_labels': user_labels,
        'restaurant_labels': restaurant_labels,
        'graph_data': graph_data,
    })
    
    
@login_required
def all_contacts(request):
    contacts = Contact.objects.all()  # Get all contact entries
    return render(request, 'all_contacts.html', {'contacts': contacts})
#...........................End.......................................
