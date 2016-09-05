import pyupm_grove as grove

class grooveTemperature(object):
	"""docstring for ClassName"""
	def __init__(self, sensor_list):
		self.resetSensors(sensor_list)

	def resetSensors(self, sensor_list):
		self.sensors = {}
		for requested_sensors in sensor_list:
			self.sensors[int(requested_sensors)] = grove.GroveTemp(int(requested_sensors))
	
	def getTemperature(self, sensor):
		return self.sensors.get(sensor).value()

		