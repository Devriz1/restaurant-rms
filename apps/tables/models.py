from django.db import models


class DiningArea(models.Model):

    name = models.CharField(max_length=100)

    description = models.TextField(blank=True)

    display_order = models.PositiveIntegerField(default=0)

    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)

    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["display_order", "name"]

    def __str__(self):
        return self.name


class RestaurantTable(models.Model):

    STATUS_CHOICES = [
        ("available", "Available"),
        ("reserved", "Reserved"),
        ("cleaning", "Cleaning"),
        ("out_of_service", "Out of Service"),
    ]

    area = models.ForeignKey(
        DiningArea,
        on_delete=models.CASCADE,
        related_name="tables"
    )
    table_number = models.CharField(max_length=20)

    display_name = models.CharField(
         max_length=100,
     blank=True
)

    capacity = models.PositiveSmallIntegerField(default=2)

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="available"
    )

    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)

    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["area", "table_number"]
        unique_together = ["area", "table_number"]
    
    def __str__(self):
        return self.display_name or self.table_number
    
    @property
    def is_occupied(self):
        return self.sessions.filter(status="open").exists()


    @property
    def current_status(self):

     if self.status != "available":
        return self.status

     if self.is_occupied:
        return "occupied"

     return "available"