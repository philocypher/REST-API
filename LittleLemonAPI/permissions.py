from rest_framework.permissions import BasePermission,IsAuthenticated

class IsManagerOrAdmin(BasePermission):
    def has_permission(self, request, view):
        # Allow GET request for managers and admins
        if request.method == 'GET':
            return request.user.is_authenticated
        
        # Allow POST request only for admins
        if request.method == 'POST':
            return request.user.is_superuser
class IsManager(BasePermission):
    def has_permission(self, request, *args, **kwargs):
        return request.user.groups.filter(name='managers').exists() | request.user.is_superuser
class IsDeliveryCrew(BasePermission):
    def has_permission(self, request, *args, **kwargs):
        return request.user.groups.filter(name='delivery_crew').exists()