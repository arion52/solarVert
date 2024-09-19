from django.db import models

class PowerData(models.Model):
    sensor_id = models.CharField(max_length=100)
    date = models.DateField()
    input_power = models.FloatField()
    usage_power = models.FloatField()

class PowerUsage(models.Model):
    dt = models.DateTimeField()
    global_active_power = models.FloatField()
    global_reactive_power = models.FloatField()
    voltage = models.FloatField()
    global_intensity = models.FloatField()
    sub_metering_1 = models.FloatField()
    sub_metering_2 = models.FloatField()
    sub_metering_3 = models.FloatField()

    def __str__(self):
        return f"{self.dt} - Active Power: {self.global_active_power}"