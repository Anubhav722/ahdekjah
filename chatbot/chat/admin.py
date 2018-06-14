from django.contrib import admin

from .models import (Answer, Tree, TreeState,
                     Question, Session, Transition,
                     QuestionAnswerPair, StructuredAnswer, SkypeToken)
# Register your models here.

admin.site.register(Answer)
admin.site.register(Tree)
admin.site.register(Question)
admin.site.register(TreeState)
admin.site.register(Session)
admin.site.register(Transition)
admin.site.register(QuestionAnswerPair)
admin.site.register(StructuredAnswer)
admin.site.register(SkypeToken)
