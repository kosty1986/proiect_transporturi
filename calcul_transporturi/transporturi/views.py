import hashlib
from django.http import HttpResponseForbidden
from django.shortcuts import render, redirect, get_object_or_404
from .forms import VehicleTypeForm
from django.urls import reverse
from django.contrib.auth import get_user_model
from datetime import  timedelta,datetime,date
from django.utils import timezone
from django.conf import settings
from .models import Transport,TransportAction, TransportPrice, VehicleType,User
from django.contrib.sites.models import Site
from django.contrib import messages
from .forms import TransportFilterForm
from django.db.models import Q
from django.http import HttpResponse
import csv
from django.core.paginator import Paginator
from django.core.mail import send_mail
from django.contrib.auth.decorators import login_required
from .utils import adauga_zile_lucru
from django.core.files.storage import FileSystemStorage
from .models import TransportFile
from django.http import JsonResponse
from django.utils import timezone
from datetime import datetime
# noinspection PyRedeclaration
# noinspection PyUnresolvedReferences,PyUnusedLocal

User = get_user_model()



@login_required
def add_transport(request):

    if request.user.user_type != 'Client':
        return redirect('view_transports')

    transporters = User.objects.filter(user_type='transportator')
    vehicle_types = VehicleType.objects.all()

    if request.method == 'POST':
        destination = request.POST.get('destination')
        delivery_type = request.POST.get('delivery_type')
        pickup_time = None


        if delivery_type == 'normal':
            delivery_date = adauga_zile_lucru(timezone.now(), 2)
        else:
            delivery_date = timezone.make_aware(datetime.strptime(request.POST.get('delivery_date'), '%Y-%m-%dT%H:%M'))

        # Obține tipul de vehicul
        vehicle_type_id = request.POST.get('vehicle_type')
        vehicle_type = get_object_or_404(VehicleType, id=vehicle_type_id)

        # Verifică dacă vehiculul este complet
        full_vehicle = request.POST.get('full_vehicle') == 'true'
        number_of_pallets = None

        # Setează numărul de paleți
        if full_vehicle:
            number_of_pallets = vehicle_type.max_pallets  # Folosește max_pallets dacă vehiculul este complet
        else:
            number_of_pallets = request.POST.get('number_of_pallets')

        # Crează instanța de Transport
        transport = Transport(
            client=request.user,
            destination=destination,
            delivery_date=delivery_date,
            pickup_time=pickup_time,
            vehicle_type=vehicle_type,
            full_vehicle=full_vehicle,
            number_of_pallets=number_of_pallets,
        )
        transport.save()

        # Păstrează linia dorită pentru obținerea ID-urilor transportatorilor selectați
        selected_transporters = request.POST.getlist('transporters')


        # Asociază transportatorii selectați folosind ID-urile
        transport.transporters.set(User.objects.filter(id__in=selected_transporters))

        # Trimite email fiecărui transportator selectat
        for transporter_id in selected_transporters:
            transporter = get_object_or_404(User, id=transporter_id)
            send_mail(
                'Nou transport adăugat',
                f'S-a adăugat un nou transport cu destinația: {destination}.\nDetalii livrare: {delivery_date}.',
                settings.EMAIL_HOST_USER,
                [transporter.email],
                fail_silently=False,
            )

        # Crează un string cu numele utilizatorilor
        selected_usernames = ', '.join(transporter.username for transporter in User.objects.filter(id__in=selected_transporters))
        user_username = request.user.username

        # Înregistrează acțiunea de transport creat
        TransportAction.objects.create(
            transport=transport,
            action_type=f'Transportul a fost creat si trimis catre: {selected_usernames}. Modificarea a fost realizată de: {user_username}.',
            user=request.user  # Adăugat utilizatorul care a făcut modificarea
        )

        return redirect('view_transports')

    return render(request, 'add_transport.html', {'transporters': transporters, 'vehicle_types': vehicle_types})


