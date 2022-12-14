import csv
import pandas as pd
from django.core.management import BaseCommand, CommandError
# from emuegg.base.models import User
from ...models import User
from ...models import Channel

# test
from django.core import files
from django.core.files.base import ContentFile
import tempfile
import requests
import os


class Command(BaseCommand):
    help = 'Load the sample user csv file into the database'

    def add_arguments(self, parser):
        parser.add_argument('--path', type=str)

    def handle(self, *args, **kwargs):

        # 清除 除super user外剩余的所有user！
        User.objects.exclude(is_staff=1).delete()
        Channel.objects.all().delete()

        # clear all images in avatar directory, ensure the file name we intended to save remain the same
        # 因为要将load_image 文件夹里的图片存进avatar里，如果avatar中有同名文件，
        # 则即将被存储的同名文件会被变更名称，因此需要先清空avatar文件夹
        dir = 'static/images/avatar/'
        for f in os.listdir(dir):
            os.remove(os.path.join(dir, f))

        path = kwargs['path']
        user_df = pd.read_csv(path)
        print(user_df)
        counter = 1
        for index, row in user_df.iterrows():
            print(str(index) + "with row number " + str(row))
            email = row["email"]
            username = row["username"]
            major = row["major"]
            country = row["country"]
            course = row["course"]
            topic = row["topic"]

            # get the url
            # url = 'https://xsgames.co/randomusers/assets/avatars/pixel/' + str(counter) + '.jpg'

            # url = 'static/images/avatar/' + str(counter) + '.png'

            image_name = str(counter) + '.png'
            # retrieve the image
            file_name, picture = retrieve_image(image_name)

            # populate User object for each row
            user = User(email=email,
                        username=username,
                        Major=major,
                        Country=country,
                        Courses=course,
                        Topics=topic
                        )
            # save user object
            user.save()
            print(file_name, "is the file name")
            user.Picture.save(image_name, ContentFile(picture))
            counter += 1


"""
Specific function used to retrieve image from a given url
"""
def retrieve_image(file_name):
    # # Avatar API to retrieve different avatar image when access each time
    # image_url = url
    # # Stream the image from the url
    # response = requests.get(image_url, allow_redirects=True, stream=True)
    #
    #
    # # error handling to check whether request works fine
    # if response.status_code != requests.codes.ok:
    #     print("Something wrong with the request")
    #     pass
    #
    # file_name = image_url.split('/')[-1]
    # lf = tempfile.NamedTemporaryFile()
    #
    # for block in response.iter_content(1024 * 8):
    #     # If no more file then stop
    #     if not block:
    #         break
    #
    #     # Write image block to temporary file
    #     lf.write(block)
    #
    # return file_name, lf

    path = 'static/images/load_Image/' + file_name
    # with open(path, 'rb') as f:
    #     data = f.read()

    with open(path, "rb") as image:
        f = image.read()
        b = bytearray(f)

    # data = Image.open(path)

    # buf = io.BytesIO()
    # data.save(buf, format='PNG')
    # data = buf.getvalue()
    print(file_name)
    return file_name, b


# Use following command to load sample user to database
# python3 manage.py load_sample_users --path sample_user.csv
# 因导入sample users会删除本地数据库中已有的数据，如果本地有基于当前user创建过channel，user清空后会出现报错

