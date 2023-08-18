import os
import boto3  # type: ignore


class SesClient:
    def __init__(self) -> None:
        if os.environ.get("STAGE") == "TEST":
            self.ses = None
            return

        self.ses = boto3.client("ses")

    def send_email(self, to: str, subject: str, body: str) -> None:
        if self.ses is None:
            return

        self.ses.