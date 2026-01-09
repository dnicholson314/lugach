import asyncio
from canvasapi import Canvas
from textual import work
from textual.app import ComposeResult
from textual.containers import HorizontalGroup, VerticalGroup
from textual.widgets import Button, SelectionList

from lugach.core import cvutils as cvu, mappings


class CourseMappingsForm(VerticalGroup):
    _canvas: Canvas | None

    def __init__(self):
        super().__init__()
        try:
            self._canvas = cvu.create_canvas_object()
        except Exception:
            self._canvas = None

    def compose(self) -> ComposeResult:
        with HorizontalGroup():
            yield Button(label="Refresh", variant="primary")
        with VerticalGroup(classes="cv_selection_list_wrapper"):
            yield SelectionList(name="Select Canvas courses")

    @work(exclusive=True)
    async def update_selections(self) -> None:
        selection_list = self.query_one(SelectionList)
        selection_list.loading = True

        try:
            self._canvas = await asyncio.to_thread(cvu.create_canvas_object)
        except Exception:
            self._canvas = None

        saved_selections = mappings.load_canvas_course_ids()
        selections = []
        if self._canvas:
            selections = [
                (course.name, course.id, course.id in saved_selections)
                for course in await asyncio.to_thread(cvu.get_courses, self._canvas)
            ]
        selection_list.clear_options()
        selection_list.add_options(selections)

        selection_list.loading = False

    def on_mount(self) -> None:
        self.update_selections()

    async def on_button_pressed(self, event: Button.Pressed) -> None:
        label = event.button.label
        if label == "Refresh":
            self.update_selections()

    async def on_selection_list_selection_toggled(
        self, event: SelectionList.SelectionToggled[int]
    ):
        selected_value = event.selection.value
        all_values = event.selection_list.selected
        if selected_value in all_values:
            mappings.save_canvas_course_id(selected_value)
        else:
            mappings.delete_canvas_course_id(selected_value)
