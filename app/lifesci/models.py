from django.db import models
from front.models import Event

class PreloadedUser(models.Model):
    
    user_id = models.BigIntegerField()
    last_name = models.CharField(max_length=100, null=True, blank=True)
    first_name = models.CharField(max_length=100, null=True, blank=True)
    email = models.EmailField(null=True, blank=True)

    def __str__(self):
        return f"{self.user_id}"



class Human(models.Model):
    user = models.OneToOneField('auth.User', on_delete=models.CASCADE, null=True, blank=True, related_name='life_sci_user')
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    slug = models.SlugField(max_length=100, unique=True)
    student_id = models.IntegerField(null=True, blank=True)
    anonymous_user = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"
    
class Question(models.Model):
    title = models.CharField(max_length=200)
    text = models.TextField()
    pub_date = models.DateTimeField('date published')
    previous = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True)
    next = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='next_question')
    question_success = models.TextField()
    image = models.FileField(upload_to='questions/', null=True, blank=True)
    function_name = models.CharField(max_length=200, null=True, blank=True)
    reddit = models.URLField(null=True, blank=True)
    resources = models.URLField(null=True, blank=True)
    puzzle_input = models.BooleanField(default=True)
    example_answer = models.BigIntegerField(null=True, blank=True)
    figure_example = models.FileField(upload_to='questions/', null=True, blank=True)
    figure_rubric = models.TextField(null=True, blank=True)
    
    def __str__(self):
        return f"{self.title}"
    
class Answer(models.Model):
    human = models.ForeignKey(Human, on_delete=models.CASCADE)
    event = models.ForeignKey(Event, on_delete=models.CASCADE, null=True, blank=True, related_name='life_sci_event')
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    correct = models.BooleanField(default=False)
    time_submitted = models.DateTimeField(auto_now_add=True)
    answer_score = models.IntegerField(default=0)
    figure_score = models.IntegerField(default=0)
    submitted = models.BigIntegerField(default=0)
    figure = models.FileField(upload_to='answers/', null=True, blank=True)
    figure_pass = models.BooleanField(default=False)
    peer_reviewed = models.BooleanField(default=False)
    peer_feedback = models.TextField(null=True, blank=True)

    def __str__(self):
        return f"{self.human} - {self.question} - {self.correct}"
    
class Resource(models.Model):
    name = models.CharField(max_length=200)
    url = models.URLField()
    question = models.ForeignKey(Question, on_delete=models.CASCADE, null=True, blank=True)
    
    def __str__(self):
        return f"{self.name}"
    
class Collaboration(models.Model):
    human = models.ForeignKey(Human, on_delete=models.CASCADE, related_name="human_colab")
    collaborator = models.ForeignKey(Human, on_delete=models.CASCADE, related_name="human_collaborator")
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name="collaboration_question", null=True, blank=True)
    score = models.IntegerField(default=1)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.human.last_name}"
    
class PeerReview(models.Model):
    human = models.ForeignKey(Human, on_delete=models.CASCADE, related_name="reviewer")
    answer = models.ForeignKey(Answer, on_delete=models.CASCADE, related_name="reviewed_answer")
    pass_peer = models.BooleanField(default=False)
    timestamp = models.DateTimeField(auto_now_add=True)
    feedback = models.TextField(null=True, blank=True)

    # Feedback cannot be blank if pass_peer is False
    def clean(self):
        if not self.pass_peer and not self.feedback:
            raise ValidationError('Feedback cannot be blank if pass_peer is False')

    def __str__(self):
        return f"{self.human.last_name}"




    