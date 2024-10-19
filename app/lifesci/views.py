from django.shortcuts import render
from .forms import HumanForm, IntegerInputForm, PeerReviewForm, FigureOnlyForm
from .models import Human, Question, Answer, Resource, PreloadedUser, Collaboration, PeerReview
from django.http import HttpResponseRedirect, HttpResponse
from .utils import foundation
import datetime
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth import logout
from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required
from cryptography.fernet import Fernet
import io
import base64
import qrcode
import hashlib
import numpy as np
import random

# import SECRET_KEY from settings
from django.conf import settings


# import sites models
from django.contrib.sites.models import Site


from allauth.socialaccount.models import SocialAccount

def get_qr_code(request, question, human):
    data = get_collaboration_link(request, question, human)
    qr = qrcode.QRCode(version=1, error_correction=qrcode.constants.ERROR_CORRECT_H, box_size=10, border=4)
    qr.add_data(data)
    qr.make()

    img = qr.make_image()

    # Convert the image to a string in base64 format
    buffered = io.BytesIO()
    img.save(buffered, format="PNG")
    img_str = base64.b64encode(buffered.getvalue()).decode()

    return img_str

def key_from_string(input_string):
    # Create a SHA-256 hash from the input string
    hash = hashlib.sha256(input_string.encode()).digest()

    # Base64 encode the hash to get a Fernet key
    key = base64.urlsafe_b64encode(hash)

    return key

def decode_collaboration_code(collaboration_code):

    print("here's my code", collaboration_code)

    
    key = key_from_string(settings.SECRET_KEY)

    # Generate a key and instantiate a Fernet instance
    cipher_suite = Fernet(key)

    slug = cipher_suite.decrypt(collaboration_code)

    return slug


def get_collaboration_link(request, question, human):

    # hash the human id and question id and encrypt it
    # return the link
    key = key_from_string(settings.SECRET_KEY)

    # Generate a key and instantiate a Fernet instance
    cipher_suite = Fernet(key)

    # Encrypt a message
    
    text = f"{human.slug}".encode()

    cipher_text = cipher_suite.encrypt(text).decode()

    # get page url from request
    url = request.build_absolute_uri()
    
    # if last character of url is integer
    if url[-1].isdigit():
        url = url[:-1]
    # remove the question id from the url
    print("collaboration_url", url)
    
    try:
        return url +f"{question.id}" + "/collaborate" + f"/{cipher_text}"
    except:
        return None


# def github_callback(request):
#     # Handle the OAuth callback here...

#     # Then return a HTML page with some JavaScript code to close the popup window and refresh the original page
#     return HttpResponse("""
#         <html><body>
#         <script type="text/javascript">
#             window.opener.location.reload(true);  // refresh the original page
#             window.close();  // close the popup window
#         </script>
#         </body></html>
#     """)

def logout_view(request):
    # Log out the user
    logout(request)

    # Get the next URL from the 'next' parameter, or default to the homepage
    next_url = request.GET.get('next', '/lifesci')

    # Redirect to the next URL
    return redirect(next_url)

def get_leaderboard_question(context):
    # Get all answers for this question that are correct. Order by most recently submitted.
    question_answers = Answer.objects.filter(question=context["question"], correct=True).order_by('-answer_score')

    # Get the top 10 scores for problem.
    question_top_answers = question_answers[:10]

    question_leaderboard = []

    for i, x in enumerate(question_top_answers):
        if x.human.anonymous_user:
            human = "AnonUser"+str(x.human.id)
        else:
            human = x.human.slug
            
        
        question_leaderboard.append(
            {
                "rank": i+1,
                "human": human,
                "score": x.answer_score
            }
        )

    context["question_leaderboard"] = question_leaderboard

    return context

def get_leaderboard_overall(context):
    humans = Human.objects.all()
    score_dict = {}

    for human in humans:
        answers = Answer.objects.filter(human=human, correct=True)
        score = sum([x.answer_score for x in answers])
        if score > 0:
            if human.anonymous_user:
                score_dict["AnonUser"+str(human.id)] = score
            else:
                score_dict[human.slug] = score
    
    sorted_score_dict = sorted(score_dict.items(), key=lambda x: x[1], reverse=True)
    top_scores = sorted_score_dict[:10]

    overall_leaderboard = [
        {
            "rank": i+1,
            "human": x[0],
            "score": x[1]
        } for i, x in enumerate(top_scores)]
    
    context["overall_leaderboard"] = overall_leaderboard

    return context

