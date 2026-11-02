from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.views import generic
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages
from .models import Course, Lesson, Enrollment, Question, Choice, Submission


# Course list view
class CourseListView(generic.ListView):
    template_name = 'onlinecourse/course_list.html'
    context_object_name = 'course_list'

    def get_queryset(self):
        return Course.objects.order_by('-total_enrollment')[:10]


# Course details view
class CourseDetailsView(generic.DetailView):
    model = Course
    template_name = 'onlinecourse/course_details_bootstrap.html'


def enroll(request, course_id):
    if request.method == 'POST':
        course = get_object_or_404(Course, pk=course_id)
        # Create an enrollment if not already enrolled
        user = request.user
        if user.is_authenticated:
            enrollment, created = Enrollment.objects.get_or_create(user=user, course=course)
            if created:
                course.total_enrollment += 1
                course.save()
        return redirect('onlinecourse:course_details', pk=course.id)


# <HINT> Create a submit view to handle exam submission
def submit(request, course_id):
    course = get_object_or_404(Course, pk=course_id)
    user = request.user
    if not user.is_authenticated:
        return redirect('onlinecourse:login')

    enrollment, _ = Enrollment.objects.get_or_create(user=user, course=course)
    submission = Submission.objects.create(enrollment=enrollment)

    # Collect selected choice IDs from POST request
    selected_choice_ids = []
    for key in request.POST:
        if key.startswith('choice_'):
            choice_id = request.POST.get(key)
            selected_choice_ids.append(int(choice_id))

    # Also handle standard choice getlist
    if not selected_choice_ids:
        choice_list = request.POST.getlist('choice')
        for cid in choice_list:
            selected_choice_ids.append(int(cid))

    for choice_id in selected_choice_ids:
        choice = Choice.objects.get(id=choice_id)
        submission.choices.add(choice)

    submission.save()
    return redirect('onlinecourse:show_exam_result', course_id=course.id, submission_id=submission.id)


# <HINT> Create a show_exam_result view to show result of exam submission
def show_exam_result(request, course_id, submission_id):
    course = get_object_or_404(Course, pk=course_id)
    submission = get_object_or_404(Submission, pk=submission_id)

    selected_ids = list(submission.choices.values_list('id', flat=True))

    total_score = 0
    max_score = 0

    # Collect questions from lessons or directly from course
    questions = []
    for lesson in course.lesson_set.all():
        for question in lesson.question_set.all():
            if question not in questions:
                questions.append(question)

    if hasattr(course, 'question_set'):
        for question in course.question_set.all():
            if question not in questions:
                questions.append(question)

    for question in questions:
        max_score += question.grade
        if question.is_get_score(selected_ids):
            total_score += question.grade

    grade = int((total_score / max_score) * 100) if max_score > 0 else 100

    context = {
        'course': course,
        'submission': submission,
        'grade': grade,
        'selected_ids': selected_ids,
        'questions': questions
    }
    return render(request, 'onlinecourse/exam_result_bootstrap.html', context)


# Authentication views
def registration_request(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('onlinecourse:popular_course_list')
    else:
        form = UserCreationForm()
    return render(request, 'onlinecourse/registration.html', {'form': form})


def login_request(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('onlinecourse:popular_course_list')
        else:
            messages.error(request, 'Invalid username or password.')
    return render(request, 'onlinecourse/login.html')


def logout_request(request):
    logout(request)
    return redirect('onlinecourse:popular_course_list')
