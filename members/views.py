from django.shortcuts import render,redirect
from django.contrib.auth import authenticate,login,logout
from django.contrib import messages
from .forms import CustomUserCreationForm
# Create your views here.

def login_in(request):
    
    if request.method == "POST":
        username = request.POST["username"].lower().strip()
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            if user.is_superuser:
                return redirect("/admin")
            return redirect("/")
        else:
            messages.success(request,("there's an error in login ,try again"))
            return redirect("login")
        
    else : 
        return render(request,"login.html")
    
def logout_view(request):
    logout(request)
    messages.success(request,("you're successfully logout"))
    return redirect("login")   

def register_user(request):
    if request.method == "POST":
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data["username"]
            password = form.cleaned_data["password1"]
            email = form.cleaned_data["email"] 
            user = authenticate(username=username, password=password)
            login(request, user)
            messages.success(request, "Registration successful!")
            return redirect("/")
    else:
        form = CustomUserCreationForm()
    
    return render(request, "register.html", {"form": form})

