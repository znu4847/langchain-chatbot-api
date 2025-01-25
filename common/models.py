from django.db import models


# Create your models here.
class CommonModel(models.Model):
    """Common Model Definition"""

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True

    def created_str(self):
        return self.created_at.strftime("%Y-%m-%d %H:%M:%S")
