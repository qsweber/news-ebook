import os
import boto3  # type: ignore
import typing
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication


class Attachment(typing.NamedTuple):
    filename: str
    content: str


class SesClient:
    def __init__(self) -> None:
        if os.environ.get("STAGE") == "TEST":
            self.ses = None
            return

        self.ses = boto3.client(
            "ses",
            region_name="us-west-2",
        )

    def send_email(
        self,
        to_address: str,
        from_address,
        subject: str,
        body: str,
        attachment_path: str,
    ) -> None:
        if self.ses is None:
            return

        msg = MIMEMultipart("mixed")
        # Add subject, from and to lines.
        msg["Subject"] = subject
        msg["From"] = from_address
        msg["To"] = to_address

        msg_body = MIMEMultipart("alternative")
        msg_body.attach(MIMEText(body, "plain", "utf-8"))

        att = MIMEApplication(open(attachment_path, "rb").read())
        att.add_header(
            "Content-Disposition",
            "attachment",
            filename=os.path.basename(attachment_path),
        )

        msg.attach(msg_body)
        msg.attach(att)

        return self.ses.send_raw_email(
            Source=from_address,
            Destinations=[to_address],
            RawMessage={
                "Data": msg.as_string(),
            },
        )
