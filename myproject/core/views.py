from django.shortcuts import render

# Create your views here.
def home(request):
    return render(request, "base.html", {
        "title": "Головна сторінка",
        "text": "Система управління послугами салону краси.",
    })
 
def about(request):
    return render(request, "base.html", {
        "title": "Про проєкт",
        "text": "Мій проєкт — система управління Beauty Clinic на Django.",
    })