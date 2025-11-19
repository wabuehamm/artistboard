from iommi import Column, Form, Page, Table

from artistboard.models import Todo


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


todo_delete = Form.delete(instance=lambda pk, **_: Todo.objects.get(pk=pk))
