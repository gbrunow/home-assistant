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


TRIGGER_SUFFIXES = {
    "remote_button_short_press": "single",
    "remote_button_double_press": "double",
    "remote_button_long_press": "long",
}
GROUP_INPUT_SUFFIXES = {"single": "press", "double": "double_press", "long": "held"}


def test_group_triggers_match_their_ids(blueprint):
    ids = []
    for trigger in blueprint["triggers"]:
        data = trigger["event_data"]
        assert data["device_id"] == "ts0044_device", trigger["id"]
        suffix = TRIGGER_SUFFIXES[data["command"]]
        assert trigger["id"] == f"button_{data['endpoint_id']}_{suffix}"
        ids.append(trigger["id"])
    assert len(set(ids)) == 12


def test_each_group_runs_its_actions_for_its_chosen_button(blueprint):
    """Catch copy-paste slips across the 12 near-identical group routes."""
    variables = blueprint["actions"][0]["variables"]
    for n in range(1, 5):
        assert variables[f"group_{n}"] == f"group_{n}_button"
    routes = {
        block["then"]: block["if"][0]["value_template"]
        for block in blueprint["actions"][2:]
    }
    assert routes == {
        f"button_{n}_{input_suffix}": (
            f"{{{{ trigger.id == 'button_' ~ group_{n} ~ '_{press}' }}}}"
        )
        for n in range(1, 5)
        for press, input_suffix in GROUP_INPUT_SUFFIXES.items()
    }


def test_group_n_defaults_to_button_n(blueprint):
    inputs = blueprint["blueprint"]["input"]
    for n in range(1, 5):
        assert inputs[f"group_{n}_button"]["default"] == str(n)
