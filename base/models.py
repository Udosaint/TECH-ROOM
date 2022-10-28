from dataclasses import dataclass
from email.policy import default
from django.db import models

#importing the user model from django
#from django.contrib.auth.models import User

#when you want to customize your user Model import this
from django.contrib.auth.models import AbstractUser

# Create your models here.


class User(AbstractUser):
    name = models.CharField(max_length=200, null=True)
    email = models.EmailField(unique=True,null=True)
    bio = models.TextField(null=True)

    avatar = models.ImageField(null=True, default="avatar.svg")

    # this part makes the user user to login using email instead of username
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []


class Topic(models.Model):
    name = models.CharField(max_length=200)

    def __str__(self):
        return self.name
    



class Room(models.Model):
    #host is the user that created the Room
    host = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    topic = models.ForeignKey(Topic, on_delete=models.SET_NULL, null=True)
    name = models.CharField(max_length=200)
    description = models.TextField(null=True, blank=True) #null for db to accept empty value, blank to accept blank when saving
    #participants are the user that join the room
    participants = models.ManyToManyField(User, related_name='participants', blank=True)
    updated = models.DateTimeField(auto_now=True) #always update the date
    created = models.DateTimeField(auto_now_add=True) #add the date created


    class Meta:
        #specifying how my data will be order when displaying
        #adding - to the field or column name order it in descending 
        ordering = ['-updated', '-created']

    def __str__(self):
        return self.name

class Message(models.Model):
    #user that sent the message or comments
    user = models.ForeignKey(User, on_delete=models.CASCADE) #CASCADE means delete this when the user is deleted from database
    room = models.ForeignKey(Room, on_delete=models.CASCADE) 
    body = models.TextField()
    updated = models.DateTimeField(auto_now=True) #always update the date
    created = models.DateTimeField(auto_now_add=True) #add the date created

    class Meta:
        #specifying how my data will be order when displaying
        #adding - to the field or column name order it in descending 
        ordering = ['-updated', '-created']

    def __str__(self):
        return self.body[0:50] #[0:50] this returns the first 50 character