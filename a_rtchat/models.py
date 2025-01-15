import shortuuid

from django.db import models
from django.contrib.auth.models import User

class ChatGroup(models.Model):
    group_name = models.CharField(max_length=128, unique=True, blank=True)
    groupchat_name = models.CharField(max_length=128, null=True, blank=True)
    admin = models.ForeignKey(User, related_name="groupchats", blank=True, null=True, on_delete=models.SET_NULL)
    users_online = models.ManyToManyField(User, related_name='online_in_groups', blank=True)
    members = models.ManyToManyField(User, related_name="chat_groups", blank=True)
    is_private = models.BooleanField(default=False)
    
    def __str__(self):
        return self.group_name
    
    def save(self, *args, **kwargs):
        if not self.group_name:
            self.group_name = shortuuid.uuid()
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = 'Chat group'
        verbose_name_plural = 'Chat groups'
    
    
class GroupMessage(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    group = models.ForeignKey(
        ChatGroup, 
        related_name='chat_messagse', 
        on_delete=models.CASCADE
    )
    body = models.CharField(max_length=300)
    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    
    def __str__(self):
        return f"{self.author.username} : {self.body}"
    
    class Meta:
        ordering = ['-created_at']
        
        verbose_name = 'Group message'
        verbose_name_plural = 'Group messages'
    