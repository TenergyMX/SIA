from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.shortcuts import render, redirect
from django.http import JsonResponse
from users.models import *

from modules.utils import *
# from helpers.enviar_correo import *

# Create your views here.
