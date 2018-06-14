from django.db import models

class BaseModel(models.Model):
    """
    A generic base model with very common attributes.
    Usually inherited by every other models of the system.
    """

    created_date = models.DateTimeField(auto_now_add=True)
    modified_date = models.DateTimeField(auto_now=True)
    deleted = models.BooleanField(default=False)

    class Meta:
        abstract = True
