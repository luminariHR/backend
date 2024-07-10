from django.core.management import BaseCommand
from django.contrib.auth.models import Group, Permission
from departments.models import Department


GROUPS_PERMISSIONS = {
    "HR 관리자": {
        Department: ["add", "change", "delete", "view"],
    },
}


class Command(BaseCommand):
    def __init__(self, *args, **kwargs):
        super(Command, self).__init__(*args, **kwargs)

    help = "추가 그룹 생성"

    def handle(self, *args, **options):
        # Loop groups
        for group_name in GROUPS_PERMISSIONS:

            # Get or create group
            group, created = Group.objects.get_or_create(name=group_name)

            # Loop models in group
            for model_cls in GROUPS_PERMISSIONS[group_name]:

                # Loop permissions in group/model
                for perm_index, perm_name in enumerate(
                    GROUPS_PERMISSIONS[group_name][model_cls]
                ):

                    # Generate permission name as Django would generate it
                    codename = perm_name + "_" + model_cls._meta.model_name
                    try:
                        # Find permission object and add to group
                        perm = Permission.objects.get(codename=codename)
                        group.permissions.add(perm)
                        self.stdout.write(
                            f"{codename}을 {group.__str__()}에 추가했습니다."
                        )
                    except Permission.DoesNotExist:
                        self.stdout.write(codename + "를 찾을 수 없습니다.")
