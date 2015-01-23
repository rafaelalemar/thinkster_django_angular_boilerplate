from rest_framework import permissions, viewsets, status
from rest_framework.response import Response

from authentication.models import Account
from authentication.permissions import IsAccountOwner
from authentication.serializers import AccountSerializer


class AccountViewSet(viewsets.ModelViewSet):
    '''
    Django REST Framework offers a feature called viewsets. A viewset, as the name implies, is a set of views.
    Specifically, the ModelViewSet offers an interface for listing, creating, retrieving, updating and destroying
    objects of a given model.
    '''

    # Here we define the query set and the serialzier that the viewset will operate on. Django REST Framework uses the
    # specified queryset and serializer to perform the actions listed below. Also note that we specify the lookup_field
    # attribute. As mentioned earlier, we will use the username attribute of the Account model to look up accounts
    # instead of the id attribute. Overriding lookup_field handles this for us.
    lookup_field = 'username'
    queryset = Account.objects.all()
    serializer_class = AccountSerializer


    def get_permissions(self):
        '''
        The only user that should be able to call dangerous methods (such as update() and delete()) is the owner of the
        account. We first check if the user is authenticated and then call a custom permission that we will write in
        just a moment. This case does not hold when the HTTP method is POST. We want to allow any user to create an
        account.

        If the HTTP method of the request ('GET', 'POST', etc) is "safe", then anyone can use that endpoint.
        :return:
        '''
        if self.request.method in permissions.SAFE_METHODS:
            return (permissions.AllowAny(),)

        if self.request.method == 'POST':
            return (permissions.AllowAny(),)

        return (permissions.IsAuthenticated, IsAccountOwner(),)


    def create(self, request):
        '''
        When you create an object using the serializer's .save() method, the object's attributes are set literally.
        This means that a user registering with the password 'password' will have their password stored as 'password'.
        This is bad for a couple of reasons:
        1) Storing passwords in plain text is a massive security issue.
        2) Django hashes and salts passwords before comparing them, so the user wouldn't be able to log in using
           'password' as their password.

        We solve this problem by overriding the .create() method for this viewset and using
        Account.objects.create_user() to create the Account object.
        :param request:
        :return:
        '''
        serializer = self.serializer_class(data=request.data)

        if serializer.is_valid():
            account = Account.objects.create_user(**serializer.validated_data)

            account.set_password(request.data.get('password'))
            account.save()

            return Response(serializer.validated_data, status=status.HTTP_201_CREATED)

        return Response({
            'status': 'Bad request',
            'message': 'Account could not be created with received data.'
        }, status=status.HTTP_400_BAD_REQUEST)