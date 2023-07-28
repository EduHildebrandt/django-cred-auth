from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from django.contrib.auth import login, logout, authenticate
from django.db import IntegrityError
from .forms import TaskForm
from .models import Task
from django.utils import timezone
from django.contrib.auth.decorators import login_required

"""
Archivo encargado en la app de generar las funciones para las vistas de las diferentes urls de la web
todo lo que se define aca, se utiliza en la raiz del proyecto para atender una url
"""

# Create your views here.


def home(request):
    return render(request, 'home.html')


def signup(request):
    """
    render recibe como primer parametro request, como segundo parametro la pagina completa que le pasamos para que responda con eso, en este caso signup.html
    Para pasar parametros al html debemos poner como tercer parametro un diccionario
    como es un formulario, que manda los datos al mismo metodo, y como se utiliza el metodo Post, para que no se envie por url los datos de login, vamos a utilizar un if para distinguir si es la primera visita o ya hubo intento de logueo
    """
    if request.method == 'GET':
        return render(request, 'signup.html', {
            'form': UserCreationForm
        })
    else:
        if request.POST['password1'] == request.POST['password2']:
            # register user
            try:
                user = User.objects.create_user(username=request.POST['username'], password=request.POST['password1'])
                user.save()
                login(request, user)
                return redirect ('tasks')
            except IntegrityError:
                return render(request, 'signup.html', {
                    'form': UserCreationForm,
                    'error': 'El Usuario ya existe!!!'
                })
        return render(request, 'signup.html', {
            'form': UserCreationForm,
            'error': 'Las Contraseñas no coinciden!!!'
        })

@login_required
def tasks(request):
    tasks = Task.objects.filter(user=request.user, datecompleted__isnull=True)
    return render(request, 'tasks.html', {'tasks': tasks})

@login_required
def tasks_completed(request):
    tasks = Task.objects.filter(user=request.user, datecompleted__isnull=False).order_by('-datecompleted')
    return render(request, 'tasks.html', {'tasks': tasks})

@login_required
def create_tasks(request):
    if request.method == 'GET':
        return render (request, 'create_tasks.html', {
            'form': TaskForm
        })
    else:
        try:
            formulario = TaskForm(request.POST)
            new_task = formulario.save(commit=False)
            new_task.user = request.user
            new_task.save()
            return redirect('tasks')
        except ValueError:
            return render (request, 'create_tasks.html', {
                'form': TaskForm,
                'error': 'Por favor provea datos válidos'
            }) 
                   
@login_required
def task_detail(request, task_id):
    if request.method == 'GET':
        task = get_object_or_404(Task, pk=task_id, user=request.user)
        form = TaskForm(instance=task)
        return render(request, 'task_detail.html', {'task': task, 'form':form})
    else:
        try:
            task = get_object_or_404(Task, pk=task_id, user=request.user)
            form = TaskForm(request.POST, instance=task)
            form.save()
            return redirect('tasks')
        except ValueError:
            return render(request, 'task_detail.html', {'task': task, 'form':form, 'error': 'Error actualizando la Tarea'})

@login_required        
def complete_task (request, task_id):
    task = get_object_or_404(Task, pk=task_id, user=request.user)
    if request.method == 'POST':
        task.datecompleted = timezone.now()
        task.save()
        return redirect('tasks')

@login_required
def delete_task (request, task_id):
    task = get_object_or_404(Task, pk=task_id, user=request.user)
    if request.method == 'POST':
        task.delete()
        return redirect('tasks')

@login_required
def cerrar_sesion(request):
    logout(request)
    return redirect('home')

def loguearse(request):
    if request.method == 'GET':
        return render(request, 'loguearse.html', {
            'form':AuthenticationForm,
        })
    else:
        user = authenticate(request, username=request.POST['username'], password=request.POST['password'])
        if user is None:
            return render(request, 'loguearse.html', {
                'form':AuthenticationForm,
                'error': 'Usuario o Contraseña incorrectos',
            })
        else:
            login(request, user)
            return redirect('tasks')