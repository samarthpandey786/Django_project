from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model




class EmailBackend(ModelBackend):
    def authenticate(self, request=None, username=None, password=None, **kwargs):  # Added `request=None`
        UserModel = get_user_model()
        try:
            user = UserModel.objects.get(email=username)
        except UserModel.DoesNotExist:
            return None
        else:
            if user.check_password(password):
                return user
        return None

