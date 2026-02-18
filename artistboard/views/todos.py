from django.http import HttpResponseRedirect
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from iommi import Column, Form, Page, Table, EditTable
from iommi.form import save_nested_forms

from artistboard.models import Todo, SeasonTodo, EventTodo


class TodoView(Page):
    todos = Table(
        title=_("Todos"),
        auto__model=Todo,
        page_size=10,
        columns__edit=Column.edit(),
        columns__delete=Column.delete(),
    )
    new_todo = Form.create(
        title=_("New Todo"),
        auto__model=Todo,
        extra__redirect_to=".",
    )


class TodoEdit(Form):
    todo = Form.edit(title=_("Todo"), auto__model=Todo, instance=lambda pk, **_: Todo.objects.get(pk=pk))

    season_todos = EditTable(
        title=_("Season todos"),
        auto__model=SeasonTodo,
        columns__season__filter__include=True,
        columns__description=Column(attr="todo__description", after=3),
        columns__done__field__include=True,
        rows=lambda pk, **_: SeasonTodo.objects.filter(todo__pk=pk),
        edit_actions__add_row__include=False,
        # columns__done__filter__include=True,
        include=lambda pk, **_: Todo.objects.get(pk=pk).available_for == "season",
    )

    event_todos = EditTable(
        title=_("Event todos"),
        auto__model=EventTodo,
        # columns__event__filter__include=True,
        columns__description=Column(attr="todo__description", after=3),
        columns__done__field__include=True,
        # columns__done__filter__include=True,
        rows=lambda pk, **_: EventTodo.objects.filter(todo__pk=pk),
        edit_actions__add_row__include=False,
        include=lambda pk, **_: Todo.objects.get(pk=pk).available_for == "event",
    )

    class Meta:
        actions__submit__post_handler = save_nested_forms
        extra__redirect_to = lambda **_: reverse("main_menu.todos")


todo_delete = Form.delete(instance=lambda pk, **_: Todo.objects.get(pk=pk))


def toggleSeasonTodo(request, pk, todo_pk):
    todo = SeasonTodo.objects.get(pk=todo_pk)
    assert todo is not None, "Can't find season todo for pk %s" % todo_pk
    todo.done = not todo.done
    todo.save()
    return HttpResponseRedirect(reverse("main_menu.seasons"))


def toggleEventTodo(request, pk, todo_pk):
    todo = EventTodo.objects.get(pk=todo_pk)
    assert todo is not None, "Can't find event todo for pk %s" % todo_pk
    todo.done = not todo.done
    todo.save()
    return HttpResponseRedirect(reverse("main_menu.events"))
