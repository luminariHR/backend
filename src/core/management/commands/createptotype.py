from django.core.management import BaseCommand
from ptos.models import PTOType


class Command(BaseCommand):
    def __init__(self, *args, **kwargs):
        super(Command, self).__init__(*args, **kwargs)

    help = "휴가 카테고리 생성"

    def handle(self, *args, **options):

        pto_type_names = list(PTOType.PTO_STRATEGY_MAPPING.keys()) + ["others"]
        for pto_type_name in pto_type_names:
            pto_type, created = PTOType.objects.get_or_create(
                name=pto_type_name, pto_type=pto_type_name
            )
            if created:
                self.stdout.write(f"'{pto_type}' 휴가 카테고리를 생성했습니다.")
