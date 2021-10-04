from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth.decorators import login_required

from users.models import Profile, Message
from users.forms import CustomUserCreationForm, ProfileForm, SkillForm, MessageForm
from users.utils import searchProfiles, paginateProfiles

# Create your views here.

def loginUser(request):

    page = 'login'

    if request.user.is_authenticated:
        return redirect('profiles')

    if request.method == 'POST':
        username = request.POST['username'].lower()
        password = request.POST['password']

        try:
            user = User.objects.get(username=username)
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, message='You successfully logged in')
                return redirect(request.GET['next'] if 'next' in request.GET else 'account')
            else:
                messages.error(request, 'Password is incorrect!')
        except:
            messages.error(request, 'Username does not exist!')

    return render(request=request, template_name='users/login_register.html')

@login_required(login_url='login')
def logoutUser(request):

    logout(request)
    messages.info(request, 'User was logged out!')

    return redirect('login')


def registerUser(request):

    page = 'register'

    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.username = user.username.lower()
            user.save()

            messages.success(request, 'User account was created')

            login(request, user)
            return redirect('edit-account')
        else:
            messages.error(request, 'An error has occurred during registration!')
    else:
        form = CustomUserCreationForm()

    context = {
        'page': page,
        'form': form,
    }

    return render(request, template_name='users/login_register.html', context=context)


def profiles(request):

    profiles, search_query = searchProfiles(request)

    profiles, custom_range = paginateProfiles(request=request, profiles=profiles, results=3)

    context = {
        'profiles': profiles,
        'search_query': search_query,
        'custom_range': custom_range
    }

    return render(request=request, template_name='users/profiles.html', context=context)


def userProfile(request, pk):

    profile = Profile.objects.get(id=pk)

    topSkills = profile.skill_set.exclude(description__exact='')
    otherSkills = profile.skill_set.filter(description='')

    context = {
        'profile': profile,
        'topSkills': topSkills,
        'otherSkills': otherSkills
    }

    return render(request=request, template_name='users/user-profile.html', context=context)

@login_required(login_url='login')
def userAccount(request):

    profile = request.user.profile

    skills = profile.skill_set.all()
    projects = profile.project_set.all()

    context = {
        'profile': profile,
        'skills': skills,
        'projects': projects,
    }
    return render(request, template_name='users/account.html', context=context)


@login_required(login_url='login')
def editAccount(request):

    profile = request.user.profile
    form = ProfileForm(instance=profile)

    if request.method == 'POST':
        form = ProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            return redirect('account')

    context = {
        'form': form
    }

    return render(request, template_name='users/profile_form.html', context=context)


@login_required(login_url='login')
def createSkill(request):

    profile = request.user.profile

    if request.method == 'POST':
        form = SkillForm(request.POST)
        if form.is_valid():
            skill = form.save(commit=False)
            skill.owner = profile
            skill.save()
            messages.info(request, 'Skill was added successfully!')
            return redirect('account')
    else:
        form = SkillForm()

    context = {
        'form': form
    }

    return render(request, template_name='users/skill_form.html', context=context)


@login_required(login_url='login')
def updateSkill(request, pk):

    profile = request.user.profile
    skill = profile.skill_set.get(id=pk)

    if request.method == 'POST':
        form = SkillForm(request.POST, instance=skill)
        if form.is_valid():
            skill.save()
            messages.info(request, 'Skill was updated successfully!')
            return redirect('account')
    else:
        form = SkillForm(instance=skill)

    context = {
        'form': form
    }

    return render(request, template_name='users/skill_form.html', context=context)


@login_required(login_url='login')
def deleteSkill(request, pk):

    profile = request.user.profile
    skill = profile.skill_set.get(id=pk)

    if request.method == 'POST':
        skill.delete()
        messages.info(request, message='Skill was deleted successfully!')
        return redirect('account')

    context = {
        'object': skill
    }

    return render(request, template_name='delete_template.html', context=context)


@login_required(login_url='login')
def inbox(request):

    profile = request.user.profile
    messageRequests = profile.messages.all()
    unreadCount = messageRequests.filter(is_read=False).count()

    context = {
        'messageRequests': messageRequests,
        'unreadCount': unreadCount
    }

    return render(request, template_name='users/inbox.html', context=context)


@login_required(login_url='login')
def viewMessage(request, pk):

    profile = request.user.profile
    message = profile.messages.get(id=pk)
    if message.is_read != True:
        message.is_read = True
        message.save()

    context = {
        'message': message
    }

    return render(request, template_name='users/message.html', context=context)


def createMessage(request, pk):

    recipient = Profile.objects.get(id=pk)
    form = MessageForm()

    try:
        sender = request.user.profile
    except:
        sender = None

    if request.method == 'POST':
        form = MessageForm(request.POST)
        if form.is_valid():
            message = form.save(commit=False)
            message.sender = sender
            message.recipient = recipient
            if sender:
                message.name = sender.name
                message.email = sender.email

            message.save()

            messages.success(request, 'Your message was successfully sent!')
            return redirect('user-profile', pk=recipient.id )

    context = {
        'recipient': recipient,
        'form': form
    }

    return render(request, template_name='users/message_form.html', context=context)
