import json, bcrypt, jwt, os

from django.http.response   import JsonResponse
from django.core.exceptions import ValidationError
from django.views           import View

from users.validation       import email_check, password_check
from .models                import User
from zara.settings          import SECRET_KEY

class SignUpView(View):
    def post(self, request):
        try:
            data          = json.loads(request.body)
            user_name     = data['name']
            user_email    = data['email']
            user_password = data['password']
            
            email_check(user_email)

            if User.objects.filter(email = user_email).exists():
                return JsonResponse({"ERROR" : "EMAIL_ALLEADY_EXIST"}, status=400)
        
            password_check(user_password)

            hashed_password = bcrypt.hashpw(user_password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
            User.objects.create(
                name     = user_name,
                email    = user_email,
                password = hashed_password
            )
            return JsonResponse({"RESULT" : "SUCCESS"}, status=200)

        except KeyError:
            return JsonResponse({"ERROR" : "KEY_ERROR"}, status = 400)

        except ValidationError as v:
            return JsonResponse({'ERROR' : v.message}, status=400)


class LoginView(View):
    def post(self, request):
        try:
            data          = json.loads(request.body)
            user_email    = data['email'] 
            user_password = data['password']
            user_db       = User.objects.get(email = user_email)  

            if bcrypt.checkpw(user_password.encode('utf-8'), user_db.password.encode('utf-8')):
                token = jwt.encode({'user_id': user_db.id}, SECRET_KEY, algorithm = os.evrion['ALGORITHM'])
                return JsonResponse({'MESSAGE' : 'SUCCESS', 'ACCESS_TOKEN' : token}, status=200)
            return JsonResponse({'ERROR' : 'PASSWORD_INVAILD_USER'}, status=401)
                                 
        except KeyError:
            return JsonResponse({'ERROR' : 'KEY_ERROR'}, status=400)

        except User.DoesNotExist:
            return JsonResponse({'message':'EMAIL_INVALD_USER'}, status=401)