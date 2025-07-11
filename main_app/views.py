import json
import requests
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render, reverse
from django.views.decorators.csrf import csrf_exempt

from .EmailBackend import EmailBackend
from .models import Attendance, Session, Subject

# Create your views here.


from django.contrib.auth import authenticate, login

def login_page(request):
    if request.user.is_authenticated:
        if request.user.user_type == '1':
            return redirect(reverse("admin_home"))
        elif request.user.user_type == '2':
            return redirect(reverse("staff_home"))
        else:
            return redirect(reverse("student_home"))

    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            # Redirect based on user type
            if user.user_type == '1':
                return redirect(reverse("admin_home"))
            elif user.user_type == '2':
                return redirect(reverse("staff_home"))
            else:
                return redirect(reverse("student_home"))
        else:
            return render(request, "main_app/login.html", {"error": "Invalid credentials"})

    return render(request, "main_app/login.html")





def doLogin(request, **kwargs):
    if request.method != 'POST':
        return HttpResponse("<h4>Denied</h4>")

    email = request.POST.get('email').strip().lower()  # Ensure consistency
    password = request.POST.get('password')

    user = EmailBackend().authenticate(username=email, password=password)  # No request argument
    print("User object:", user)  # Debugging output

    if user is not None:
        login(request, user)

        # Redirect based on user type
        if user.user_type == '1':
            return redirect(reverse("admin_home"))
        elif user.user_type == '2':
            return redirect(reverse("staff_home"))
          
        else:
            return redirect(reverse("student_home"))
    else:
        messages.error(request, "Invalid details")
        return redirect("/")






def logout_user(request):
    if request.user != None:
        logout(request)
    return redirect("/")


@csrf_exempt
def get_attendance(request):
    subject_id = request.POST.get('subject')
    session_id = request.POST.get('session')
    try:
        subject = get_object_or_404(Subject, id=subject_id)
        session = get_object_or_404(Session, id=session_id)
        attendance = Attendance.objects.filter(subject=subject, session=session)
        attendance_list = []
        for attd in attendance:
            data = {
                    "id": attd.id,
                    "attendance_date": str(attd.date),
                    "session": attd.session.id
                    }
            attendance_list.append(data)
        return JsonResponse(json.dumps(attendance_list), safe=False)
    except Exception as e:
        return None


def showFirebaseJS(request):
    data = """
    // Give the service worker access to Firebase Messaging.
    // Note that you can only use Firebase Messaging here, other Firebase libraries
    // are not available in the service worker.
    importScripts('https://www.gstatic.com/firebasejs/7.22.1/firebase-app.js');
    importScripts('https://www.gstatic.com/firebasejs/7.22.1/firebase-messaging.js');

    // Initialize the Firebase app in the service worker by passing in
    // your app's Firebase config object.
    // https://firebase.google.com/docs/web/setup#config-object
    firebase.initializeApp({
        apiKey: "AIzaSyBarDWWHTfTMSrtc5Lj3Cdw5dEvjAkFwtM",
        authDomain: "sms-with-django.firebaseapp.com",
        databaseURL: "https://sms-with-django.firebaseio.com",
        projectId: "sms-with-django",
        storageBucket: "sms-with-django.appspot.com",
        messagingSenderId: "945324593139",
        appId: "1:945324593139:web:03fa99a8854bbd38420c86",
        measurementId: "G-2F2RXTL9GT"
    });

    // Retrieve an instance of Firebase Messaging so that it can handle background
    // messages.
    const messaging = firebase.messaging();
    messaging.setBackgroundMessageHandler(function (payload) {
        const notification = JSON.parse(payload);
        const notificationOption = {
            body: notification.body,
            icon: notification.icon
        }
        return self.registration.showNotification(payload.notification.title, notificationOption);
    });
    """
    return HttpResponse(data, content_type='application/javascript')
import json
from django.http import JsonResponse
from django.core.mail import send_mail
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings

@csrf_exempt  # Allows AJAX requests without CSRF token
def send_student_result(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body.decode("utf-8")) 
        except json.JSONDecodeError:
            return JsonResponse({"error": "Invalid JSON data"}, status=400)

        email = data.get("email")
        test_score = data.get("test")
        exam_score = data.get("exam")

        if not email or not test_score or not exam_score:
            return JsonResponse({"error": "Missing required fields"}, status=400)

        subject = "Academic Performance Report  Your Ward's Results"

        message = f"""
        Dear Guardian,

        We are pleased to share the academic performance details of your ward. Please find the results below:

        📌 **Internal Assessment :** {test_score} / 100  
        📌 **Final Examination :** {exam_score} / 600  

        🔹 **Overall Performance:**  
        Your ward has shown dedication and effort in their studies. We encourage them to keep up the good work and strive for continuous improvement.  

        If you have any questions regarding these results or need further clarification, please feel free to reach out to us. We are always here to support your child’s academic journey.  

        ✨ **Stay connected for further updates.**  

        Best regards,  
        **Modern College of Professional Studies**  
        📧 Contact us: [modercollege1@gmail.com]  
        📞 Helpline: [+91 9711149573]  
        🌐 Website: [ https://moderncollege.org/]  
        📍 Address: [Anand Industrial Estate, Mohan Nagar, Ghaziabad - 201007, Uttar Pradesh, India]\n(https://www.google.com/maps/place/Anand+Industrial+Estate,+Mohan+Nagar,+Ghaziabad+-+201007,+Uttar+Pradesh,+India)

        """


        sender_email = settings.EMAIL_HOST_USER  # Uses settings instead of hardcoded email

        try:
            send_mail(subject, message, sender_email, [email], fail_silently=False)
            return JsonResponse({"message": "Email sent successfully!"})
        except Exception as e:
            return JsonResponse({"error": f"Failed to send email: {str(e)}"}, status=500)

    return JsonResponse({"error": "Invalid request"}, status=400)



