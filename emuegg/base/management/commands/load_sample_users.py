import csv
import pandas as pd
from django.core.management import BaseCommand, CommandError
# from emuegg.base.models import User
from ...models import User
from ...models import Channel

class Command(BaseCommand):
    help = 'Load the sample user csv file into the database'

    def add_arguments(self, parser):
        parser.add_argument('--path', type=str)

    def handle(self, *args, **kwargs):

        # 清除所有的 user和channel 已有数据，如果当前开发依赖这些已有数据，不要run这两行！
        User.objects.all().delete()
        Channel.objects.all().delete()
        path = kwargs['path']
        user_df = pd.read_csv(path)
        print(user_df)

        for index, row in user_df.iterrows():
            print(str(index) + "with row number " + str(row))
            email = row["email"]
            # username = row["username"]   # this attribute not working
            major = row["major"]
            country = row["country"]
            course = row["course"]

            # populate User object for each row
            user = User(email=email,
                        Country=country,
                        Major=major,
                        Courses=course
                        )
            # save user object
            user.save()
        # print(f"User: {email}, {username} saved...")


# Use following command to load sample user to database
# python manage.py load_sample_users --path sample_user.csv
# 因导入sample users会删除本地数据库中已有的数据，如果本地有基于当前user创建过channel，user清空后会出现报错

