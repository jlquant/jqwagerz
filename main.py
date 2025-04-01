#!/usr/bin/env python3
import time

from nicegui import ui
from nicegui import events

columns = [
    {"name": "name", "label": "Team", "field": "name", "sortable": True},
    {
        "name": "points",
        "label": "Points",
        "field": "points",
        "sortable": True,
    },
]
teams = [
    {
        "id": idx,
        "name": f"Team {idx+1}",
        "points": 0
    
    }
    for idx in range(5)
]

team_table = ui.table(
    title="Scores",
    rows=teams,
    row_key="id",
    columns=columns,
).classes(
    "w-1/3"
)  # Set the width of the table

def edit_val(e: events.GenericEventArguments) -> None:
    for row in teams:
        if row["id"] == e.args["id"]:
            row.update(e.args)
    team_table.update()


team_table.add_slot(
    "body",
    r"""
    <q-tr :props="props">
        <q-td key="name" :props="props">
            {{ props.row.name }}
            <q-popup-edit v-model="props.row.name" v-slot="scope"
                @update:model-value="() => $parent.$emit('edit_val', props.row)"
            >
                <q-input v-model="scope.value" dense autofocus counter @keyup.enter="scope.set" />
            </q-popup-edit>
        </q-td>
        <q-td key="points" :props="props">
            {{ props.row.points }}
            <q-popup-edit v-model="props.row.points" v-slot="scope"
                @update:model-value="() => $parent.$emit('edit_val', props.row)"
            >
                <q-input v-model.number="scope.value" type="number" dense autofocus counter @keyup.enter="scope.set" />
            </q-popup-edit>
        </q-td>
    </q-tr>
""",
)

team_table.on('edit_val', edit_val)

with team_table.row():
    with team_table.cell():
        new_team_name = ui.input("team name")
    with team_table.cell():
        ui.button(
            "Add",
            on_click=lambda: (
                team_table.add_row({"name": new_team_name.value, "points": 0}),
                new_team_name.set_value(""),  # Clear input after adding
            ),
        )

ui.run()
