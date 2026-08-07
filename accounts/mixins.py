from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.shortcuts import render


class BasePermissionRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    permission_denied_template_name = "accounts/permission_denied.html"

    def handle_no_permission(self):
        if not self.request.user.is_authenticated:
            return super().handle_no_permission()
        return render(
            self.request,
            self.permission_denied_template_name,
            status=403,
        )


class ModeratorOrAdminRequiredMixin(BasePermissionRequiredMixin):
    def test_func(self):
        return self.request.user.can_moderate()


class AdminRequiredMixin(BasePermissionRequiredMixin):
    def test_func(self):
        return self.request.user.is_admin_role()