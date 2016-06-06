#!/usr/bin/python
# -*- coding: utf-8 -*-

""" This file is part of B{Domogik} project (U{http://www.domogik.org}).

License
=======

B{Domogik} is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

B{Domogik} is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with Domogik. If not, see U{http://www.gnu.org/licenses}.

Plugin purpose
==============

Body metrics

Implements
==========

- BodyManager

@author: Fritz SMG <fritz.smh@gmail.com>
@copyright: (C) 2007-2016 Domogik project
@license: GPL(v3)
@organization: Domogik
"""

from domogik.common.plugin import Plugin
from domogikmq.message import MQMessage


class BodyManager(Plugin):
    """
    """

    def __init__(self):
        """ Init plugin
        """
        Plugin.__init__(self, name='body')

        # check if the plugin is configured. If not, this will stop the plugin and log an error
        # if not self.check_configured():
        #    return

        # get the devices list
        self.devices = self.get_device_list(quit_if_no_device=True)
        # self.log.info(u"==> device:   %s" % format(self.devices))

        # get the sensors id per device:
        self.commands = self.get_commands(self.devices)
        self.sensors = self.get_sensors(self.devices)
        self.log.info(u"==> commands:   %s" % format(self.commands))    
        self.log.info(u"==> sensors:   %s" % format(self.sensors))    
        # INFO ==> sensors:   {66: {u'set_weight': 159}}  # {'device id': {'sensor name': 'sensor id'}}

        # for each device ...
        self.body_namelist = {}
        for a_device in self.devices:
            # global device parameters
            device_name = a_device["name"]                    # Ex.: "john"
            device_id = a_device["id"]                        # Ex.: "128"
            device_typeid = a_device["device_type_id"]        # Ex.: "body.body 
            self.log.info(u"==> Device '%s' (id:%s / %s), Sensor: '%s'" % (device_name, device_id, device_typeid, self.sensors[device_id]))
            # INFO ==> Device 'VDevice Binary 1' (id:112 / vdevice.info_binary), Sensor: '{u'get_info_binary': 216}'
            # INFO ==> Device 'VDevice Number 1' (id:113 / vdevice.info_number), Sensor: '{u'get_info_number': 217}'
            # INFO ==> Device 'VDevice String 1' (id:114 / vdevice.info_string), Sensor: '{u'get_info_string': 218}'
            self.body_namelist[device_id] = device_name

        self.ready()

    def get_related_sensor_id(self, device_id, command_id):
        """ return the appropriate sensor_id. For example, for the command set_weight, return the id for sensor weight
        """
        for cmd in self.commands[device_id]:
            if self.commands[device_id][cmd] == command_id:
                # get the sensor id
                if cmd == "set_weight":
                    return self.sensors[device_id]['weight']
                elif cmd == "set_fat":
                    return self.sensors[device_id]['fat']
                elif cmd == "set_muscle":
                    return self.sensors[device_id]['muscle']
                elif cmd == "set_bone":
                    return self.sensors[device_id]['bone']
                elif cmd == "set_water":
                    return self.sensors[device_id]['water']
        return None


    def on_mdp_request(self, msg):
        """ Called when a MQ req/rep message is received
        """
        Plugin.on_mdp_request(self, msg)
        #self.log.debug(u"==> Received 0MQ messages: %s" % format(msg))
        if msg.get_action() == "client.cmd":
            data = msg.get_data()
            self.log.debug(u"==> Received 0MQ messages data: %s" % format(data))
            # ==> Received 0MQ messages data: {u'command_id': 35, u'value': u'1', u'device_id': 112}
            # ==> Received 0MQ messages data: {u'command_id': 36, u'value': u'128', u'device_id': 113}
            # ==> Received 0MQ messages data: {u'command_id': 37, u'value': u'Bonjour', u'device_id': 114}

            sensor_id = self.get_related_sensor_id(data['device_id'], data['command_id'])
            self.log.debug(u"Storing data for sensor_id = {0} : '{1}'".format(sensor_id, data["value"]))
            status, reason = self.send_data(sensor_id, data["value"])

            self.log.info("Reply to command 0MQ")
            reply_msg = MQMessage()
            reply_msg.set_action('client.cmd.result')
            reply_msg.add_data('status', status)
            reply_msg.add_data('reason', reason)
            self.reply(reply_msg.get())


    def send_data(self, sensor_id, value):
        """ Send the sensors values over MQ
        """
        data = {sensor_id : value}
        try:
            self._pub.send_event('client.sensor', data)
            return True, None
        except:
            self.log.debug(u"Error while sending sensor MQ message for sensor values : {0}".format(traceback.format_exc()))
            return False, u"Error while sending sensor MQ message for sensor values : {0}".format(traceback.format_exc())


if __name__ == "__main__":
    BodyManager()

