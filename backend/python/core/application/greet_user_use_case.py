from core.domain.greeting_service import GreetingService


class GreetUserUseCase:
    def execute(self, name: str) -> str:
        return GreetingService.greet(name)
