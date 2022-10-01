import csv
import pandas as pd
from django.core.management import BaseCommand, CommandError
# from emuegg.base.models import User
from ...models import User

class Command(BaseCommand):
    help = 'Load the sample user csv file into the database'

    def add_arguments(self, parser):
        parser.add_argument('--path', type=str)

    def handle(self, *args, **kwargs):
        # remove the existing user data?
        User.objects.all().delete()
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

