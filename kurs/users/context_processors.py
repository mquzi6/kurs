def user_role(request):
    """Добавляет информацию о роли пользователя в контекст"""
    return {
        'is_admin': request.user.is_authenticated and request.user.is_staff,
        'is_superuser': request.user.is_authenticated and request.user.is_superuser,
    }