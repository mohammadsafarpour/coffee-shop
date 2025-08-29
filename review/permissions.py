from rest_framework import permissions

class IsReviewOwnerOrAdminOrReadOnly(permissions.BasePermission):

    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True

        return request.user and request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            if request.user.is_staff:
                return True
            return obj.is_approved or (
                request.user.is_authenticated and obj.user == request.user
            )

        if request.user.is_staff:
            return True
        
        return obj.user == request.user


class CanReviewProduct(permissions.BasePermission):

    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated


class IsAdminOrReadOnly(permissions.BasePermission):

    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        
        return request.user and request.user.is_staff