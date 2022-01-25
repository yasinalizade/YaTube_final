from django.db import models


class CreatedModel(models.Model):
    """Abstract model. Add publication date."""
    pub_date = models.DateTimeField(
        'Дата создания',
        auto_now_add=True
    )

    class Meta:
        abstract = True
