from django.db import models
from django.contrib.auth import get_user_model


User = get_user_model()

class VehicleType(models.Model):
    name = models.CharField(max_length=50)
    max_pallets = models.PositiveIntegerField()

    def __str__(self):
        return self.name

class Transport(models.Model):
    client = models.ForeignKey(User, on_delete=models.CASCADE, related_name='transports')
    nr_masina = models.CharField(max_length=50, null=True, blank=True)
    destination = models.CharField(max_length=255,verbose_name='Destinatie')
    delivery_date = models.DateTimeField(verbose_name='Data de livrare')
    pickup_time = models.DateTimeField(null=True, blank=True)
    transporters = models.ManyToManyField(User, related_name='transport_requests',
                                          limit_choices_to={'user_type': 'Transportator'})
    allocated_transporter = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL,
                                              related_name='allocated_transports')
    vehicle_type = models.ForeignKey(VehicleType, on_delete=models.SET_NULL, null=True)
    full_vehicle = models.BooleanField(default=True)
    number_of_pallets = models.PositiveIntegerField(null=True, blank=True)
    is_allocated = models.BooleanField(default=False,verbose_name='Alocat')
    is_departed = models.BooleanField(default=False,verbose_name='Plecat')
    is_completed = models.BooleanField(default=False,verbose_name='Finalizat')
    current_location = models.CharField(max_length=255, blank=True, null=True)

    # noinspection PyUnresolvedReferences
    def __str__(self):
        return f'Transport {self.id} - {self.client.username}'



class TransportPrice(models.Model):
    transport = models.ForeignKey(Transport, on_delete=models.CASCADE, related_name='prices')
    transporter = models.ForeignKey(User, on_delete=models.CASCADE, limit_choices_to={'user_type': 'Transportator'})
    price = models.DecimalField(max_digits=10, decimal_places=2)

    # noinspection PyUnresolvedReferences
    def __str__(self):
        return f'Price for Transport {self.transport.id} by {self.transporter.username}: {self.price}'

class TransportAction(models.Model):
    objects = None
    transport = models.ForeignKey('Transport', on_delete=models.CASCADE)
    action_type = models.CharField(max_length=100)
    timestamp = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.action_type} at {self.timestamp} by {self.user.username} for {self.transport}"

class TransportFile(models.Model):
    transport = models.ForeignKey(Transport, related_name='uploaded_files', on_delete=models.CASCADE)
    file = models.FileField(upload_to='calcul_transporturi/transport_files/')
    file_hash = models.CharField(max_length=64, unique=True)  # Adaugă acest câmp
    uploaded_at = models.DateTimeField(auto_now_add=True)