# noinspection PyUnresolvedReferences,PyUnusedLocal
@login_required
def edit_transport(request, transport_id):
    transport = get_object_or_404(Transport, id=transport_id)
    vehicle_types = VehicleType.objects.all()

    if request.user == transport.client:
        if request.method == 'POST':
            # Obține și verifică datele din formular
            destination = request.POST.get('destination')
            delivery_date_str = request.POST.get('delivery_date')
            if delivery_date_str:  # Verificăm dacă valoarea este prezentă
                delivery_date = timezone.make_aware(datetime.strptime(delivery_date_str, '%Y-%m-%dT%H:%M'))
            else:
                delivery_date = None

            vehicle_type_id = request.POST.get('vehicle_type')
            full_vehicle = request.POST.get('full_vehicle') == 'true'

            # Obține tipul de vehicul și validează numărul de paleți
            vehicle_type = VehicleType.objects.get(id=vehicle_type_id)
            number_of_pallets = vehicle_type.max_pallets if full_vehicle else int(
                request.POST.get('number_of_pallets') or 0)

            # Actualizează informațiile transportului
            transport.destination = destination
            transport.delivery_date = delivery_date
            transport.vehicle_type = vehicle_type
            transport.full_vehicle = full_vehicle
            transport.number_of_pallets = number_of_pallets

            transport.save()



            # Trimite notificări transportatorilor
            for transporter in transport.transporters.all():
                send_mail(
                    'Transport Modificat',
                    f'Clientul {transport.client.username} a modificat transportul la destinația {transport.destination}.',
                    settings.EMAIL_HOST_USER,
                    [transporter.email],
                    fail_silently=False,
                )

            return redirect('view_transports')

    elif request.user in transport.transporters.all():
        if request.method == 'POST':
            # Preluăm și validăm datele din formular
            price_str = request.POST.get('price')
            price = float(price_str) if price_str else None

            pickup_time_str = request.POST.get('pickup_time')
            if pickup_time_str:  # Verificăm dacă valoarea este prezentă
                pickup_time = timezone.make_aware(datetime.strptime(pickup_time_str, '%Y-%m-%dT%H:%M'))
            else:
                pickup_time = None

            nr_masina = request.POST.get('nr_masina')
            user_username = request.user.username
            if transport.nr_masina != nr_masina:
                transport.nr_masina = nr_masina
                TransportAction.objects.create(transport=transport,
                                               action_type= f'Numărul mașinii modificat la:  {nr_masina} Modificarea a fost realizată de: {user_username}.',
                                               user=request.user )

            created = False
            # Verifică dacă prețul nu este None sau gol înainte de a salva
            if price is not None:
                transport_price, created = TransportPrice.objects.update_or_create(
                    transport=transport,
                    transporter=request.user,
                    defaults={'price': price}
                )
                if created:
                # Prețul a fost creat pentru prima dată
                    previous_price = None
                else:
                    previous_price = transport_price.price

            # Compară prețul anterior cu cel nou
                if previous_price != price:
                    TransportAction.objects.create(
                        transport=transport,
                        action_type=f'Oferta depusa: {price}. Modificarea a fost realizată de: {user_username}.',
                        user=request.user
                    )

            transport.nr_masina = nr_masina
            transport.pickup_time = pickup_time
            transport.save()

            return redirect('view_transports')

    return render(request, 'modify_transport.html', {
        'transport': transport,
        'vehicle_types': vehicle_types,
    })


