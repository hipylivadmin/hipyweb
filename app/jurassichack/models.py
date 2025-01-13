from django.db import models
from django.core.exceptions import ValidationError

class Hack(models.Model):
    name = models.CharField(max_length=128, unique=True)
    start = models.DateTimeField()
    finish = models.DateTimeField()

    def __str__(self):
        return self.name
    
    def clean(self):
        # Check for overlapping records
        overlapping_hacks = Hack.objects.filter(
            finish__gt=self.start, # Existing finish is after new start
            start__lt=self.finish # Existing start is before new finish
        )

        if self.pk: # Exclude the current instance from the query if updating
            overlapping_hacks = overlapping_hacks.exclude(pk=self.pk)

        if overlapping_hacks.exists():
            raise ValidationError("Another hack overlaps with the specified time range.")
        
    def save(self, *args, **kwargs):
        # Call clean to validate before saving
        self.clean()
        super().save(*args, **kwargs)
    
class Character(models.Model):
    name = models.CharField(max_length=128, unique=True)

    def __str__(self):
        return self.name
    
class Question(models.Model):
    name = models.CharField(max_length=128, unique=True)
    title = models.CharField(max_length=128, blank=True, null=True)
    text = models.TextField(null=True, blank=True)
    next_question = models.ForeignKey('self', on_delete=models.CASCADE, related_name="next", blank=True, null=True)
    function_name = models.CharField(max_length=128, null=True, blank=True)

    def __str__(self):
        return self.name

class Answer(models.Model):
    character = models.ForeignKey(Character, on_delete=models.CASCADE)
    hack = models.ForeignKey(Hack, on_delete=models.CASCADE)
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name="question", blank=True, null=True)
    correct_answer = models.BigIntegerField(blank=True, null=True)
    score = models.IntegerField(default = 0)
    started_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return self.character.name


    
