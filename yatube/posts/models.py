from core.models import CreatedModel

from django.db import models
from django.contrib.auth import get_user_model


User = get_user_model()


class Group(models.Model):
    """Model - group."""
    title = models.CharField(
        verbose_name='Group',
        help_text='Choose group',
        max_length=200
    )
    slug = models.SlugField(allow_unicode=True, unique=True)
    description = models.TextField()

    class Meta:
        verbose_name = 'Group'
        verbose_name_plural = 'Groups'

    def __str__(self) -> str:
        return self.title

    def __repr__(self) -> str:
        return f'<Group {self.title}>'


class Post(CreatedModel):
    """Model - post."""
    text = models.TextField(
        'Text',
        help_text='Write here'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='posts',
        verbose_name='Author',
    )
    group = models.ForeignKey(
        Group,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name='posts',
        verbose_name='Group',
        help_text='Choose group',
    )
    image = models.ImageField(
        'Image',
        upload_to='posts/',
        blank=True,
    )

    class Meta:
        ordering = ('-pub_date',)
        verbose_name = 'Post'
        verbose_name_plural = 'Posts'

    def __str__(self) -> str:
        return self.text[:15]


class Comment(models.Model):
    """Model - comment."""
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='Comments',
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='Comment\'s author',
    )
    text = models.TextField(
        'Text',
        help_text='Write your comment here'
    )
    created = models.DateTimeField(
        'Date',
        auto_now_add=True
    )

    class Meta:
        ordering = ('-created',)
        verbose_name = 'Comment'
        verbose_name_plural = 'Comments'

    def __str__(self) -> str:
        return self.text[:30]


class Follow(models.Model):
    """Model - follow."""
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='following',
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='follower',
    )

    class Meta:
        constraints = [models.UniqueConstraint(
            fields=['author', 'user'], name='unique_follower')
        ]
        verbose_name = 'Follow'
        verbose_name_plural = 'Follows'

    def __str__(self) -> str:
        return f'{self.user} follows {self.author}'
