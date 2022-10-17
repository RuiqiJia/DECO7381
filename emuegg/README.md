# Getting Started
This document is a guide for setting up a development environment for Cultural Bridge that uses:
1. windows
1. python 3.10.8
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

## Install Django and run django server
1. navigate to the project folder and run the following command:
- `pip install django`
- `pip install channels`
- `pip install mysqlclient`
- `pip install branca`
- `pip install folium`
- `pip install geocoder`
- `pip install geopy`
- `pip install Pillow`
1. After installing all the dependencies, run the following command to start the server:
- `python manage.py migrate`
- `python manage.py runserver`
1. visit http://127.0.0.1:8000/ to view the website

## Accesse database and create superuser
1. navigate to the project folder and run the following command:
- `python manage.py createsuperuser`
1. follow the instruction to create a superuser
1. visit http://127.0.0.1:8000/admin/ and login with the newly created superuser credentials

## Other instructions
1. The application is using mobile first design approach, for better viewing experience, navigate to inspect [F12] on your browser and choose IPhone XR with 100% zoom.
1. Information Entries Format(Please follow the instruction to enter the information if needed)：
- For single field, if multiple topics/courses requires, seperate them with comma without space (e.g. "A,B")
- Topics：sports,music
- Courses: DECO3801,DECO7381


