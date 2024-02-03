import os
import boto3  # type: ignore
import typing


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
            aws_access_key_id=os.environ["AWS_ACCESS_KEY_ID"],
            aws_secret_access_key=os.environ["AWS_SECRET_ACCESS_KEY"],
        )

    def send_email(
        self,
        to_address: str,
        from_address,
        subject: str,
        body: str,
        attachment: Attachment,
    ) -> None:
        if self.ses is None:
            return

        raw_message = """From: {from_address}
            To: {to_address}
            Subject: {subject}
            MIME-Version: 1.0
            Content-type: Multipart/Mixed; boundary="NextPart"

            --NextPart
            Content-Type: text/plain

            {body}

            --NextPart
            Content-Type: text/plain;
            Content-Disposition: attachment; filename="{filename}"

            {content}

            --NextPart--""".format(
            from_address=from_address,
            to_address=to_address,
            subject=subject,
            body=body,
            filename=attachment.filename,
            content=attachment.content,
        )

        return self.ses.send_raw_email(
            Destinations=[],
            RawMessage={"Data": raw_message.encode()},
        )
