from django.shortcuts import render
from .forms import StartForm, InputForm
from django.http import HttpResponseRedirect, HttpResponse
from .models import Character, Hack, Question, Answer
from django.utils.timezone import now
from django.core.exceptions import ObjectDoesNotExist
from .utils import jurassichack
import math
from collections import OrderedDict
import itertools
from django.contrib.auth.decorators import login_required

def calculate_score(answers):

    total_score = 0
    for answer in answers:

        answer.completed_at = now()
        answer.save()

        time_to_complete = (answer.completed_at - answer.started_at).total_seconds()
        score = 900 * math.exp(-time_to_complete/900) + 100
        score = int(score)

        total_score += score

    return total_score

def check_for_collaborators(hack, value):
    # Fetch all answers for the given hack and question where completed_at is None
    answers = [x for x in Answer.objects.filter(hack=hack, completed_at=None)]

    print(answers)
    
    # Get the total number of answers with no completed_at
    num_answers = len(answers)
    print("num_answers:", num_answers)

    r = 5
    if r > num_answers:
        r = num_answers

    # Start checking from r = num_answers and decrease r until 1
    for r in range(r, 0, -1):
        print("r=", r)
        # Iterate over all combinations of r answers
        for combo in itertools.combinations(answers, r):
            print("combo:", combo)
            # Calculate the sum of the scores in the current combination
            score_sum = sum(answer.correct_answer for answer in combo)

            print("score_sum:", score_sum)
            
            # If the sum matches the value, return the combination of answers
            if score_sum == value:
                return combo
    
    # If no combination is found, return None
    return None

def get_rankings(hack):
    answers = Answer.objects.filter(hack=hack)
    characters = set(x.character for x in answers)

    rankings_table = {}

    for character in characters:
        rankings_table[character.name] = sum([x.score for x in answers.filter(character=character)])

    return OrderedDict(sorted(rankings_table.items(), reverse=True))

def get_current_hack():
    current_time = now()
    hack = Hack.objects.filter(start__lt = current_time, finish__gt = current_time).first()
    return hack

    
def index(request):

    form = StartForm()

    context = {}

    if request.method == "POST":
        start_form = StartForm(request.POST)
        if start_form.is_valid():
            # Capture the character_name from the form
            character_name = start_form.cleaned_data["character_name"]

            try:
                character = Character.objects.get(name=character_name.lower())
            except ObjectDoesNotExist:
                start_form.add_error(None, "Character does not exist.")
                context["form"] = start_form
                return render(request, "jurassichack/index.html", context)

            hack = get_current_hack()

            if hack is None:
                # Add a form error if no active Hack is found
                start_form.add_error(None, "No Hack is available at the moment.")
                context["form"] = start_form
                return render(request, "jurassichack/index.html", context)
            
            try:
                question = Question.objects.get(name="question_1")
            except ObjectDoesNotExist:
                start_form.add_error(None, "Error. First question is missing!")
                context["form"] = start_form
                return render(request, "jurassichack/index.html", context)
            
            # Try and get existing answer
            try:
                answer = Answer.objects.get(character=character, hack=hack, question=question)
                return HttpResponseRedirect(f'{character.name}/')
            except ObjectDoesNotExist:
            
                # generate_correct_answer
                function = getattr(jurassichack, question.function_name)


                correct_answer = function(character, get_answer=True)

                answer = Answer(
                    character = character,
                    hack = hack,
                    question = question,
                    correct_answer = correct_answer
                )
                answer.save()

                return HttpResponseRedirect(f'{character.name}/')

    context["form"] = form

    return render(request, "jurassichack/index.html", context)


def character(request, character_name):

    hack = get_current_hack()

    try:
        character = Character.objects.get(name=character_name)

        answers = Answer.objects.filter(hack=hack, character=character)

        current_score = sum([x.score for x in answers])
        
        rankings = get_rankings(hack)

        current_rank = list(rankings.keys()).index(character_name) + 1

        answer = answers.last()

        context = {
            "character": character, 
            "answer": answer, 
            "current_score": current_score,
            "current_rank": current_rank
            }

        return render(request, "jurassichack/character.html", context)
        
    except (ObjectDoesNotExist, ValueError):
        start_form = StartForm()
        context = {"form": start_form}
        return render(request, "jurassichack/index.html", context)
    

    

def input(request, answer_id):

    answer = Answer.objects.get(id=answer_id)
    function_name = answer.question.function_name

    # get function from function_name
    function = getattr(jurassichack, function_name)

    html = function(answer.character)
    

    return HttpResponse(html, content_type='text/plain')

def console(request):

    context = {}

    hack = get_current_hack()

    rankings_table = get_rankings(hack)
    context["rankings"] = rankings_table

    if request.method == "POST":
        input_form = InputForm(request.POST)
        if input_form.is_valid():
            value = input_form.cleaned_data["input"]
            #try:
            results = check_for_collaborators(hack, value)
            if results:
                
                score = calculate_score(results)

                user_list = ""

                # update scores
                for answer in results:
                    answer.score = score
                    answer.save()
                    user_list += f"<li>{answer.character.name}</li>"

                
                for answer in results:

                    message = "<strong>Well done:</strong><ul>{0}</ul><p>You've scored <strong>{1}</strong> points!".format(user_list, score)
                    context["message"] = message
                

                    # generate_correct_answer
                    function = getattr(jurassichack, answer.question.next_question.function_name)


                    correct_answer = function(answer.character, get_answer=True)

                    new_answer = Answer(
                            character = answer.character,
                            hack = answer.hack,
                            question = answer.question.next_question,
                            correct_answer = correct_answer,
                            score = 0
                        )
                    
                    new_answer.save()
            


            rankings_table = get_rankings(hack)
            context["form"] = InputForm()
            context["rankings"] = rankings_table
            return render(request, "jurassichack/console.html", context)
            # except:
            #     #input_form.add_error(None, "Ah, ah, ah! You didn't say the magic word.")
            #     context["error"] = "<iframe src='https://giphy.com/embed/3ohzdQ1IynzclJldUQ' width='300' height='auto' style='' frameBorder='0' class='giphy-embed' allowFullScreen></iframe><p>"
            #     context["form"] = input_form
            #     return render(request, "jurassichack/console.html", context)

    rankings_table = get_rankings(hack)
    context["form"] = InputForm()
    context["rankings"] = rankings_table

    return render(request, "jurassichack/console.html", context)

@login_required
def reset(request):

    hack = get_current_hack()
    answers = Answer.objects.filter(hack=hack)
    answers.delete()

    return HttpResponseRedirect('/jurassichack')