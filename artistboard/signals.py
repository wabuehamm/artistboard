from artistboard.models import Event, EventTodo, Season, SeasonTodo, Todo
from django.db.models.signals import post_save
from django.dispatch import receiver


@receiver(post_save)
def generate_todos(sender, instance, **_):
    if sender == Season:
        for todo in Todo.objects.filter(available_for="season"):
            if SeasonTodo.objects.filter(season=instance, todo=todo).count() == 0:
                SeasonTodo(season=instance, todo=todo).save()
    elif sender == Event:
        for todo in Todo.objects.filter(available_for="event"):
            if EventTodo.objects.filter(event=instance, todo=todo).count() == 0:
                EventTodo(event=instance, todo=todo).save()
