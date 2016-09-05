from TemperatureMQTT import TemperatureMQTT

clientName = "gijupiter" # + str(random.randint(1, 100)) (Change this as same names will conflict)

#device setup
j = """
{
    "deviceInfo": {
        "status": "good",
        "color": "#4D90FE",
        "endPoints": {
            "temperatureHistory": {
                "values": {
                    "labels": [0],
                    "series": [[0]],
                    "update": ""
                },
                "max": 3600,
                "low": 10,
                "high": 180,
                "card-type": "crouton-chart-line",
                "title": "Temperature (C)"
            },
            "temperatureT0": {
                "values": {
                    "labels": [], 
                    "series": [0]
              },
              "total": 120,
              "centerSum": true,
              "units": "C",
              "card-type": "crouton-chart-donut",
              "title": "T0 temperature"
            },
            "temperatureT1": {
                "values": {
                    "labels": [], 
                    "series": [0]
              },
              "total": 120,
              "centerSum": true,
              "units": "C",
              "card-type": "crouton-chart-donut",
              "title": "T1 temperature"
            },
            "temperatureT2": {
                "values": {
                    "labels": [], 
                    "series": [0]
              },
              "total": 120,
              "centerSum": true,
              "units": "C",
              "card-type": "crouton-chart-donut",
              "title": "T2 temperature"
            },
            "temperatureT3": {
                "values": {
                    "labels": [], 
                    "series": [0]
              },
              "total": 120,
              "centerSum": true,
              "units": "C",
              "card-type": "crouton-chart-donut",
              "title": "T2 temperature"
            },                                    
            "updateRate": {
              "values": {
                "value": 1 
              },
              "min": 1, 
              "max": 60, 
              "units": "s", 
              "card-type": "crouton-simple-slider",
              "title": "Update Time" 
            }
        },
        "description": "Machine Temperature"
    }
}
"""

print "Client Name is: " + clientName









mqtt = TemperatureMQTT("Machine-1")
mqtt.createDeviceInfo(j)
mqtt.run("192.168.2.3", 8883, "./ca.crt")
