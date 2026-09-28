"""Structural checks for the ZHA TS0044 scene switch blueprint."""

from pathlib import Path

import pytest
import yaml

BLUEPRINT_PATH = (
    Path(__file__).resolve().parent.parent
    / "blueprints"
    / "automation"
    / "scene-switch-ts0044-zha"
    / "scene-switch-ts0044-zha.yaml"
)


class Input(str):
    """Value of a `!input` tag: the name of the referenced input."""


class BlueprintLoader(yaml.SafeLoader):
    """SafeLoader that understands Home Assistant's `!input` tag."""


BlueprintLoader.add_constructor(
    "!input", lambda loader, node: Input(loader.construct_scalar(node))
)


@pytest.fixture(scope="module")
def blueprint():
    return yaml.load(BLUEPRINT_PATH.read_text(encoding="utf-8"), Loader=BlueprintLoader)


def declared_inputs(inputs):
    """Map every leaf input key to its definition, flattening sections."""
    leaves = {}
    for key, definition in inputs.items():
        if "input" in definition:
            leaves.update(declared_inputs(definition["input"]))
        else:
            leaves[key] = definition
    return leaves


def input_references(node):
    if isinstance(node, Input):
        yield str(node)
    elif isinstance(node, dict):
        for value in node.values():
            yield from input_references(value)
    elif isinstance(node, list):
        for item in node:
            yield from input_references(item)


def body(blueprint):
    return {key: value for key, value in blueprint.items() if key != "blueprint"}


def test_every_reference_is_declared(blueprint):
    declared = declared_inputs(blueprint["blueprint"]["input"])
    assert set(input_references(body(blueprint))) <= set(declared)


def test_every_input_is_used(blueprint):
    declared = declared_inputs(blueprint["blueprint"]["input"])
    assert set(declared) <= set(input_references(body(blueprint)))


PRESS_SUFFIXES = {
    "remote_button_short_press": "press",
    "remote_button_double_press": "double_press",
    "remote_button_long_press": "held",
}


def test_each_trigger_runs_the_actions_of_its_button(blueprint):
    """Catch copy-paste slips across the 12 near-identical triggers and routes."""
    triggers = {trigger["id"]: trigger["event_data"] for trigger in blueprint["triggers"]}
    routes = {
        option["conditions"][0]["id"]: option["sequence"]
        for option in blueprint["actions"][0]["choose"]
    }
    assert set(routes) == set(triggers)
    for trigger_id, event_data in triggers.items():
        assert event_data["device_id"] == "ts0044_device", trigger_id
        press = PRESS_SUFFIXES[event_data["command"]]
        assert routes[trigger_id] == f"button_{event_data['endpoint_id']}_{press}", trigger_id
    presses = {(data["endpoint_id"], data["command"]) for data in triggers.values()}
    assert len(presses) == len(triggers) == 12
