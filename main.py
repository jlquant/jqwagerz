#!/usr/bin/env python3
import time

from nicegui import ui
from nicegui import events

default_teams = 5

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
    {"id": idx, "name": f"Team {idx+1}", "points": 0} for idx in range(default_teams)
]

round_cols = [
    {"name": "name", "label": "Team", "field": "name", "sortable": False},
    {
        "name": "guess",
        "label": "Guess",
        "field": "guess",
        "sortable": True,
    },
]
round = []


def _generate_question_raw():
    return [
        {
            "txt": "In m/s, what is the airspeed velocity of an unladed European swallow?",
            "source": "chatgpt",
            # 11 m/s
        },
        {
            "txt": "How many attendees came to infocomm last year?",
            "source": "infocomm.com?",
            # TODO
        },
        {
            "txt": "How many part numbers are in our SAP instance?",
            "source": "Local SAP Wizards",
        },
        {
            "txt": "In what year was IEEE founded?",
            "source": "ieee.org",
            # 1/1/63
        },
        {
            "txt": "In GHz, what is the frequency range of IEEE 802.11ac?",
            "source": "ieee.org",
            # 5 GHz band
        },
        {
            "txt": "In what year was IEEE 802.11 first released?",
            "source": "ieee.org",
            # 1997
        },
        {
            "txt": "How many brands are listed on the 'About Us' on the AVD website?",
            "source": "legrandav.com",
            # 10
        },
        {
            "txt": "In decibels, During take off, what is the estimated peak noise level of a F-35 Lightning II?",
            "source": "healthvermont.gov",
            #
        },
        {
            "txt": "In meters, what is the diameter of the optical element of the  Gran Telescopio Canarias telescope?",
            "source": "wikipedia.org",
            #
        },
    ]


def _make_score_table():
    team_table = ui.table(
        title="Scores",
        rows=teams,
        row_key="id",
        columns=columns,
    ).classes("w-full")

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
    _configure_score_table(team_table)


def _configure_score_table(team_table):
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

    team_table.on("edit_val", edit_val)


def _make_round_table():
    round_table = ui.table(
        title="Round",
        rows=round,
        row_key="id",
        columns=round_cols,
    ).classes("w-full")

    with round_table.row():
        ui.button("New round", on_click=lambda: _generate_round_rows(round_table))

    _configure_round_table(round_table)
    _generate_round_rows(round_table)


def _configure_round_table(round_table):
    def edit_guess(e: events.GenericEventArguments) -> None:
        for row in round:
            if row["id"] == e.args["id"]:
                row.update(e.args)
        round_table.update()

    round_table.add_slot(
        "body",
        r"""
        <q-tr :props="props">
            <q-td key="name" :props="props">
                {{ props.row.name }}
            </q-td>
            <q-td key="guess" :props="props">
                {{ props.row.guess }}
                <q-popup-edit v-model="props.row.guess" v-slot="scope"
                    @update:model-value="() => $parent.$emit('edit_guess', props.row)"
                >
                    <q-input v-model.number="scope.value" type="number" dense autofocus counter @keyup.enter="scope.set" />
                </q-popup-edit>
            </q-td>
        </q-tr>
    """,
    )

    round_table.on("edit_guess", edit_guess)


def _generate_round_rows(round_table):
    while round:
        round.pop(0)

    round.append(
        {
            "id": 0,
            "name": "",
            "guess": 0,
        }
    )

    round.extend(
        [
            {
                "id": idx + 1,
                "name": team["name"],
                "guess": 0,
            }
            for idx, team in enumerate(teams)
        ]
    )

    round_table.update()


def _make_question_box():
    questions.label = ui.label("").style(
        "font-size: 2.5em; font-weight: bold; margin-bottom: 10px; text-align: left;"
    )
    questions.source = ui.label("").style(
        "font-size: 1.5em; font-weight: bold; margin-bottom: 10px; text-align: left;"
    )
    ui.separator()
    with ui.row():
        ui.button("Prev question", on_click=lambda: questions.previous_question())
        ui.button("Next question", on_click=lambda: questions.next_question())


class Questions:
    def __init__(self):
        self.label = None
        self.source = None
        self._questions = _generate_question_raw()
        self._question_idx = -1

    def next_question(self):
        if self._questions:
            self._question_idx = min(self._question_idx + 1, len(self._questions) - 1)
            self._set_labels()

    def previous_question(self):
        if self._questions:
            self._question_idx = max([0, self._question_idx - 1])
            self._set_labels()

    def _set_labels(self):
        q = self._questions[self._question_idx]
        self.label.set_text(q["txt"])
        self.source.set_text(f"Source: {q['source']}")


questions = Questions()


ui.label("JQWagerz")
_make_question_box()
with ui.row().classes("w-full"):
    with ui.column().classes("w-1/3"):
        _make_score_table()

    with ui.column().classes("w-1/2"):
        _make_round_table()

ui.run()
