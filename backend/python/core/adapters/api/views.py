from django.http import JsonResponse
from core.application.greet_user_use_case import GreetUserUseCase


def greet_user_view(request):
    name = request.GET.get("name", "")
    use_case = GreetUserUseCase()
    message = use_case.execute(name)

    return JsonResponse({"message": message})
