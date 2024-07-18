from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.conf import settings
from django.db.models.signals import pre_save
from django.dispatch import receiver
from django.utils.crypto import get_random_string
from .models import Employee


@receiver(pre_save, sender=Employee)
def set_random_password(sender, instance, **kwargs):
    if not instance.pk:
        password = get_random_string(12)
        instance.set_password(password)

        login_url = settings.LOGIN_URL
        html_content = render_to_string(
            "invite-email.html",
            {"login_url": login_url, "email": instance.email, "password": password},
        )

        # Create the email
        subject = "루미나리 팀의 가족이 되신 것을 축하드립니다!"
        from_email = settings.DEFAULT_FROM_EMAIL
        to_email = instance.email
        text_content = f"""
        루미나리 팀의 가족이 되신 것을 진심으로 축하드립니다.
        아래의 이메일 / 비밀번호를 이용해서 {login_url}에 로그인해주세요.
        이메일 주소: { instance.email }
        비밀번호: { password }
        """

        email = EmailMultiAlternatives(subject, text_content, from_email, [to_email])
        email.attach_alternative(html_content, "text/html")
        email.send(fail_silently=False)
