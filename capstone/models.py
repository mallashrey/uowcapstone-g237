from django.db import models
from django.contrib.auth.models import AbstractUser

from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
import json

# Create your models here.

PRIORITY = (
    (1, 'Low'),
    (2, 'Normal'),
    (3, 'High'),
    (4, 'Very High'),
    (5, 'Urgent')
)

STATUS = (
    (0, 'Open'),
    (1, 'In Progress'),
    (2, 'Waiting Approval'),
    (3, 'Done')
)

ROLE = (
    ('SA', 'Software Analyst'),
    ('SD', 'Software Designer'),
    ('SP', 'Software Programmer'),
    ('ST', 'Software Tester'),
    ('SM', 'Software Maintainer')
)

class User(AbstractUser):
    img_profile = models.CharField(max_length=100, null=True, blank=True)
    address = models.TextField(null=True, blank=True)
    is_manager = models.BooleanField(default=False)
    dept = models.IntegerField(null=True, blank=True)

    def serialize(self):
        return {
            "id": self.id,
            "username": self.username,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "img_profile": self.img_profile,
            "dept": self.dept,
        }

    def __str__(self):
        return f"Id: {self.id}, User: {self.username}"
    
class Category(models.Model):
    name = models.CharField(max_length=30)
    slug = models.SlugField()

    def serialize(self):
        return {
            "id": self.id,
            "name": self.name,
            "slug": self.slug
        }

    def __str__(self):
        return f"Id: {self.id}, Name: {self.name}"
    
class CategoryRole(models.Model):
    role_name = models.CharField(max_length=50)

    def serialize(self):
        return {
            "id": self.id,
            "role_name": self.role_name
        }
    
    def __str__(self):
        return f"Id: {self.id}, Role Name: {self.role_name}"

class Questionnaire(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="user_id")
    opt_ans1 = models.IntegerField(default=0)
    opt_ans2 = models.IntegerField(default=0)
    opt_ans3 = models.IntegerField(default=0)
    opt_ans4 = models.IntegerField(default=0)
    txt_ans1 = models.TextField(blank=True, null=True)
    txt_ans2 = models.TextField(blank=True, null=True)
    create_date = models.DateTimeField(blank=True, null=True)

    def serialize(self):
        return {
            "id": self.id
        }
    
    def __str__(self):
        return f"Id: {self.id}"

class MBTIResult(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="user_mbti")
    value = models.DecimalField(max_digits=4, decimal_places=2)
    mbti_type = models.CharField(max_length=4, null=True)
    create_date = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return f"Id: {self.id}, Value: {self.value}, Type: {self.mbti_type}"
    
class Ticket(models.Model):
    ticket_title = models.CharField(max_length=80)
    description = models.TextField()
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name="ticket_category", null=True)
    priority = models.IntegerField(default=1, choices=PRIORITY)
    requester = models.ForeignKey(User, on_delete=models.CASCADE, related_name="requester")
    watcher = models.ManyToManyField(User, related_name="watcher", blank=True, null=True)
    assigned_to = models.ManyToManyField(User, related_name="assigned_to_user", blank=True, null=True)
    status = models.IntegerField(default=0)
    due_date = models.DateField(blank=True, null=True)
    is_finished = models.BooleanField(default=False)
    create_date = models.DateTimeField(blank=True, null=True)
    modify_date = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        watcher = ', '.join([str(watcher.id) for watcher in self.watcher.all()])
        return f"Id: {self.id}, Title: {self.ticket_title}, assigned_to: {self.assigned_to}, watcher: {[watcher]}"
    
    def ticket_title_slug(self):
        return self.ticket_title.replace(' ', '-')
    
    def serialize(self):
        return {
            "id": self.id,
            "ticket_title": self.ticket_title,
            "requester": self.requester.serialize(),
            "create_date": self.create_date,
            "modify_date": self.modify_date
        }
    
class Role(models.Model):
    # role_type = models.CharField(max_length=5, choices=ROLE, blank=True, null=True)
    role_type = models.ForeignKey(CategoryRole, on_delete=models.CASCADE, related_name="role_type", blank=True, null=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="user_role")
    is_best = models.BooleanField(default=False)
    create_date = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return f"Id: {self.id}, Role: {self.role_type}, User: {self.user}"

class Notification(models.Model):
    send_to = models.ForeignKey(User, on_delete=models.CASCADE, related_name="send_to", blank=True, null=True)
    ticket = models.ForeignKey(Ticket, on_delete=models.CASCADE, related_name="ticket_id", blank=True, null=True)
    notification = models.IntegerField(null=True)
    is_read = models.BooleanField(default=False)
    creator = models.ForeignKey(User, on_delete=models.CASCADE, related_name="creator", blank=True, null=True)
    create_date = models.DateTimeField(null=True)

    def __str__(self):
        return f"Id: {self.id}, requester: {self.creator}, desc: {self.notification}, receiver: {self.send_to.id}"
    
    def notif_ticket_title_slug(self):
        return self.ticket.ticket_title.replace(' ', '-')
    
    def serialize(self):
        return {
            "send_to": self.send_to.serialize(),
            "ticket": self.ticket.serialize(),
            "slug": self.ticket.ticket_title_slug(),
            "notification": self.notification,
            "is_read": self.is_read,
            "creator": self.creator.serialize(),
            "create_date": self.create_date
        }

    def save(self, *args, **kwargs):
        channel_layer = get_channel_layer()
        notification_objs = Notification.objects.filter(is_read=False).count()
        data = {'count': notification_objs, 'msg': self.notification, 'requester': self.creator.id, 'receiver': self.send_to.id}

        async_to_sync(channel_layer.group_send) (
            'test_consumer_group', {
                'type': 'send_notification',
                'value': json.dumps(data)
            }
        )

        super(Notification, self).save(*args, **kwargs)

    # def bulk_create(self, objs, **kwargs):
    #     channel_layer = get_channel_layer()
    #     notification_objs = Notification.objects.filter(is_read=False).count()
    #     data = {'count': notification_objs, 'msg': self.notification, 'user': self.user.id}
    #     async_to_sync(channel_layer.group_send) (
    #         'test_consumer_group', {
    #             'type': 'send_notification',
    #             'value': json.dumps(data)
    #         }
    #     )

    #     return super(Notification, self).bulk_create(objs, **kwargs)