import smtplib, ssl

# import os


class Email:
    def __init__(self,) -> None:
        self.smtp_server = "smtp.gmail.com"
        self.ssl_port=465
        self.context = ssl.create_default_context()
    
    def send(self, sender_email, sender_password, receiver_email, message):
        with smtplib.SMTP_SSL(self.smtp_server, self.ssl_port, context=self.context) as server:
            server.login(sender_email, sender_password)
            server.sendmail(sender_email, receiver_email, message)
        return



e = Email()

# e.send(os.getenv('APP_MAIL'),os.getenv('APP_PASSWORD'), 'pfanosigama8@gmail.com','hello there')






