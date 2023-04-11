import os
import boto3


class SesClient:
   def __init__(self) -> None:
       if os.environ.get("STAGE") == "TEST":
           self.sqs = None
           return

       self.sqs = boto3.client("ses")