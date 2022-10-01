import csv
import pandas as pd
from django.core.management import BaseCommand, CommandError
from ..models import User

class Command(BaseCommand):
    help = 'Load the sample user csv file into the database'

    def add_arguments(self, parser):
        parser.add_argument('--path', type=str)

    def handle(self, *args, **kwargs):
        # remove the existing user data?

