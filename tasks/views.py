from django.http import Http404
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.db.models import Q, Count
from django.contrib.auth.decorators import login_required
from .models import List, Task
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from .forms import TaskForm


@login_required
def pomodoro_view(request):
    return render(request, 'tools/pomodoro.html')

class TaskCreateView(LoginRequiredMixin, CreateView):
    model = Task
    form_class = TaskForm
    template_name = 'tasks/task_form.html'
    success_url = reverse_lazy('task-list')

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        # Безопасно фильтруем списки по владельцу
        form.fields['list'].queryset = List.objects.filter(owner=self.request.user)
        return form


    def form_valid(self, form):
        form.instance.owner = self.request.user 
        return super().form_valid(form)


class TaskUpdateView(LoginRequiredMixin, UpdateView):
    model = Task
    form_class = TaskForm
    template_name = 'tasks/task_update.html'
    success_url = reverse_lazy('task-list')



class ListListView(LoginRequiredMixin, ListView):
    model = List
    template_name = 'tasks/list_list.html'
    context_object_name = 'lists'

    def get_queryset(self):
        return List.objects.filter(owner=self.request.user)


class ListCreateView(LoginRequiredMixin, CreateView):
    model = List
    fields = ['name']
    template_name = 'tasks/list_create.html'
    success_url = reverse_lazy('list-list')

    def form_valid(self, form):
        form.instance.owner = self.request.user
        return super().form_valid(form)


class ListUpdateView(LoginRequiredMixin, UpdateView):
    model = List
    fields = ['name']
    template_name = 'tasks/list_update.html'
    success_url = reverse_lazy('list-list')


class ListDeleteView(LoginRequiredMixin, DeleteView):
    model = List
    template_name = 'tasks/list_confirm_delete.html'
    success_url = reverse_lazy('list-list')

class ListDetailView(LoginRequiredMixin, DetailView):
    model = List
    template_name = 'tasks/list_view.html'
    context_object_name = 'list'

    def get_object(self, queryset=None):
        obj = super().get_object(queryset)
        if obj.owner != self.request.user:
            raise Http404("Список не найден.")
        return obj

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        now = timezone.now()
        
        # Получаем все задачи для данного списка
        tasks = Task.objects.filter(list=self.object)

        # Получаем фильтры из GET
        status = self.request.GET.get('status')
        search = self.request.GET.get('search')
        sort = self.request.GET.get('sort')

        if search:
            tasks = tasks.filter(title__icontains=search)

        if status == 'completed':
            tasks = tasks.filter(completed=True)
        elif status == 'not_completed':
            tasks = tasks.filter(completed=False)
        elif status == 'urgent':
            tasks = tasks.filter(completed=False, priority='high')
        elif status == 'overdue':
            tasks = tasks.filter(completed=False, deadline__lt=now)

        allowed_sorts = ['deadline', '-deadline', 'created_at', '-created_at', 'priority', '-priority']
        if sort in allowed_sorts:
            tasks = tasks.order_by(sort)
        else:
            tasks = tasks.order_by('deadline')

        context['tasks'] = tasks
        context['now'] = now
        context['lists'] = self.request.user.lists.all()  # если нужно для бокового меню
        return context

class TaskListView(LoginRequiredMixin, ListView):
    model = Task
    template_name = 'tasks/task_list.html'
    context_object_name = 'tasks'

    def get_queryset(self):
        qs = super().get_queryset().filter(list__owner=self.request.user)

        status = self.request.GET.get('status')
        search = self.request.GET.get('search')
        now = timezone.now()

        if search:
            qs = qs.filter(title__icontains=search)

        if status == 'completed':
            qs = qs.filter(completed=True)
        elif status == 'not_completed':
            qs = qs.filter(completed=False)
        elif status == 'urgent':
            qs = qs.filter(completed=False, priority='high')
        elif status == 'overdue':
            qs = qs.filter(completed=False, deadline__lt=now)

        list_id = self.request.GET.get('list')
        if list_id:
            qs = qs.filter(list_id=list_id)

        # Получаем параметр сортировки из запроса
        sort = self.request.GET.get('sort')

        # Безопасно задаём сортировку
        allowed_sorts = ['deadline', '-deadline', 'created_at', '-created_at', 'priority', '-priority']
        if sort in allowed_sorts:
            qs = qs.order_by(sort)
        else:
            qs = qs.order_by('deadline')  # сортировка по умолчанию

        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['now'] = timezone.now()
        context['lists'] = self.request.user.lists.all()  # чтобы вывести боковое меню списков
        return context

class TaskDeleteView(DeleteView):
    model = Task
    template_name = 'tasks/task_confirm_delete.html'

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        success_url = request.META.get('HTTP_REFERER', '/')
        self.object.delete()
        return redirect(success_url)

    def get_success_url(self):
        return reverse_lazy('task-list') + f'?list={self.object.list.id}'


def toggle_task_status(request, pk):
    task = get_object_or_404(Task, pk=pk)
    if task.completed:
        task.completed = False
        task.completed_at = None
    else:
        task.completed = True
        task.completed_at = timezone.now()
    task.save()
    return redirect(request.META.get('HTTP_REFERER', 'task-list'))

@login_required
def statistics_view(request):
    user = request.user
    tasks = Task.objects.filter(list__owner=user)

    total = tasks.count()
    completed = tasks.filter(completed=True).count()
    not_completed = tasks.filter(completed=False).count()
    overdue = tasks.filter(deadline__lt=timezone.now(), completed=False).count()
    urgent = tasks.filter(priority='high', completed=False).count()

    list_stats = List.objects.filter(owner=user).annotate(
        total_tasks=Count('tasks'),
        completed_tasks=Count('tasks', filter=Q(tasks__completed=True))
    )

    # Подготовка данных для графиков
    pie_data_all = {
        'labels': ['Выполненные', 'Не выполненные', 'Просроченные'],
        'data': [completed, not_completed, overdue]
    }

    pie_data_lists = {
        'labels': [lst.name for lst in list_stats],
        'data': [lst.total_tasks for lst in list_stats]
    }

    context = {
        'total': total,
        'completed': completed,
        'half_total': total / 2 if total else 0,
        'not_completed': not_completed,
        'overdue': overdue,
        'urgent': urgent,
        'list_stats': list_stats,
        'pie_data_all': pie_data_all,
        'pie_data_lists': pie_data_lists
    }
    return render(request, 'tasks/statistics.html', context)