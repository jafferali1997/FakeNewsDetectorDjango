from django.shortcuts import render
from numpy import vectorize
from .models import Body, UserLoginModel
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import PassiveAggressiveClassifier
import pickle
import pandas as pd
from sklearn.model_selection import train_test_split
from django.shortcuts import render
from .models import UserInfoModel
from .forms import UserSignupForm
from .loginforms import UserLoginForm
from csv import writer
import urllib.request
import re
from django.core.validators import URLValidator
from django.core.exceptions import ValidationError

from django.contrib.auth import authenticate,login,logout
from django.http import HttpResponseRedirect, HttpResponse
from django.urls import reverse
from django.contrib.auth.decorators import login_required



def UserInfoView(request):
    CallUser = UserInfoModel.objects.order_by('FirstName')
    return render(request,'user.html',context={'user': CallUser})

@login_required
def special(request):
    return HttpResponse("You are logged in nice")

@login_required
def user_logout(request):
    logout(request)
    return HttpResponseRedirect(reverse('login'))


def SignupForm(request):

    registered = False

    if request.method=="POST":
        user_info = UserSignupForm(data=request.POST)
        user_form = UserLoginForm(data=request.POST)
        

        if user_form.is_valid() and user_info.is_valid():
            user = user_form.save()
            user.set_password(user.password)
            user.save()
            
            userinfo=user_info.save(commit=False)
            userinfo.save()
            registered=True
        else:
            print(user_form.errors,user_info.errors)

    else:
        user_form = UserLoginForm()
        user_info = UserSignupForm()
        
    return render(request,'signup.html',context={'form': user_form,'registered':registered,'forminfo':user_info})

def LoginForm(request):

    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(username=username,password=password)

        if user:
            if user.is_active:
                login(request,user)
                return HttpResponseRedirect(reverse('index'))
            else:
                return HttpResponse("ACCOUNT NOT ACTIVE")
        else:
            print("someone tried to login but failed")
            print("Username:{} Password:{}".format(username,password))
            return HttpResponse("Invalid login details")
    else:
        return render(request,'login.html',{})


def TextAreaForm(request):   
    return render(request,'index.html',{})
    

def ResultOut(request):
    if request.method == "POST" and request.POST.get("text") and request.POST.get("texturl")=='' :
        text = request.POST.get("text","")
        Result = predict(text)

        return render(request,'result.html',context={"result":Result})
    elif request.method == "POST" and request.POST.get("texturl") and request.POST.get("text")=='' :
        text = request.POST.get("texturl","")
        validate = URLValidator()

        try:
            validate(text)
        except ValidationError as exception:
            Result = 'incorrect url'
            return render(request,'result.html',context={"result":Result})

        
        file = urllib.request.urlopen(text).read().decode('UTF-8')
        clean = re.compile('<.*?>')
        text = re.sub(clean, '', file)
        Result= predict(text)
        return render(request,'result.html',context={"result":Result})
    
    Result='Please fill in one box'

    return render(request,'result.html',context={"result":Result})



def AddNew(request):
    Added=''
    if request.method == "POST":
        text = request.POST.get("text","")
        label = request.POST.get("label","")
        Added = InsertResult(text, label)
    return render(request,'addnew.html',{'added':Added})

def InsertResult(text, label):
    label= label.lower()
    if label=='fake':
        lab = 0
    else:
        lab = 1
    List=['A','A',text,lab]
    with open('C:/Users/Jaffer Ali/projects/FYP/FakeNewsDetector/data.csv', 'a') as f_object:
        writer_object = writer(f_object)
        writer_object.writerow(List)
        f_object.close()
        
    return 'Done'

def predict(text):
    tfvect = TfidfVectorizer(stop_words='english', max_df=0.7)
    
    DataFrame = pd.read_csv('C:/Users/Jaffer Ali/projects/FYP/FakeNewsDetector/data.csv')
    DataFrame=DataFrame.dropna()
    x=DataFrame['Body']
    y=DataFrame['Label']
    if type(DataFrame['Label'][0])==str:
        check=DataFrame['Label'][0].lower()
    else:
        check=DataFrame['Label'][0]
    if check!='fake' or check!='real':
        y= DataFrame['Label'].replace({0:'Fake', 1:'Real'})
    
    xy = tfvect.fit_transform(x)
    
    
    classifire = PassiveAggressiveClassifier(max_iter=50)
    classifire.fit(xy,y)

    pickle.dump(classifire,open('C:/Users/Jaffer Ali/projects/FYP/FakeNewsDetector/model.pkl','wb'))
    loaded_model =pickle.load(open('C:/Users/Jaffer Ali/projects/FYP/FakeNewsDetector/model.pkl','rb'))
    input_data=[text]
    vectorize_input_data = tfvect.transform(input_data)
    prediction = loaded_model.predict(vectorize_input_data)
    
    i=0
    word=''
    NumberofWords=0
    NotEnglishWord=0
    df = str(DataFrame['Body'])
    df1 = str(DataFrame['Headline'])
    df=df.lower()
    df1=df1.lower()
    checklength=len(input_data[0])
    while i<checklength:
        if input_data[0][i]!=' ': 
            word= word + str(input_data[0][i])
            word=word.lower()
        elif word!=' ':
            NumberofWords= NumberofWords+1
            if df.find(word)==-1 and df1.find(word)==-1:
                NotEnglishWord=NotEnglishWord+1
            word=''
        i=i+1
    if NumberofWords==0:
        prediction='Not A News'
    

    return prediction
    