# noinspection PyUnresolvedReferences
@login_required
def view_transports(request):
    form = TransportFilterForm(request.GET or None)

    # Filtrarea transporturilor în funcție de tipul utilizatorului
    if request.user.user_type == 'Client':
        transports = Transport.objects.filter(client=request.user).order_by('id')
    elif request.user.user_type == 'Transportator':
        transports = Transport.objects.filter(allocated_transporter=request.user) | Transport.objects.filter(is_allocated=False).order_by('id')
    else:
        transports = Transport.objects.none()

    # Procesarea formularului de filtrare
    if form.is_valid():
        destination = form.cleaned_data.get('destination', '')
        status = form.cleaned_data.get('status', '')
        delivery_date = form.cleaned_data.get('delivery_date', None)

        if destination:
            transports = transports.filter(destination__icontains=destination)

        if status:
            if request.user.user_type == 'Client':
                if status == 'allocated':
                    transports = transports.filter(is_allocated=True, is_completed=False,is_departed=False, client=request.user)
                elif status == 'departed':
                    transports = transports.filter(is_departed=True, is_completed=False,client=request.user)
                elif status == 'pending':
                    transports = transports.filter(is_allocated=False, is_departed=False,is_completed=False,
                                                   client=request.user)
                elif status == 'completed':
                    transports = transports.filter(is_completed=True, client=request.user)
            elif request.user.user_type == 'Transportator':
                if status == 'allocated':
                    transports = transports.filter(is_allocated=True, is_completed=False,is_departed=False,
                                                   allocated_transporter=request.user)
                elif status == 'departed':
                    transports = transports.filter(is_departed=True, is_completed=False,
                                                   allocated_transporter=request.user)
                elif status == 'pending':
                    transports = transports.filter(is_allocated=False,is_completed=False,
                                                   is_departed=False)
                elif status == 'completed':
                    transports = transports.filter(is_completed=True, allocated_transporter=request.user)

        if delivery_date:
            if isinstance(delivery_date, date):
                delivery_date = timezone.make_aware(datetime.combine(delivery_date, datetime.min.time()))

            if timezone.is_naive(delivery_date):
                delivery_date_aware = timezone.make_aware(delivery_date)
            else:
                delivery_date_aware = delivery_date
            transports = transports.filter(delivery_date__gte=delivery_date_aware,
                                           delivery_date__lt=delivery_date_aware + timedelta(days=1))



    paginator = Paginator(transports, 10)
    page_number = request.GET.get('page')
    transports_page = paginator.get_page(page_number)

    total_transports = transports.count()
    total_pages = paginator.num_pages
    current_page = transports_page.number

    transport_data = []
    for transport in transports_page:
        prices = TransportPrice.objects.filter(transport=transport)
        allocated_transporter = transport.allocated_transporter if transport.is_allocated else None

        # Filtrarea prețurilor pentru transportatori
        if request.user.user_type == 'Transportator':
            prices = prices.filter(transporter=request.user)

        transport_data.append({
            'transport': transport,
            'prices': prices,
            'allocated_transporter': allocated_transporter
        })

    # Gestionarea formularului de alocare transportator
    if request.method == 'POST' and request.user.user_type == 'Client':
        transport_id = request.POST.get('transport_id')
        selected_transporter_username = request.POST.get('selected_transporter')

        transport = get_object_or_404(Transport, id=transport_id)
        selected_transporter = get_object_or_404(User, username=selected_transporter_username)

        transport.is_allocated = True
        transport.allocated_transporter = selected_transporter
        transport.save()
        user_username = request.user.username
        TransportAction.objects.create(
            transport=transport,
            action_type=f'Transportul a fost alocat transportatorului {selected_transporter.username}.Modificarea a fost realizată de: {user_username}.',
            user=request.user
        )

        send_mail(
            'Transport alocat',
            f'Transportul cu ID {transport.id} a fost alocat transportatorului {selected_transporter.username}.\n'
            f'Destinația: {transport.destination}\n'
            f'Data livrarii: {transport.delivery_date}.',
            settings.EMAIL_HOST_USER,
            [selected_transporter.email],
            fail_silently=False,
        )

        other_transporters = TransportPrice.objects.filter(transport=transport).exclude(
            transporter=selected_transporter)
        for other in other_transporters:
            send_mail(
                'Transport alocat altui transportator',
                f'Un alt transportator a fost selectat pentru transportul cu ID {transport.id}.\n'
                f'Destinația: {transport.destination}\n'
                f'Data livrarii: {transport.delivery_date}.',
                settings.EMAIL_HOST_USER,
                [other.transporter.email],
                fail_silently=False,
            )
        return redirect('view_transports')
    return render(request, 'view_transports.html', {
        'transport_data': transport_data,
        'form': form,
        'transports': transports_page,
        'total_transports': total_transports,
        'total_pages': total_pages,
        'current_page': current_page,
    })



@login_required
def add_vehicle_type(request):
    if request.method == 'POST':
        form = VehicleTypeForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('view_vehicle_types')
    else:
        form = VehicleTypeForm()

    return render(request, 'add_vehicle_type.html', {'form': form})



@login_required
def view_vehicle_types(request):
    vehicle_types = VehicleType.objects.all()  # Obține toate tipurile de vehicule
    return render(request, 'view_vehicle_types.html', {'vehicle_types': vehicle_types})

@login_required
def mark_as_departed(request, transport_id):
    transport = get_object_or_404(Transport, id=transport_id)

    # Verifică dacă utilizatorul este clientul transportului
    if request.user == transport.client:
        # Marchează transportul ca plecat
        transport.is_departed = True
        transport.save()
    TransportAction.objects.create(
        transport=transport,
        action_type=f'Transportul a  plecat spre destinatie.',
        user=request.user
    )


    return redirect('view_transports')


