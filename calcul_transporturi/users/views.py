

from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required,user_passes_test
from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import send_mail
from django.conf import settings
from django.shortcuts import render, get_object_or_404,redirect
from django.http import HttpResponse
from django.utils import timezone

from .models import CustomUser
from .constants import TOKEN_LIFETIME
from .forms import RegistrationForm
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
import uuid

def staff_required(user):
    return user.is_staff


EMAIL_HOST_USER = settings.EMAIL_HOST_USER


def activate(request, token):
    user = get_object_or_404(CustomUser, verification_token=token)

    # Verifică dacă tokenul a expirat
    if user.token_created < timezone.now() - TOKEN_LIFETIME:
        # Afișează un mesaj cu un link pentru a solicita un nou token
        current_site = get_current_site(request)
        resend_link = f"http://{current_site.domain}:8000/users/resend_activation_email/{user.id}/"
        return render(request, 'token_expired.html', {
            'message': 'Tokenul a expirat. Poți solicita un nou token.',
            'resend_link': resend_link
        })

    # Dacă tokenul este valid și nu a fost utilizat
    if user.verification_token is None or user.token_used:
        return HttpResponse('Tokenul a fost deja folosit sau este invalid.')

    user.email_verified = True
    user.verification_token = uuid.uuid4()
    user.token_used = True
    user.save()
    return HttpResponse('Email verificat cu succes!')

def resend_activation_email(request, user_id):
    user = get_object_or_404(CustomUser, id=user_id)
    if not user.email_verified:
        user.verification_token = uuid.uuid4()
        user.token_created = timezone.now()
        user.save()

        # Trimiteți email-ul de activare din nou
        current_site = get_current_site(request)
        email_subject = 'Confirmare Email'
        email_body = (
            f'Verifică-ți email-ul folosind următorul link: http://{current_site.domain}:8000/users/activate/{user.verification_token}/\n'
        )
        send_mail(email_subject, email_body, settings.EMAIL_HOST_USER, [user.email], fail_silently=False)

        return HttpResponse('Un nou email de activare a fost trimis!')

    return HttpResponse('Utilizatorul este deja verificat.')

def register(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password'])
            user.verification_token = uuid.uuid4()
            user.token_created = timezone.now()

            # Verifică tipul de utilizator și setează starea de aprobat
            if user.user_type == 'Staff':
                user.is_approved = False
            else:
                user.is_approved = True

            user.save()

            expiration_time = user.token_created + TOKEN_LIFETIME
            expiration_time_local = timezone.localtime(expiration_time)
            # Trimiterea email-ului de activare pentru utilizator
            current_site = get_current_site(request)
            email_subject = 'Confirmare Email'
            email_body = (
                f'Verifică-ți email-ul folosind următorul link: http://{current_site.domain}:8000/users/activate/{user.verification_token}/\n'
                f'Tokenul de activare va expira pe {expiration_time_local.strftime("%Y-%m-%d %H:%M:%S")}.'

            )
            send_mail(email_subject, email_body, settings.EMAIL_HOST_USER, [user.email], fail_silently=False)

            return redirect('login')  # Redirect către pagina de login
    else:
        form = RegistrationForm()

    return render(request, 'register.html', {'form': form})

def approve_user(user):
    user.is_approved = True
    # Obține permisiunile pentru modelul Transport
    transport_content_type = ContentType.objects.get(app_label='transporturi', model='transport')
    permissions = Permission.objects.filter(content_type=transport_content_type)
    user.user_permissions.set(permissions)
    user.save()


# noinspection PyUnusedLocal
@user_passes_test(staff_required) # Asigură-te că doar utilizatorii staff pot accesa această pagină
def approve_user_view(request, user_id):
    user = get_object_or_404(CustomUser, id=user_id)
    user.is_approved = True

    if user.user_type == 'Staff':
        user.is_staff = True
    else:
        user.is_staff = False
    # Obține permisiunile pentru modelul Transport
    transport_content_type = ContentType.objects.get(app_label='transporturi', model='transport')
    permissions = Permission.objects.filter(content_type=transport_content_type)
    user.user_permissions.set(permissions)
    user.save()

    return redirect('user_list')

@user_passes_test(staff_required)
def user_list_view(request):
    users = CustomUser.objects.all()  # Obține toți utilizatorii
    return render(request, 'user_list.html', {'users': users})

@login_required
def profile(request):
    user = request.user
    if request.method == 'POST':
        form = RegistrationForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            return redirect('dashboard')
    else:
        # Dacă cererea este de tip GET, trebuie să inițializezi formularul
        form = RegistrationForm(instance=user)

    return render(request, 'profile.html', {'form': form})


def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect('dashboard')
        else:
            return render(request, 'login.html', {'error': 'Date de logare incorecte'})

    return render(request, 'login.html')


@login_required
def dashboard(request):
    return render(request, 'dashboard.html')

def welcome(request):
    return render(request, 'welcome.html')

