# Scene switch (TS0044, ZHA)

This blueprint runs your actions when you press a button on a Tuya TS0044 scene switch. MOES sells this switch. The blueprint works with ZHA only.

Supported device: manufacturer `_TZ3000_wkai4ga5`, model `TS0044`.

[![Import the blueprint into Home Assistant](https://my.home-assistant.io/badges/blueprint_import.svg)](https://my.home-assistant.io/redirect/blueprint_import/?blueprint_url=https%3A%2F%2Fgithub.com%2Fgbrunow%2Fhome-assistant%2Fblob%2Fmain%2Fblueprints%2Fautomation%2Fscene-switch-ts0044-zha%2Fscene-switch-ts0044-zha.yaml)

To import the blueprint by hand:

1. In Home Assistant, go to Settings > Automations & scenes > Blueprints.
2. Select Import blueprint.
3. Paste this URL: `https://github.com/gbrunow/home-assistant/blob/main/blueprints/automation/scene-switch-ts0044-zha/scene-switch-ts0044-zha.yaml`

## Use

The form has four groups. Each group has a dropdown that picks a button on the switch, for example ◰ Upper-left · Button 1. Below the dropdown, each group has sections for the actions of a single press, a double press, and a long press. Group 1 starts on button 1, group 2 on button 2, and so on.

To move all actions of a group to a different button, pick another button in the dropdown of the group. To move one action, cut it in one section. Then paste it in the other section.

If two groups pick the same button, a press on that button runs the actions of both groups. The blueprint also creates a notification about it. To stop the notification, turn off Warn when groups share a button.

To use the same actions on two switches, put the actions in a script. Then call the script from the automation of each switch.

## Move from the TS0044 Zigbee Remote blueprint

This blueprint uses the same input names as the [TS0044 Zigbee Remote](https://github.com/zpriddy/Home-Assistant/blob/main/blueprints/ts0044_zigbee_remote.yaml) blueprint by Zachary Priddy. Earlier versions of that blueprint have the name Moes Scene Switch. To move an automation from that blueprint:

1. Import this blueprint.
2. Open the automation and select Edit in YAML.
3. Change `use_blueprint` > `path` to `gbrunow/scene-switch-ts0044-zha.yaml`.
4. Save the automation. Your actions stay the same.
