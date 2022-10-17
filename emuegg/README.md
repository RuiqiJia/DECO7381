# Getting Started
This document is a guide for setting up a development environment for Cultural Bridge that uses:
1. windows
1. python 3.10.8
1. django 4.1.2
1. pip
1. mysql
## Install Python
https://www.python.org/ftp/python/3.10.8/python-3.10.8-amd64.exe

## Install pip
1. By defalut when installing python, pip will be installed, if not, navigate to cmd and type:
1. `pip install pip`

## Install mysql
1. https://dev.mysql.com/downloads/mysql/
1. https://dev.mysql.com/downloads/installer/
1. run the installer and set password to `root`
1. once installed, connected to database using password `root`, add new schema callled `emuegg`
1. in settings.py, change the database settings to:
```
 DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.mysql',
            'NAME': 'emuegg',
            'USER': 'root',
            'PASSWORD': 'root',
            'HOST': 'localhost',
            'PORT': 3306,
        }
    }
```

## Install Django and run django server
1. navigate to the project folder and run the following commands:
- `pip install django`
- `pip install channels`
- `pip install mysqlclient`
- `pip install branca`
- `pip install folium`
- `pip install geocoder`
- `pip install geopy`
- `pip install Pillow`
1. After installing all the dependencies, run the following commands to start the server:
- `python manage.py migrate`
- `python manage.py runserver`
1. visit http://127.0.0.1:8000/ to view the website

## Access database and create superuser
1. navigate to the project folder and run the following command:
- `python manage.py createsuperuser`
1. follow the instruction to create a superuser
1. visit http://127.0.0.1:8000/admin/ and login with the newly created superuser credentials
1. Alternatively, the project is upon UQ CLOUD ZONE, visit https://deco3801-emuegg.uqcloud.net/
- logging in with the UQ SSO is required

## load sample user
1. Use the following command to load sample users to the database
- `python3 manage.py load_sample_users --path sample_user.csv`

## Other instructions
1. The application is using mobile first design approach, for better viewing experience, navigate to inspect [F12] on your browser and choose iPhone XR with 100% zoom.
1. Information Entries Format(Please follow the instruction to enter the information if needed)：
- For single field, if multiple topics/courses requires, seperate them with comma without space (e.g. A,B)
- Potential Courses to select: COMP3702,CSSE1001,CSSE3003,DECO2500,INFS2200,INFS1200,COMP3506,INFS3200,DECO1800,COMS3200,DECO1400
- Potential Major to select: IT, ID, CS, BISM
- Potential Topics to select: Music,Game,Fitness,Study,Sport,Dance,News
- The reason for choosing from the given list is to make sure the recommendation algorithm can work properly. As there are limited number of sample users being loaded into database, selecting courses/topics/major from a smaller amount data will make sure a higher chance in common so that recommendation algorithm will always have someone to recommend.