@login_required
def mark_transport_as_completed(request, transport_id):
    transport = get_object_or_404(Transport, id=transport_id)

    # Verifică dacă utilizatorul este transportatorul alocat
    if request.user == transport.allocated_transporter:
        # Schimbă statusul transportului în "finalizat"
        transport.is_completed = True
        transport.save()

        # Trimite email clientului
        subject = f'Transport finalizat pentru Transport #{transport.id}'
        message = f'Salut {transport.client.username},\n\n' \
                  f'Transportul către {transport.destination} a fost finalizat.\n' \
                  f'ID Transport: {transport.id}'
        send_mail(subject, message, settings.EMAIL_HOST_USER, [transport.client.email])

        messages.success(request, 'Transportul a fost marcat ca finalizat.')

        # Creează un nou transport action
        TransportAction.objects.create(
            transport=transport,
            action_type='Transportul a fost finalizat.',
            user=request.user  # Adăugat utilizatorul care a făcut modificarea
        )

        # Redirecționează către pagina de transporturi
        return redirect('view_transports')
    else:
        messages.error(request, 'Nu ești autorizat să finalizezi acest transport.')
        return redirect('view_transports')




@login_required
def request_transport_status(request, transport_id):
    transport = get_object_or_404(Transport, id=transport_id)

    if transport.allocated_transporter:
        # Creează subiectul și corpul mesajului
        subject = f'Solicitare status transport pentru ID {transport.id}'

        # Obține adresa site-ului curent
        current_site = Site.objects.get_current()
        site_domain = current_site.domain

        message = (
            f'S-a solicitat actualizarea statusului pentru transportul cu ID {transport.id}.\n'
            f'Destinatie: {transport.destination}\n'
            f'Dată livrare: {transport.delivery_date}.\n'
            f'Te rugăm să actualizezi locația actuală a transportului accesând următorul link:\n'
            f'http://{site_domain}:8000{reverse("update_transport_status", args=[transport.id])}'
        )

        # Trimite e-mailul către transportatorul alocat
        send_mail(
            subject,
            message,
            settings.EMAIL_HOST_USER,
            [transport.allocated_transporter.email],
            fail_silently=False,
        )

        messages.success(request, 'Solicitarea a fost trimisă cu succes către transportator.')
    else:
        messages.error(request, 'Transportul nu are un transportator alocat.')

    # print(f"Emailul transportatorului este: {transport.allocated_transporter.email}")

    user_username = request.user.username
    TransportAction.objects.create(
        transport=transport,
        action_type=f'A fost cerut status locatie.Modificarea a fost realizată de: {user_username}.',
        user=request.user  # Adăugat utilizatorul care a făcut modificarea
    )
    return redirect('view_transports')


@login_required
def update_transport_status(request, transport_id):
    transport = get_object_or_404(Transport, id=transport_id)

    # Inițializarea current_location în afara blocului POST
    current_location = transport.current_location

    if request.method == 'POST':
        # Actualizează statusul transportului pe baza datelor din formular
        current_location = request.POST.get('current_location')
        transport.current_location = current_location

        # Salvează modificările în baza de date
        transport.save()

        user_username = request.user.username
        TransportAction.objects.create(
            transport=transport,
            action_type=f'locatie receptionata: {current_location}. Modificarea a fost realizată de: {user_username}.',
            user=request.user
        )

        messages.success(request, 'Statusul transportului a fost actualizat cu succes.')
        return redirect('view_transports')

    # Dacă metoda nu este POST, returnează un formular pentru actualizare
    return render(request, 'update_transport_status.html',
                  {'transport': transport, 'current_location': current_location})

@login_required
def transport_detail(request, transport_id):
    transport = get_object_or_404(Transport, id=transport_id)

    # Dacă utilizatorul este Transportator, redirecționează către lista de transporturi
    if request.user.user_type == 'Transportator':
        return redirect('view_transports')

    # Verifică dacă utilizatorul este clientul asociat transportului
    if request.user.user_type == 'Client' and transport.client != request.user:
        return HttpResponseForbidden()

    return render(request, 'transport_detail.html', {
        'transport': transport,
    })


