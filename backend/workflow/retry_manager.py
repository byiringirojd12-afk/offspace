class RetryManager:
    """Handles workflow retries after failed steps."""

    def __init__(self, max_retries=3):
        self.max_retries = max_retries

    def should_retry(self, attempt):
        return attempt < self.max_retries

    def execute_with_retry(self, action):
        attempt = 0
        while self.should_retry(attempt):
            try:
                return action()
            except Exception:
                attempt += 1
        raise RuntimeError("Workflow failed after retry limit")
