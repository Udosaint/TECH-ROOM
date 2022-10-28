from multiprocessing import context
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.contrib import messages
# to enforce login for pages
from django.contrib.auth.decorators import login_required
# for doing multiple filtering
from django.db.models import Q
#from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
#from django.contrib.auth.forms import UserCreationForm
from .models import Room, Topic, Message, User
from .forms import RoomForm, UserForm, MyUserCreationForm

# Create your views here.

def loginPage(request):
    page = 'login'
    if request.user.is_authenticated:
        return redirect('home')

    if request.method == "POST":
        email = request.POST.get('email').lower()
        password = request.POST.get('password')

        # checking if the user exist
        try:
            user = User.objects.get(email=email)
        except:    
            messages.error(request, 'User does not exist')
        
        user = authenticate(request, email=email, password=password)

        if user is not None:
            login(request,user)
            return redirect('home')
        else:
            messages.error(request, 'Email or Password does not exist')      
    context = {'page':page}
    return render(request,'base/login_register.html', context)




def logoutUser(request):
    logout(request)
    return redirect('home')



def registerPage(request):
    page = 'register'
    form = MyUserCreationForm()

    if request.method == "POST":
        form =MyUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.username = user.username.lower()
            user.save()
            login(request, user)
            return redirect('home')
        else:
            messages.error(request, 'An error occurred!')
    context = {'page':page, 'form':form}
    return render(request, 'base/login_register.html', context)


def home(request):

    # get a request from the website, use for filtering
    q = request.GET.get('q') if request.GET.get('q') != None else '' #inline if statement to check if there is no request  then return ''
    # to list all the room
    rooms = Room.objects.filter(
        Q(topic__name__icontains=q) |
        Q(name__icontains=q) |
        Q(description__icontains=q)
        ) 
        # Q for multiple filtering
        #icontains get the value that are in q, i in the contains make it to be CSAE insensitive

    # to list all the topic
    topics = Topic.objects.all()[0:5]
    # to get the number of room
    room_count = rooms.count()

    #for the recent activities
    comments = Message.objects.filter(Q(room__topic__name__icontains=q))
    context = {'rooms': rooms, 'topics':topics, 'room_count':room_count, 'comments':comments}
    return render(request, 'base/home.html', context)




def room(request,pk):
    room = Room.objects.get(id=pk)

    #get all the messages for a particular room
    #message is the model/table name for Message but here you write it in small letters
    comments = room.message_set.all().order_by('-created')

    participants = room.participants.all()

    #for posting my comments
    if request.method == "POST":
        comment = Message.objects.create(
            user = request.user,
            room = room,
            body = request.POST.get('body') #body here is from my input field for the comment
        )
        #adding the user as the partictpant
        room.participants.add(request.user)
        return redirect('room', pk=room.id)


    context = {'room': room, 'comments':comments, 'participants':participants}
    return render(request, 'base/room.html', context)



def userProfile(request, pk):
    user = User.objects.get(id=pk)
    #getting all the rooms of the user
    rooms = user.room_set.all()
    comments = user.message_set.all()
    topics = Topic.objects.all()
    context = {'user':user, 'rooms':rooms, 'comments':comments, 'topics':topics}
    return render(request, 'base/profile.html',context)


@login_required(login_url='login')
def createRoom(request):
    form = RoomForm
    page = "Create"
    topics = Topic.objects.all()
    if request.method == 'POST':
        #code that will make the new input filed for the topic work
        topic_name = request.POST.get('topic')
        topic, created = Topic.objects.get_or_create(name=topic_name)
        #topic,this code return the topic name that is from the drop down list and assign it to topic
        #while created, get the topic that is typed in the input file that is not there ans assign to created
        #code ends here

        Room.objects.create(
            host = request.user,
            topic = topic,
            name = request.POST.get('name'),
            description = request.POST.get('description'),
        )


        # this code down here is for workig with normal input that come from the model
        # form = RoomForm(request.POST)
        # if form.is_valid():
        #     room = form.save(commit=False)
        #     #add the user as the Host
        #     room.host = request.user
        #     room.save()
        return redirect('home')
    context = {'form':form, 'topics':topics, 'page':page}
    return render(request, 'base/room_form.html', context)





@login_required(login_url='login')
def updateRoom(request, pk):
    #get the room with id
    room = Room.objects.get(id=pk)
    form = RoomForm(instance=room)
    topics = Topic.objects.all()
    page = "Update"
    if request.user != room.host:
        return HttpResponse('you are allow here')

    if request.method == 'POST':

        topic_name = request.POST.get('topic')
        topic, created = Topic.objects.get_or_create(name=topic_name)
        room.name = request.POST.get('name')
        room.topic = topic
        room.description = request.POST.get('description')
        room.save()
        # form = RoomForm(request.POST, instance=room)
        # if form.is_valid():
        #     form.save()
        return redirect('home')
    context = {'form': form, 'topics':topics, 'page':page, 'room':room}
    return render(request, 'base/room_form.html', context)




@login_required(login_url='login')
def deleteRoom(request, pk):
    room = Room.objects.get(id=pk)
    if request.method == 'POST':
        room.delete()
        return redirect('home')
    return render(request, 'base/delete.html', {'obj': room})


@login_required(login_url='login')
def deleteComment(request, pk):
    comment = Message.objects.get(id=pk)
    if request.method == 'POST':
        comment.delete()
        return redirect('home')
    return render(request, 'base/delete.html', {'obj': comment})



@login_required(login_url='login')
def updateUser(request):
    user = request.user
    form = UserForm(instance=user)

    if request.method == "POST":
        form = UserForm(request.POST, request.FILES, instance=user) #request.FILES is when you are uploading files that you add it
        if form.is_valid():
            form.save()
            return redirect('user-profile', pk=user.id)
    context = {'form':form}
    return render(request, 'base/update-user.html', context)

def topicsPage(request):
    q = request.GET.get('q') if request.GET.get('q') != None else ''
    topics = Topic.objects.filter(name__icontains=q)
    context = {'topics':topics}
    return render(request, 'base/topics.html',context)


def activityPage(request):
    q = request.GET.get('q') if request.GET.get('q') != None else ''
    
    #for the recent activities
    comments = Message.objects.filter(Q(room__topic__name__icontains=q))[0:5]
    topics = Topic.objects.filter(name__icontains=q)
    context = {'topics':topics, 'comments':comments}
    return render(request, 'base/activity.html',context)