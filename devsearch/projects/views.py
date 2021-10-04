from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from projects.models import Project
from projects.forms import ProjectForm, ReviewForm
from projects.utils import searchProjects, paginateProjects

# Create your views here.

def projects(request):

    projects, search_query = searchProjects(request=request)

    projects, custom_range = paginateProjects(request=request, projects=projects, results=6)

    context = {
        'projects': projects,
        'search_query': search_query,
        'custom_range': custom_range
    }

    return render(request, template_name='projects/projects.html', context=context)


def project(request, pk):

    projectObj = Project.objects.get(id=pk)
    tags = projectObj.tags.all()
    form = ReviewForm()

    if request.method == 'POST':
        form = ReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.project = projectObj
            review.owner = request.user.profile
            review.save()

        # Update project votecount

        projectObj.getVoteCount

        messages.success(request, 'Your review was successfully submitted!')
        return redirect('project', pk=projectObj.id)

    context = {
        'project': projectObj,
        'tags': tags,
        'form': form
    }

    return render(request=request, template_name='projects/project.html', context=context)


@login_required(login_url='login')
def createProject(request):

    profile = request.user.profile

    if request.method == 'POST':
        form = ProjectForm(request.POST, request.FILES)
        if form.is_valid():
            project = form.save(commit=False)
            project.owner = profile
            project.save()
            messages.info(request, message='Project was created successfully!')
            return redirect('account')
    else:
        form = ProjectForm()

    context = {
        'form': form,
    }

    return render(request=request, template_name='projects/project_form.html', context=context)


@login_required(login_url='login')
def updateProject(request, pk):

    profile = request.user.profile
    project = profile.project_set.get(id=pk)

    if request.method == 'POST':
        form = ProjectForm(request.POST, request.FILES, instance=project)
        if form.is_valid():
            form.save()
            messages.info(request, message='Project was updated successfully!')
            return redirect('account')
    else:
        form = ProjectForm(instance=project)
    context = {
        'form': form,
    }

    return render(request=request, template_name='projects/project_form.html', context=context)


@login_required(login_url='login')
def deleteProject(request, pk):

    profile = request.user.profile
    project = profile.project_set.get(id=pk)
    if request.method == 'POST':
        project.delete()
        messages.info(request, message='Project was deleted successfully!')
        return redirect('account')
    context = {
        'object': project,
    }

    return render(request=request, template_name='delete_template.html', context=context)
