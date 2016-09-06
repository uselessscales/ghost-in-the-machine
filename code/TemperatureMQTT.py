import paho.mqtt.client as mqtt
import time
import json
import collections
from threading import Timer, Lock
from datetime import datetime
from grooveTemperature import grooveTemperature as gTemp
import random
import pyupm_grove as grove
from buzzer import buzz

class TemperatureMQTT(mqtt.Client):

    def on_connect(self, mqttc, obj, flags, rc):
        print("Connected with result code " + str(rc))

    def on_message(self, mqttc, obj, msg):
        if (msg.topic.split("/")[1] in "inbox outbox"):
            box = (msg.topic.split("/")[1])
            name = msg.topic.split("/")[2]
            address = msg.topic.split("/")[3]

            # Return device info on call to /inbox/name/deviceInfo:get
            if box == "inbox" and str(msg.payload) == "get" and address == "deviceInfo":
                self.publish("/outbox/"+self._client_id+"/deviceInfo", self.deviceInfo, 1)
            # set the new update rate
            if box == "inbox" and address == "updateRate" :
                self.startTimer(msg.payload)
                self.publishUpdateRate()           

            if box == "inbox" and address == "alarm" :
                if str(msg.payload) < 1:
                    buzz(1.0)
                else:
                    buzz(msg.payload)
            if box == "inbox" and address == "reset":
                #initial values
                self.publish("/outbox/"+client_id+"/updateRate", '{"value":'+ temperatureRate + '}',1)
                print "Reseting values...."
            elif (msg.topic.split("/")[0] == "$SYS"):
                pass
        else:
            pass

    def on_publish(self, mqttc, obj, mid):
        pass
    def on_subscribe(self, mqttc, obj, mid, granted_qos):
        print("Subscribed: "+str(mid)+" "+str(granted_qos))

    def on_log(self, mqttc, obj, level, string):
        pass
    def run(self, ip="localhost", port=1883, tls=None):
        self.lock = Lock()

        if tls != None:
            self.tls_set(tls)
        self.connect(ip, port, 60)
        
        self.publish("/outbox/"+self._client_id+"/deviceInfo", self.deviceInfo, 1) #for autoreconnect
        self.subscribe("$SYS/#", 1)
        self.subscribe("/inbox/"+self._client_id+"/deviceInfo", 1)
        self.subscribe("/inbox/"+self._client_id+"/alarm", 1)

        device = json.loads(self.deviceInfo)
        for key in device["deviceInfo"]["endPoints"]:
            self.subscribe("/inbox/"+self._client_id+"/"+str(key), 1)

        self.loop_start()
        self.startTimer()
        self.publishUpdateRate()

        while True:
            pass
        self.loop_stop()



    def stop(self,force=False):
        try:
            self.timer.cancel()
        except:
            pass
        self.loop_stop(force)



    def createDeviceInfo(self, deviceInfo):
        device = json.loads(deviceInfo)
        device["deviceInfo"]["name"] = self._client_id
        self.deviceInfo = json.dumps(device)
        self.updateRate = float(device["deviceInfo"]["endPoints"]["updateRate"]["values"]["value"])
        self.temperature = {}
        for endPoints in device["deviceInfo"]["endPoints"]:
            if "temperatureT" in endPoints:
                self.temperature[endPoints.split("temperatureT", 1)[1]] = collections.deque(maxlen=3600)
        print self.temperature.keys()
        self.groove = gTemp(self.temperature.keys())

    def startTimer(self, newRate=None):
        self.lock.acquire()
        if newRate != None:
            device = json.loads(self.deviceInfo)
            self.updateRate = float(newRate)
            device["deviceInfo"]["endPoints"]["updateRate"]["values"]["value"] = self.updateRate
            self.deviceInfo = json.dumps(device)
        try:
            self.timer.cancel()
        except:
            pass

        try:
            self.timer = Timer(1.0/self.updateRate, self.update)
        except:
            self.timer = Timer(1.0, self.update)

        self.lock.release()       
        self.timer.start()


    def publishUpdateRate(self):
         self.publish("/outbox/"+self._client_id+"/updateRate", self.updateRate,2)
    
    def update(self):
        for name , key in self.temperature.iteritems():
            tempTemp = self.groove.getTemperature(int(name))
            if tempTemp < 0:
                tempTemp = random.randint(0,50)
            self.publish("/outbox/"+self._client_id+"/temperatureT"+ name, tempTemp,1)            
        self.startTimer()
