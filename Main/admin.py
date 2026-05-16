from django.contrib import admin
from .models import *

admin.site.register(Chat)
admin.site.register(Message)
admin.site.register(MessageAttachment)
admin.site.register(Poll)
admin.site.register(PollOption)
admin.site.register(PollVote)