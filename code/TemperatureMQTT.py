import paho.mqtt.client as mqtt
import time
import json
import collections
from threading import Timer
from datetime import datetime
from grooveTemperature import grooveTemperature as gTemp

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
                self.publish("/outbox/"+self._client_id+"/deviceInfo", self.deviceInfo)
                print self.deviceInfo
            # set the new update rate
            if box == "inbox" and address == "updateRate" :
                temp = json.loads(msg.payload)
                print ("New Update Rate: " + str(temp["value"]))
                self.startTimer(temp["value"])
                self.publishUpdateRate()

            if box == "inbox" and address == "reset":
                #initial values
                self.publish("/outbox/"+client_id+"/updateRate", '{"value":'+ temperatureRate + '}')
                print "Reseting values...."
            elif (msg.topic.split("/")[0] == "$SYS"):
                print("Sys message: " + msg.payload)

        else:
            pass

    def on_publish(self, mqttc, obj, mid):
        pass
    def on_subscribe(self, mqttc, obj, mid, granted_qos):
        print("Subscribed: "+str(mid)+" "+str(granted_qos))

    def on_log(self, mqttc, obj, level, string):
        print(string)

    def run(self, ip="localhost", port=1883, tls=None):
        if tls != None:
            print
            self.tls_set(tls)
        self.connect(ip, port, 60)
        
        self.publish("/outbox/"+self._client_id+"/deviceInfo", self.deviceInfo) #for autoreconnect
        self.subscribe("$SYS/#", 0)
        self.subscribe("/inbox/"+self._client_id+"/deviceInfo")

        device = json.loads(self.deviceInfo)
        for key in device["deviceInfo"]["endPoints"]:
            #print key
            self.subscribe("/inbox/"+self._client_id+"/"+str(key))

        self.loop_start()
        self.timer = Timer(self.updateRate, self.update)
        self.timer.start()
        print ("started timer with: "+str(self.updateRate))
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
        self.updateRate = int(device["deviceInfo"]["endPoints"]["updateRate"]["values"]["value"])
        self.temperature = {}
        for endPoints in device["deviceInfo"]["endPoints"]:
            if "temperatureT" in endPoints:
                self.temperature[endPoints.split("temperatureT", 1)[1]] = collections.deque(maxlen=3600)
        print self.temperature.keys()
        self.groove = gTemp(self.temperature.keys())

    def startTimer(self, newRate=None):
        if newRate != None:
            device = json.loads(self.deviceInfo)
            self.updateRate = int(newRate)
            device["deviceInfo"]["endPoints"]["updateRate"]["values"]["value"] = self.updateRate
            self.deviceInfo = json.dumps(device)
        try:
            self.timer.cancel()
        except:
            pass
        self.timer = Timer(self.updateRate, self.update)
        self.timer.start()

    def publishUpdateRate(self):
         self.publish("/outbox/"+self._client_id+"/updateRate", '{"value":'+ str(self.updateRate) +'}')
    
    def update(self):
        for name , key in self.temperature.iteritems():
            self.publish("/outbox/"+self._client_id+"/temperatureT"+ name, '{"series":['+str(self.groove.getTemperature(int(name)))+']}')
            self.temperature[name].append( (str(datetime.now().strftime('%S')), self.groove.getTemperature(int(name)) ) )
            if name == "0":
                unzipped = zip(*self.temperature[name])
                self.publish("/outbox/"+self._client_id+"/temperatureHistory", '{"update": {"labels":[' + str(', '.join(map(str,unzipped[0]))) + '],"series":[[' + str(', '.join(map(str,unzipped[1]))) + ']]}}')
                print("updated history")
        self.timer = Timer(self.updateRate, self.update)
        self.timer.start()