from .models import LostAndFound, Course

def lost_and_found(request):
    if request.method == "POST":
        name = request.POST.get("name")
        course_id = request.POST.get("course")
        identity = request.POST.get("identity")
        description = request.POST.get("description")
        image = request.FILES.get("image")

        course = Course.objects.get(id=course_id)

        LostAndFound.objects.create(
            name=name,
            course=course,
            identity=identity,
            description=description,
            image=image
        )

        return redirect("lost_and_found")

    lost_items = LostAndFound.objects.all()
    courses = Course.objects.all()
    
    return render(request, "main_app/lost_and_found.html", {"lost_items": lost_items, "courses": courses})


from django.contrib.auth.decorators import login_required, user_passes_test

def update_description(request):
    if request.method == "POST":
        item_id = request.POST.get('item_id')
        new_description = request.POST.get('new_description')

        item = get_object_or_404(LostAndFound, id=item_id)
        item.description = new_description  # Update description
        item.save()

        return JsonResponse({"success": True, "new_description": new_description})
    
    return JsonResponse({"success": False})

def is_admin(user):
    return user.is_superuser


@user_passes_test(is_admin)  # Only admin can delete

def delete_item(request, item_id):
    item = get_object_or_404(LostAndFound, id=item_id)
    item.delete()
    return redirect('lost_and_found')  # Redirect to the same page

# payment of studnets
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import StudentPayment
from main_app.models import Student  # Assuming Student model is in `main_app`



@login_required
def student_payment(request):
    try:
        student = Student.objects.get(admin=request.user)  # Get student profile
        course = student.course  # Get student’s course
    except Student.DoesNotExist:
        messages.error(request, "Student profile not found.")
        return redirect('student_home')

    if request.method == "POST":
        transaction_id = request.POST.get("transaction_id")
        amount = request.POST.get("amount")

        if transaction_id and amount:
            StudentPayment.objects.create(
                student=request.user,
                course=course,
                transaction_id=transaction_id,
                amount=amount
            )
            messages.success(request, "Payment recorded successfully!")
            return redirect('student_home')

        messages.error(request, "Please enter a valid transaction ID and amount.")

    return render(request, "student_template/payment.html", {
        "student": student,
        "course": course,
        "qr_code_url": "/static/qr_code.png"

        
    })

import razorpay
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json

@csrf_exempt  # Allow AJAX requests
def create_order(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)  # Parse JSON from frontend
            amount = int(data.get("amount", 500)) * 100  # Convert ₹500 → 50000 paise

            # Razorpay client setup
            client = razorpay.Client(auth=("rzp_test_AewwYpDdKjarAy", "RXZM8vnr240IYxkn9sXb2nkk"))
            
            order = client.order.create({
                "amount": amount,
                "currency": "INR",
                "payment_capture": "1"
            })
            

            print("Order Created:", order)  # Debugging
            return JsonResponse({"order_id": order["id"]})  # Return JSON

        except Exception as e:
            print("Error:", str(e))  # Debugging
            return JsonResponse({"error": str(e)}, status=500)

    return JsonResponse({"error": "Invalid request"}, status=400)

@csrf_exempt
def verify_payment(request):
    if request.method == "POST":
        data = request.POST
        razorpay_payment_id = data.get("razorpay_payment_id")
        razorpay_order_id = data.get("razorpay_order_id")
        razorpay_signature = data.get("razorpay_signature")

        # Verify signature
        params_dict = {
            "razorpay_order_id": razorpay_order_id,
            "razorpay_payment_id": razorpay_payment_id,
            "razorpay_signature": razorpay_signature,
        }

        try:
            client.utility.verify_payment_signature(params_dict)
            return JsonResponse({"message": "Payment verified successfully"})
        except razorpay.errors.SignatureVerificationError:
            return JsonResponse({"error": "Payment verification failed"}, status=400)
    
    return JsonResponse({"error": "Invalid request"}, status=400)



def admin_payment_dashboard(request):
    payments = StudentPayment.objects.select_related('student', 'course').all()
    return render(request, 'hod_template/admin_payment_dashboard.html', {'payments': payments})





@login_required
def library_home(request):
    return render(request, "library_template/library_home.html")
