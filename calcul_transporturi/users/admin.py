from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser
from django.contrib.auth.models import Group

admin.site.unregister(Group)
class CustomUserAdmin(UserAdmin):  # Extinde UserAdmin pentru gestionarea utilizatorilor
    list_display = ('username', 'email', 'user_type', 'email_verified', 'is_staff')
    search_fields = ('username', 'email')

    # Extindem fieldsets pentru a adăuga câmpurile personalizate din modelul CustomUser
    fieldsets = UserAdmin.fieldsets + (
        (None, {'fields': ('user_type', 'email_verified', 'verification_token', 'token_used', 'token_created', 'is_approved')}),

    )
    def save_model(self, request, obj, form, change):
        if form.cleaned_data['is_approved'] and not obj.is_approved:  # Dacă a fost aprobat și nu era aprobat
            obj.approved_by = request.user  # Setează utilizatorul care a aprobat
        obj.save()
    # Definim ce câmpuri pot fi editate direct în interfața de administrare
    readonly_fields = ('verification_token', 'token_created', 'token_used')



# Înregistrăm modelul CustomUser împreună cu admin-ul personalizat CustomUserAdmin
admin.site.register(CustomUser, CustomUserAdmin)