def get_rank(human, question=None):

    humans = Human.objects.all()
    score_dict = {}

    if question:
        if len(Answer.objects.filter(human=human, correct=True, question=question)) == 0:
            return {"rank": "--", "score": "--", "mistakes": "--"}
        else:
            incorrect_answers = Answer.objects.filter(human=human, correct=False, question=question)
    else:
        if len(Answer.objects.filter(human=human, correct=True)) == 0:
            return {"rank": "--", "score": "--", "mistakes": "--"}
        else:
            incorrect_answers = Answer.objects.filter(human=human, correct=False)
 
    if question:
        answers = Answer.objects.filter(human=human, correct=True, question=question)
        peer_reviews = PeerReview.objects.filter(answer__human=human, answer__question=question).count()
        colaborations = Collaboration.objects.filter(human=human, question=question).count()
        print("Figure Pass", [x.figure_pass for x in answers])
        
    else:
        answers = Answer.objects.filter(human=human, correct=True)
        peer_reviews = PeerReview.objects.filter(answer__human=human).count()
        colaborations = Collaboration.objects.filter(human=human).count()


    input_score = sum([x.answer_score/2 for x in answers])
    figure_score = sum([x.answer_score/2 for x in answers if x.figure_pass])
    total_score = input_score + figure_score + colaborations + peer_reviews


    return {
        "input_score": input_score,
        "figure_score": figure_score,
        "peer_reviews": peer_reviews,
        "collaborations": colaborations,
        "total_score": total_score,
    }


def start(request):

    context = {}

    # Get logged in user
    try:
        user = request.user
    
    except AttributeError:
        user = None

    human_form = None

    if request.method == 'POST':
            human_form = HumanForm(request.POST, user=user)
            if human_form.is_valid():

                # Check if student_id is already in preloaded_user list

                human = human_form.save()
                context = {"human_form": None}
                # Redirect to /question
                return HttpResponseRedirect('/lifesci/question')
            else:
                print("form is not valid")
                context = {"human_form": human_form, "errors": human_form.errors}
                return render(request, 'lifesci/start.html', context)

    #if user is not anonymous user
    if user is not None and user.is_authenticated:
        try:
            human = Human.objects.get(user=user)
            context={"human": human}
 
        except:
            human = None
            human_form = HumanForm(initial={
                "user": user,
                "last_name": user.last_name, 
                "first_name": user.first_name
            })
            


    context["human_form"] = human_form
    
    
    return render(request, 'lifesci/start.html', context)

