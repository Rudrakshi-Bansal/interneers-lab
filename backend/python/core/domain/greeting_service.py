class GreetingService:
    """Domain service responsible for greeting logic."""

    @staticmethod
    def greet(name: str) -> str:
        if not name:
            return "Hello Stranger"
        return f"Hello {name}"
