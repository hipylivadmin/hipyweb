from django.contrib import admin

from .models import Hack, Character, Question, Answer

class HackAdmin(admin.ModelAdmin):
    list_display = ('name', 'start', 'finish')

class CharacterAdmin(admin.ModelAdmin):
    list_display = ('name',)

class AnswerAdmin(admin.ModelAdmin):
    list_display = ('character', 'question', 'hack', 'correct_answer', 'score')

class QuestionAdmin(admin.ModelAdmin):
    list_display = ('name',)

admin.site.register(Hack, HackAdmin)
admin.site.register(Character, CharacterAdmin)
admin.site.register(Question, QuestionAdmin)
admin.site.register(Answer, AnswerAdmin)