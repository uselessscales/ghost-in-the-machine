import pyupm_grove as grove

class groveTemperature(object):
	"""docstring for ClassName"""
	def __init__(self, sensor_list):
		resetSensors(sensor_list)

	def resetSensors(self, sensor_list):
		self.sensors = {}
		for requested_sensors in sensor_list:
			self.sensors{requested_sensors} = grove.GroveTemp(requested_sensors)
	
	def getTemperature(self, sensor):
		return self.sensors.get(sensor)