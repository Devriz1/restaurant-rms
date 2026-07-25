from django.contrib import messages
from django.contrib.auth import get_user_model, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView
from django.shortcuts import (
    get_object_or_404,
    redirect,
    render,
)
from django.views.decorators.cache import never_cache
from apps.accounts.decorators import permission_required
from .forms import (
    LoginForm,
    UserCreateForm,
    UserEditForm,
)
from .models import Permission, UserPermission


User = get_user_model()


# ==========================================================
# USER LIST
# ==========================================================
@never_cache
@login_required
def user_list(request):

    users = User.objects.order_by("username")

    return render(
        request,
        "accounts/user_list.html",
        {
            "users": users,
        },
    )


# ==========================================================
# ADD USER
# ==========================================================

@login_required
def user_add(request):

    permissions = Permission.objects.order_by(
        "category",
        "name",
    )

    if request.method == "POST":

        form = UserCreateForm(request.POST)

        if form.is_valid():

            user = form.save()

            UserPermission.objects.filter(
                user=user
            ).delete()

            selected_permissions = request.POST.getlist(
                "permissions"
            )

            for permission_id in selected_permissions:

                UserPermission.objects.create(
                    user=user,
                    permission_id=permission_id,
                )

            messages.success(
                request,
                "User created successfully.",
            )

            return redirect(
                "accounts:user-list",
            )

    else:

        form = UserCreateForm()

    return render(
        request,
        "accounts/user_form.html",
        {
            "form": form,
            "title": "Add User",
            "permissions": permissions,
            "user_permissions": [],
        },
    )


# ==========================================================
# EDIT USER
# ==========================================================

@login_required
def user_edit(request, pk):

    user = get_object_or_404(
        User,
        pk=pk,
    )

    permissions = Permission.objects.order_by(
        "category",
        "name",
    )

    user_permissions = list(
        UserPermission.objects.filter(
            user=user,
        ).values_list(
            "permission_id",
            flat=True,
        )
    )

    if request.method == "POST":

        form = UserEditForm(
            request.POST,
            instance=user,
        )

        if form.is_valid():

            user = form.save()

            UserPermission.objects.filter(
                user=user,
            ).delete()

            selected_permissions = request.POST.getlist(
                "permissions"
            )

            for permission_id in selected_permissions:

                UserPermission.objects.create(
                    user=user,
                    permission_id=permission_id,
                )

            messages.success(
                request,
                "User updated successfully.",
            )

            return redirect(
                "accounts:user-list",
            )

    else:

        form = UserEditForm(
            instance=user,
        )

    return render(
        request,
        "accounts/user_form.html",
        {
            "form": form,
            "title": "Edit User",
            "permissions": permissions,
            "user_permissions": user_permissions,
        },
    )


# ==========================================================
# DELETE USER
# ==========================================================

@login_required
def user_delete(request, pk):

    user = get_object_or_404(
        User,
        pk=pk,
    )

    if user == request.user:

        messages.error(
            request,
            "You cannot delete your own account.",
        )

        return redirect(
            "accounts:user-list",
        )

    if request.method == "POST":

        UserPermission.objects.filter(
            user=user,
        ).delete()

        user.delete()

        messages.success(
            request,
            "User deleted successfully.",
        )

        return redirect(
            "accounts:user-list",
        )

    return render(
        request,
        "accounts/user_delete.html",
        {
            "user": user,
        },
    )

# ==========================================================
# CHANGE USER PASSWORD
# ==========================================================

@login_required
def change_user_password(request, pk):

    user = get_object_or_404(
        User,
        pk=pk,
    )

    if request.method != "POST":

        return redirect(
            "accounts:user-list",
        )

    new_password = request.POST.get(
        "new_password",
        "",
    )

    confirm_password = request.POST.get(
        "confirm_password",
        "",
    )

    if not new_password:

        messages.error(
            request,
            "Password cannot be empty.",
        )

        return redirect(
            "accounts:user-edit",
            pk=user.pk,
        )

    if new_password != confirm_password:

        messages.error(
            request,
            "Passwords do not match.",
        )

        return redirect(
            "accounts:user-edit",
            pk=user.pk,
        )

    user.set_password(new_password)

    user.save()

    messages.success(
        request,
        f"Password for '{user.username}' changed successfully.",
    )

    return redirect(
        "accounts:user-list",
    )


# ==========================================================
# LOGIN
# ==========================================================

class UserLoginView(LoginView):

    template_name = "registration/login.html"

    authentication_form = LoginForm

    redirect_authenticated_user = True


# ==========================================================
# LOGOUT
# ==========================================================

@login_required
def user_logout(request):

    logout(request)

    return redirect(
        "accounts:login",
    )