@login_required(login_url='/lifesci')
def question(request, question_id=None):

    

    context = {}
    social_account = SocialAccount.objects.filter(user=request.user).first()
    print(social_account, request.user)
    context["social_account"] = social_account

    
    try:
        human = Human.objects.get(user=request.user)
    except ObjectDoesNotExist:
        return HttpResponseRedirect('/lifesci')
    context["human"] = human
    answer_form = IntegerInputForm()
    context["answer_form"] = answer_form
    context["stats"] = get_rank(human)

    # Get all answers for this human that are correct. Order by most recently submitted.
    answers = Answer.objects.filter(human=human).order_by('-time_submitted')

    # If there are no correct answers, then this is the first question.
    correct_answers = Answer.objects.filter(human=human, correct=True).order_by('-time_submitted')
    if len(correct_answers) == 0:
        question = Question.objects.first()
    else:
        # Get the most recent answer.
        answer = correct_answers[0]

        # Get the next question.
        question = answer.question.next

    context["question"] = question
       
    if question_id:
        question = Question.objects.get(id=question_id)
        answers = Answer.objects.filter(human=human, question=question, correct=True).order_by('-time_submitted')
        resources = Resource.objects.filter(question=question)

        if len(answers) > 0:
            answer = answers[0]
            context["complete"] = True
            context["question"] = question
            context["answer"] = answer
            context = get_leaderboard_question(context)
            context = get_leaderboard_overall(context)
            context["stats_part"] = get_rank(human, question=context["question"])
            context["resources"] = resources
            qrcode = get_qr_code(request, question, human)
            collaborate_url = get_collaboration_link(request, question, human)
            context["collaboration_qr"] = qrcode
            context["collaboration_url"] = collaborate_url
            context["collaborations"] = Collaboration.objects.filter(human=human, question=question)
            
            if request.method == "POST":
                if "resubmit_figure" in request.FILES:
                    figure_only_form = FigureOnlyForm(request.POST, request.FILES)
                    if figure_only_form.is_valid():
                        answer = Answer.objects.get(id=answer.id)
                        answer.figure = figure_only_form.cleaned_data['resubmit_figure']
                        answer.peer_reviewed = False
                        answer.save()
                        return HttpResponseRedirect('/lifesci/question')
                    else:
                        print(figure_only_form.errors)
                        return render(request, 'lifesci/figure_only.html', {
                            "answer": answer,
                            "figure_only_form": figure_only_form
                        })

            if answer.peer_reviewed:
                try:
                    peer_review = PeerReview.objects.get(answer=answer)
                    context["peer_review"] = peer_review
                    if not answer.figure_pass:
                        figure_only_form = FigureOnlyForm()
                        context["figure_only_form"] = figure_only_form
                except:
                    pass
            return render(request, 'lifesci/question.html', context)
    

    if request.method == 'POST':
        print("submitting form")
        print(request.POST, request.FILES)

        # if IntegerInputform is submitted
        if "number" in request.POST:

            answer_form = IntegerInputForm(request.POST, request.FILES)
            if answer_form.is_valid():
                print("form valid")
                incorrect_answers = Answer.objects.filter(human=human, correct=False, question=question)
                # If datetime now - datetime of most recent answer is less than 3 minutes, then return error.
                if incorrect_answers and len(incorrect_answers) > 0:
                    if datetime.datetime.now(datetime.timezone.utc) - answers[0].time_submitted < datetime.timedelta(minutes=1):
                        context["message"] = f"Sorry, you must wait 1 minute before answering this question again."
                        return render(request, 'lifesci/question.html', context)


                answer = Answer()
                answer.human = human
                answer.question = question
                
                answer.submitted = answer_form.cleaned_data['number']
                answer.figure = answer_form.cleaned_data['figure']
                
                answer.save()

                # Get the function from the question.
                function_name = question.function_name
                function = getattr(foundation, function_name)

                # Run the function with the human as the argument.
                result = function(human, check=answer.submitted)

                # If the result is True, then the answer is correct.
                if result == True:
                    answer.correct = True

                    # build datetime from date and time
                    start = question.pub_date.replace(tzinfo=datetime.timezone.utc)

                    now = datetime.datetime.now(datetime.timezone.utc)

                    elapsed = now - start

                    seconds = elapsed.total_seconds()

                    half_life = 604800
                    decay_const = np.log(2)/half_life

                    if seconds < half_life:
                        answer_score = 100
                        answer.answer_score = answer_score
                        answer.save()
                    else:
                        answer.answer_score = 40 + 60*(np.exp(-decay_const*(seconds-half_life)))
                        answer.save()

                    context = get_leaderboard_question(context)
                    context = get_leaderboard_overall(context)
                    context["stats_part"] = get_rank(human, question=context["question"])
                    context["stats"] = get_rank(human)

                    context["success"] = True

                else:
                    answer.correct = False
                    answer.save()

                    context["message"] = f"Sorry, that is not the correct answer. Please wait 1 minute before trying again. "

                    # Look for answers with the same submitted value.
                    matching_answers = Answer.objects.filter(question=question, correct=True, submitted=answer.submitted)
                    if len(matching_answers) > 0:

                        context["message"] += f"Curiously, the human <strong>{matching_answers[0].human.slug}</strong> submitted the same answer and got it correct. What are the odds, eh?"

                render(request, 'lifesci/question.html', context)
            else:
                print("form not valid")
                # print errors
                print(answer_form.errors)

        # if PeerReviewForm is submitted
        if "feedback" in request.POST:
            print("Hello from peer review form")
            peer_review_form = PeerReviewForm(request.POST)
            answer = Answer.objects.get(id=request.POST["answer"])
            if peer_review_form.is_valid():
                peer_review = peer_review_form.save()
                peer_review.answer.peer_reviewed = True
                pass_peer = peer_review_form.cleaned_data['pass_peer']
                feedback = peer_review_form.cleaned_data['feedback']
                peer_review.answer.peer_feedback = feedback
                peer_review.answer.figure_pass = pass_peer
                peer_review.answer.save()
                return HttpResponseRedirect('/lifesci/question')
            else:
                print(peer_review_form.errors)
                return render(request, 'lifesci/peer_review.html', {
                    "answer": answer,
                    "peer_review_form": peer_review_form
                })
            
    try:
        # How many peer marks for this question?
        peer_reviews = PeerReview.objects.filter(human=human, answer__question=answer.question)
        if len(peer_reviews) == 0:
            answers = Answer.objects.exclude(human=human).filter(
                question=answer.question, 
                correct=True,
                peer_reviewed=False,
                figure_pass=False
            )
            if len(answers) > 0:
                answer = random.choice(answers)
                peer_review_form = PeerReviewForm(initial={
                    "human":human, 
                    "answer": answer})
                
                return render(request, "lifesci/peer_review.html", {
                    "answer": answer,
                    "peer_review_form": peer_review_form
                })
    except:
        pass

    context["question"] = question
    context["stats_part"] = get_rank(human, question=context["question"])
    context = get_leaderboard_question(context)
    context = get_leaderboard_overall(context)
    qrcode = get_qr_code(request, question, human)
    collaborate_url = get_collaboration_link(request, question, human)
    context["collaboration_qr"] = qrcode
    context["collaboration_url"] = collaborate_url
    context["collaborations"] = Collaboration.objects.filter(human=human, question=question)
                

    # If there is no next question, then this is the last question.
    if question is None:
        previous_question = Answer.objects.filter(human=human).order_by('-time_submitted')[0].question
        context["previous_question"] = previous_question
        # TODO: Create Summary Page
        return render(request, 'lifesci/finish.html', context)
    
    context["question"] = question
    context["resources"] = Resource.objects.filter(question=question).order_by('name')
    
    return render(request, 'lifesci/question.html', context)


