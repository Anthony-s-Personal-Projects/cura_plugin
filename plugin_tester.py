import json
from pprint import pprint

# The plugin settings need to be in json format; this is to catch errors in the json string
def check_json_format(obj):
    try:
        json.loads(obj())
        print(f'"{obj.__name__}" passed the json format check!')
    except Exception as e:
        print(f'"{obj.__name__}" failed the json format check!')
        raise (e)

# The plugin's name needs to match the name specified in the settings otherwise cura won't load the plugin
def check_name_matching(obj):
    try:
        settings = json.loads(obj.getSettingDataString())
        if obj.__class__.__name__ == settings['key']:
            print(f'"{obj.__class__.__name__}" passed the script name check!')
        else:
            print(f'"{obj.__class__.__name__}" failed the json format check!')
    except Exception as e:
        raise (e)


# import plugin for testing
from src.scripts import DynamicInsertAtLayers

my_plugin = DynamicInsertAtLayers.DynamicInsertAtLayers()

# perform integrity checks
check_json_format(my_plugin.getSettingDataString)
check_name_matching(my_plugin)

# mock the setting entered by user
settings = json.loads(my_plugin.getSettingDataString())

my_plugin.settings['settings']['start_layer_number'] = 0
my_plugin.settings['settings']['stop_layer_number'] = -1
my_plugin.settings['settings']['increment_layer_number'] = 1
my_plugin.settings['settings']['pre_fg'] = 'this is fixed pre-gcode'
my_plugin.settings['settings']['post_fg'] = 'this is fixed post-gcode'
my_plugin.settings['settings']['dg_command'] = 'G4'
my_plugin.settings['settings']['dg_action'] = 'S'
my_plugin.settings['settings']['dg_const'] = 0
my_plugin.settings['settings']['dg_first'] = 1
my_plugin.settings['settings']['dg_second'] = 0
my_plugin.settings['settings']['dg_third'] = 0
my_plugin.settings['settings']['add_dg'] = True

pprint(my_plugin.settings)

# fake G-Code to be modified
data = [
    ';this is for pre-code layer\nsome pre-code\n\n',
    ';LAYER:0\n;some other comments\nsome code in layer 0\n',
    ';LAYER:1\n;some other comments\nsome code in layer 1\n',
    ';LAYER:2\n;some other comments\nsome code in layer 2\n',
    ';LAYER:3\n;some other comments\nsome code in layer 3\n',
    ';this is for post-code layer\nsome post-code\n\n',
    ';this is for end comments\n',
]

pprint(data)

# test the logic of the plugin
modified_data = my_plugin.execute(data)

print(modified_data)


