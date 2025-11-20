from django.urls import reverse
from iommi import Column, Form, Page, Table, EditTable

from artistboard.models import Todo, SeasonTodo, EventTodo
from iommi.form import save_nested_forms


class TodoView(Page):
    todos = Table(
        auto__model=Todo,
        page_size=10,
        columns__edit=Column.edit(),
        columns__delete=Column.delete(),
    )
    new_todo = Form.create(
        title="New Todo",
        auto__model=Todo,
        extra__redirect_to=".",
    )


class TodoEdit(Form):
    todo = Form.edit(auto__model=Todo, instance=lambda pk, **_: Todo.objects.get(pk=pk))

    season_todos = EditTable(
        auto__model=SeasonTodo,
        # columns__season__filter__include=True,
        columns__description=Column(attr="todo__description", after=3),
        columns__done__field__include=True,
        rows=lambda pk, **_: SeasonTodo.objects.filter(todo__pk=pk),
        edit_actions__add_row__include=False,
        # columns__done__filter__include=True,
        include=lambda pk, **_: Todo.objects.get(pk=pk).available_for == "season",
    )

    event_todos = EditTable(
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