def input(request, question_id):

    # if "example" at the end of path, then set example to True
    example = False
    if request.path.endswith("example"):
        example = True



    human = Human.objects.get(user=request.user)
    question = Question.objects.get(id=question_id)
    function_name = question.function_name

    # get function from function_name
    function = getattr(foundation, function_name)

    html = function(human,example=example)
    

    return HttpResponse(html, content_type='text/plain')

@login_required(login_url='/lifesci')
def collaborate(request, question_id, collaboration_code):

    try:
        human = Human.objects.get(user=request.user)
        question = Question.objects.get(id=question_id)
    except ObjectDoesNotExist:
        return HttpResponseRedirect('/lifesci')

    # convert collaboration code to bytes
    collaboration_code = collaboration_code.encode()
    print(collaboration_code)

    slug = decode_collaboration_code(collaboration_code).decode()

    print(slug, human.slug )


    if slug == human.slug:
        return HttpResponse(f"Woah, you can't collaborate with yourself. Ask the person you're collaborating with to scan the qr code, or give them the link.")
    else:
        collaborator = Human.objects.get(slug=slug)

    # Create collaboration records for both collaborator and collaboratee

    # Check collaboration doesn't exist already

    if len(Collaboration.objects.filter(human=human, question=question)) > 10:
        return HttpResponse(f"You've collaborated with 10 people already on this question. No more!")
        pass
    
    try:
        Collaboration.objects.get(human=human, collaborator=collaborator)
        return HttpResponse(f"It look's like you've already collaborated with this person on this question.")
    except ObjectDoesNotExist:
        pass
        
    
    Collaboration(
        human = human,
        collaborator = collaborator,
        question=question
    ).save()

    Collaboration(
        human=collaborator,
        collaborator=human,
        question=question).save()
    
    return HttpResponse(f"Awesome. You collaborated with {slug} on question {question_id}")
    

 

    

    
