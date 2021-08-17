from base.services import IService
from django.contrib.auth.models import User
from rest_framework.exceptions import ValidationError
from django.db.utils import IntegrityError


class UserService(IService):
    model = User
    basequeryset = User.objects.all()

    def check_password(self, **data):
        if data.get('repeat_password') != data.get('password'):
            raise ValidationError('Passwords doesn\'t match')

    def create(self, **data):
        ''' Create new user '''
        self.check_password

        new_user = None
        
        try:
            try:
                new_user = self.model.objects.create_user(
                    username=data.get('username'),
                    password=data.get('password'),
                )
                new_user.save()
            except IntegrityError as e:
                raise ValidationError(f'User already registred!')

            return new_user
        except KeyError as e:
            raise ValidationError(str(e))

    def update(self, update_data, **filters):
        if 'repeat_password' in list(update_data.keys()):
            update_data.pop('repeat_password')

        return super().update(update_data, **filters)