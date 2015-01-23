'''
Serializers

Serializers allow complex data such as querysets and model instances to be converted to native Python datatypes that
can then be easily rendered into JSON, XML or other content types. Serializers also provide deserialization, allowing
parsed data to be converted back into complex types, after first validating the incoming data.

The serializers in REST framework work very similarly to Django's Form and ModelForm classes. We provide a Serializer
class which gives you a powerful, generic way to control the output of your responses, as well as a ModelSerializer
class which provides a useful shortcut for creating serializers that deal with model instances and querysets.
'''

from django.contrib.auth import update_session_auth_hash
from rest_framework import serializers
from authentication.models import Account



class AccountSerializer(serializers.ModelSerializer):
    '''
    Instead of including password in the fields tuple, we explicitly define the field at the top of this class. The
    reason we do this is so we can pass the required=False argument. Each field in fields is required, but we don't
    want to update the user's password unless they provide a new one.

    confirm_pssword is similar to password and is used only to make sure the user didn't make a typo on accident.

    Also note the use of the write_only=True argument. The user's password, even in it's hashed and salted form,
    should not be visible to the client in the AJAX response.
    '''
    password = serializers.CharField(write_only=True, required=False)
    confirm_password = serializers.CharField(write_only=True, required=False)

    class Meta:
        '''
        The Meta sub-class defines metadata the serializer requires to operate. We have defined a few common attributes
        of the Meta class here.
        '''

        #  Because this serializers inherits from serializers.ModelSerializer, it should make sense that we must tell
        # it which model to serialize. Specifying the model creates a guarantee that only attributes of that model or
        # explicitly created fields can be serialized.
        model = Account

        # The fields attribute is where we specify which attributes of the Account model should be serialized.
        fields = (
            'id', 'email', 'user_name', 'created_at', 'updated_at', 'first_name',
            'last_name', 'tagline', 'password', 'confirm_password'
        )

        # On the Account model, we made the created_at and updated_at fields self-updating. Because of this feature,
        # we add them to a list of fields that should be read-only.
        read_only_fields = ('created_at', 'updated_at')


    def create(self, validated_data):
        '''
        Deserialization (turn JSON into a Python object)
        :param validated_data:
        :return:
        '''
        return Account.objects.create(**validated_data)


    def update(self, instance, validated_data):
        '''
        Deserialization (turn JSON into a Python object)
        :param validated_data:
        :return:
        '''

        # We will let the user update their username and tagline attributes for now. If these keys are present in the
        # arrays dictionary, we will use the new value. Otherwise, the current value of the instance object is used.
        # Here, instance is of type Account.
        instance.username = validated_data.get('username', instance.username)
        instance.tagline = validated_data.get('tagline', instance.tagline)

        instance.save()

        password = validated_data.get('password', None)
        confirm_password = validated_data.get('confirm_password', None)

        # Before updating the user's password, we need to confirm they have provided values for both the password and
        # password_confirmation field. We then check to make sure these two fields have equivelant values.
        #
        # After we verify that the password should be updated, we much use Account.set_password() to perform the
        # update. Account.set_password() takes care of storing passwords in a secure way. It is important to note that
        # we must explicitly save the model after updating the password.
        #
        # NOTE: This is a naive implementation of how to validate a password. I would not recommend using this in a
        # real-world system, but for our purposes this does nicely.
        if password and confirm_password and password == confirm_password:
            instance.set_password(password)
            instance.save()

        # When a user's password is updated, their session authentication hash must be explicitly updated. If we don't
        # do this here, the user will not be authenticated on their next request and will have to log in again.
        update_session_auth_hash(self.context.get('request'), instance)

        return instance