@login_required
def transport_history(request, transport_id):
    transport = get_object_or_404(Transport, id=transport_id)
    actions = TransportAction.objects.filter(transport=transport).order_by('-timestamp')

    return render(request, 'transport_history.html', {
        'transport': transport,
        'actions': actions,
    })


# noinspection PyUnresolvedReferences

from django.utils import timezone

@login_required
def export_data(request):
    # Preluăm parametrii de filtrare din request
    destination = request.GET.get('destination')
    status = request.GET.get('status')
    delivery_date = request.GET.get('delivery_date')

    # Debugging: Verificăm parametrii primiți
    print("Filters received: Destination -", destination, ", Status -", status, ", Delivery Date -", delivery_date)

    # Aplicăm filtrele doar dacă parametrii nu sunt goi
    filters = Q()

    if destination:
        filters &= Q(destination__icontains=destination)

    if status:
        if status == 'completed':
            filters &= Q(is_completed=True)
        elif status == 'allocated':
            filters &= Q(is_allocated=True)
        elif status == 'departed':
            filters &= Q(is_departed=True)

    # Filtrăm după delivery_date, inclusiv întreaga zi
    if delivery_date:
        try:
            # Convertim delivery_date într-un obiect datetime
            delivery_date_obj = timezone.datetime.strptime(delivery_date, '%Y-%m-%d')
            # Calculăm intervalul de timp pentru toată ziua
            start_of_day = delivery_date_obj.replace(hour=0, minute=0, second=0, microsecond=0)
            end_of_day = delivery_date_obj.replace(hour=23, minute=59, second=59, microsecond=999999)
            # Aplicăm filtrul pentru intervalul de timp
            filters &= Q(delivery_date__range=(start_of_day, end_of_day))
        except ValueError:
            print("Date format error: ", delivery_date)

    # Debugging
    print("Applying filters:", filters)

    # Filtrăm transporturile în funcție de parametrii din request
    transports = Transport.objects.filter(filters)

    # Debugging
    print("Number of transports after filtering:", transports.count())

    # Creează un răspuns HTTP cu tipul de conținut CSV
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="transports.csv"'

    writer = csv.writer(response)
    writer.writerow(['ID', 'Destinatie', 'Data livrarii', 'Status', 'Preturi'])

    for transport in transports:
        prices = transport.prices.all()
        if prices.exists():
            price_list = ', '.join([f'{price.transporter.username}: {price.price}' for price in prices])
        else:
            price_list = 'Fara oferta'

        writer.writerow([
            transport.id,
            transport.destination,
            transport.delivery_date,
            transport.current_location,
            price_list
        ])

    return response

@login_required
def upload_transport_file(request, transport_id):
    transport = get_object_or_404(Transport, id=transport_id)

    # Verifică dacă utilizatorul este transportator
    if request.user.user_type != 'Transportator':
        return HttpResponseForbidden()

    if request.method == 'POST' and request.FILES.get('file_upload'):
        uploaded_file = request.FILES['file_upload']

        # Calculează hash-ul fișierului
        file_hash = get_file_hash(uploaded_file)

        # Verifică dacă fișierul cu acest hash există deja pentru acest transport
        if TransportFile.objects.filter(transport=transport, file_hash=file_hash).exists():
            messages.error(request, "Acest fișier a fost deja încărcat pentru acest transport.")
            return redirect('upload_transport_file', transport_id=transport_id)

        # Verifică dacă fișierul cu acest hash există deja pentru alt transport
        if TransportFile.objects.filter(file_hash=file_hash).exists():
            messages.error(request, "Acest fișier a fost deja încărcat pentru un alt transport.")
            return redirect('upload_transport_file', transport_id=transport_id)

        # Salvează fișierul în sistemul de fișiere
        fs = FileSystemStorage()
        filename = fs.save(uploaded_file.name, uploaded_file)

        # Salvează fișierul în baza de date
        transport_file = TransportFile(file=filename, transport=transport, file_hash=file_hash)
        transport_file.save()

        messages.success(request, "Fișierul a fost încărcat cu succes.")
        return redirect('view_transports')

    return render(request, 'upload_transport_file.html', {
        'transport': transport,
    })

def get_file_hash(file):
    """Calculează hash-ul SHA256 pentru un fișier."""
    hasher = hashlib.sha256()
    for chunk in file.chunks():
        hasher.update(chunk)
    return hasher.hexdigest()