# Copyright (c) 2020 Ultimaker B.V.
# Cura is released under the terms of the LGPLv3 or higher.
# Created by Anthony Rongtao Ma

# Version - V1.0
# Main Feature: To allow user to insert dynamic G-Code as a function of layer numbers (up to the third order)
# Email to report issues: anthonyma24.development@gmail.com
# Github repo: https://github.com/anthonyma24/cura_plugin.git

from ..Script import Script


class DynamicInsertAtLayers(Script):
    def __init__(self):
        super().__init__()

    def getSettingDataString(self):
        return """{
            "name": "Insert G-code as a function of layers",
            "key": "DynamicInsertAtLayers",
            "metadata": {},
            "version": 2,
            "settings":
            {
                "start_layer_number":
                {
                    "label": "Layer to start insert",
                    "description": "Specify at which layer to start inserting the G-Code",
                    "type": "int",
                    "default_value": 0
                },
                "stop_layer_number":
                {
                    "label": "Layer to stop insert",
                    "description": "Specify at which layer to stop inserting the G-Code; If enter '-1' (default), the end layer will be set to the last layer",
                    "type": "int",
                    "default_value": -1
                },
                "increment_layer_number":
                {
                    "label": "Increment for insert",
                    "description": "Specify the increment layer steps for inserting the G-Code",
                    "type": "int",
                    "default_value": 1
                },
                "add_dg": {
                    "label": "Add G-Code as a function of layers",
                    "description": "Check to enable inserting dynamic G-Code as a function of layer >> f(l) = const + first_coef*l + second_coef*l^2 + third_coef*l^3 (e.g. Insert G4 S{every_layer_increment * 3} will be 'Command=G4' 'Action=S' 'First order coefficient=3' with all other coefficients set to zero)",
                    "type": "bool",
                    "default_value": false
                },
                "dg_command": {
                    "label": "Command",
                    "description": "Specify the command of dynamic G-Code (e.g. M0, G4, etc.)",
                    "type": "str",
                    "default_value": "M0",
                    "enabled": "add_dg"
                },
                "dg_action": {
                    "label": "Action",
                    "description": "Specify the action of dynamic G-Code (e.g. S, F, etc.)",
                    "type": "str",
                    "default_value": "S",
                    "enabled": "add_dg"
                },
                "dg_const": {
                    "label": "Constant coefficient",
                    "description": "The constant coefficient of the dynamic G-Code function",
                    "type": "float",
                    "default_value": 0.0,
                    "enabled": "add_dg"
                },
                "dg_first": {
                    "label": "First order coefficient",
                    "description": "The first order coefficient of the dynamic G-Code function",
                    "type": "float",
                    "default_value": 0.0,
                    "enabled": "add_dg"
                },
                "dg_second": {
                    "label": "Second order coefficient",
                    "description": "The second order coefficient of the dynamic G-Code function",
                    "type": "float",
                    "default_value": 0.0,
                    "enabled": "add_dg"
                },
                "dg_third": {
                    "label": "Third order coefficient",
                    "description": "The third order coefficient of the dynamic G-Code function",
                    "type": "float",
                    "default_value": 0.0,
                    "enabled": "add_dg"
                },
                "pre_fg":
                {
                    "label": "Add fixed pre-G-Code",
                    "description": "Add fixed G-Code that will be repeatedly inserted before each dynamic G-Code",
                    "type": "str",
                    "default_value": ""
                },
                "post_fg":
                {
                    "label": "Add fixed post-G-Code",
                    "description": "Add fixed G-Code that will be repeatedly inserted after each dynamic G-Code",
                    "type": "str",
                    "default_value": ""
                }
            }
        }"""

    def _dynamic_gcode_generator(self, pre_code, post_code, layer_number, command, action, const, first, second, third):

        value = round(const + first * layer_number + second * layer_number ** 2 + third * layer_number ** 3, 2)

        if action == 'S':
            value = int(value)

        insert_gcode = '\n;this is inserted dynamic gcode\n' \
                       + command + ' ' \
                       + action + str(value) + '\n\n'

        if pre_code:
            insert_gcode = '\n;this is inserted fixed pre-gcode\n' \
                           + pre_code + '\n' \
                           + insert_gcode
        if post_code:
            insert_gcode = insert_gcode \
                           + ';this is inserted fixed post-gcode\n' \
                           + post_code + '\n\n'

        return insert_gcode

    def execute(self, data):

        start_layer = self.getSettingValueByKey('start_layer_number')
        stop_layer = self.getSettingValueByKey('stop_layer_number')
        increment = self.getSettingValueByKey('increment_layer_number')

        pre_gcode = self.getSettingValueByKey('pre_fg')
        post_gcode = self.getSettingValueByKey('post_fg')
        command = self.getSettingValueByKey('dg_command')
        action = self.getSettingValueByKey('dg_action')
        const = self.getSettingValueByKey('dg_const')
        first_coe = self.getSettingValueByKey('dg_first')
        second_coe = self.getSettingValueByKey('dg_second')
        third_coe = self.getSettingValueByKey('dg_third')

        total_layers = len([layer for layer in data if ";LAYER:" in layer])

        if stop_layer == -1 or stop_layer == total_layers - 1:
            stop_layer = total_layers
        elif stop_layer > total_layers - 1:
            raise Exception('Error: The input stop layer is larger than maximum layer numbers!')

        index = 0

        for layer_number in range(start_layer, stop_layer, increment):
            dynamic_gcode = self._dynamic_gcode_generator(pre_gcode, post_gcode, layer_number, command, action, const,
                                                          first_coe, second_coe, third_coe)
            found = False
            if data:
                while not found and index < len(data):
                    lines = data[index].split('\n')
                    for line in lines:
                        if ';LAYER:' + str(layer_number) in line:
                            found = True
                            data[index] = dynamic_gcode + data[index]
                            break
                    index += 1
                    if found:
                        break

        return data
