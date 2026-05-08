from llms.deepseek import DeepSeekLLM


class Router:

    def __init__(self):

        self.providers = {
            "deepseek": DeepSeekLLM(),
        }

    def route(self, request: dict) -> str:
        """
        Placeholder routing logic.
        """

        return "deepseek"

    def get_provider(self, name: str):

        return self.providers[name]