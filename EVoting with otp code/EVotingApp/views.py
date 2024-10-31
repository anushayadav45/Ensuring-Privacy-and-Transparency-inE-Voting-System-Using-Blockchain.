from django.shortcuts import render
from django.template import RequestContext
from django.contrib import messages
import pymysql
from django.http import HttpResponse
from django.core.files.storage import FileSystemStorage
import os
from Blockchain import *
from Block import *
from datetime import date
import cv2
import numpy as np
import base64
import random
from datetime import datetime
from PIL import Image
from sendmail import sendmail
import random

global username, password, contact, email, address,adhar

blockchain = Blockchain()
if os.path.exists('blockchain_contract.txt'):
    with open('blockchain_contract.txt', 'rb') as fileinput:
        blockchain = pickle.load(fileinput)
    fileinput.close()

face_detection = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')
recognizer = cv2.face_LBPHFaceRecognizer.create()

def votepage(request):
    if request.method == 'GET':
       return render(request, 'VotePage.html', {})
    
def OTPValidation(request):
    if request.method == 'GET':
       return render(request, 'OTPValidation.html', {})
    
def generate_otp(length=4):
    digits = "0123456789"
    otp = ""
    for _ in range(length):
        otp += random.choice(digits)
    return otp

      

def AddParty(request):
    if request.method == 'GET':
       return render(request, 'AddParty.html', {})

def index(request):
    if request.method == 'GET':
       return render(request, 'index.html', {})

def Login(request):
    if request.method == 'GET':
       return render(request, 'Login.html', {})

def CastVote(request):
    if request.method == 'GET':
       return render(request, 'CastVote.html', {})
    

def Register(request):
    if request.method == 'GET':
       return render(request, 'Register.html', {})

def Admin(request):
    if request.method == 'GET':
       return render(request, 'Admin.html', {})
    
def WebCam(request):
    if request.method == 'GET':
        data = str(request)
        formats, imgstr = data.split(';base64,')
        imgstr = imgstr[0:(len(imgstr)-2)]
        data = base64.b64decode(imgstr)
        if os.path.exists("EVotingApp/static/photo/test.png"):
            os.remove("EVotingApp/static/photo/test.png")
        with open('EVotingApp/static/photo/test.png', 'wb') as f:
            f.write(data)
        f.close()
        context= {'data':"done"}
        return HttpResponse("Image saved")    

def checkUser(name):
    flag = 0
    for i in range(len(blockchain.chain)):
          if i > 0:
              b = blockchain.chain[i]
              data = b.transactions[0]
              print(data)
              arr = data.split("#")
              if arr[0] == name:
                  flag = 1
                  break
    return flag            

def getOutput(status):
    output = '<h3><br/>'+status+'<br/><table border=1 align=center>'
    output+='<tr><th><font size=3 color=black>Candidate Name</font></th>'
    output+='<th><font size=3 color=black>Party Name</font></th>'
    output+='<th><font size=3 color=black>Area Name</font></th>'
    output+='<th><font size=3 color=black>Image</font></th>'
    output+='<th><font size=3 color=black>Cast Vote Here</font></th></tr>'
    con = pymysql.connect(host='127.0.0.1',port = 3306,user = 'root', password = 'root', database = 'evoting',charset='utf8')
    with con:
        cur = con.cursor()
        cur.execute("select * FROM addparty")
        rows = cur.fetchall()
        for row in rows:
            cname = row[0]
            pname = str(row[1])
            area = row[2]
            image = row[3]
            output+='<tr><td><font size=3 color=black>'+cname+'</font></td>'
            output+='<td><font size=3 color=black>'+pname+'</font></td>'
            output+='<td><font size=3 color=black>'+area+'</font></td>'
            output+='<td><img src="/static/parties/'+cname+'.png" width=200 height=200></img></td>'
            output+='<td><a href="FinishVote?id='+cname+'"><font size=3 color=black>Click Here</font></a></td></tr>'
    output+="</table><br/><br/><br/><br/><br/><br/>"        
    return output      
    

def OTPAction(request):
    if request.method == 'POST':
      global username, password, contact, email, address,adhar
      otp = request.POST.get('otp', False)
      status = 'none'
      con = pymysql.connect(host='127.0.0.1',port = 3306,user = 'root', password = 'root', database = 'evoting',charset='utf8')
      with con:
        cur = con.cursor()
        cur.execute("select * FROM otp")
        rows = cur.fetchall()
        for row in rows:
            if row[0] == username and int(row[1] )== int(otp):
                status = 'success'   
                print("111111111111111111111111111111111111111")             
                break 
      if status == 'success':
            print("2222222222222222222222222222222222222")        
            output = getOutput("User predicted as : "+username+"<br/><br/>")
            print(output)
            context= {'data':output}            
            return render(request, 'VotePage.html', context)
      else:
            context= {'data':'Invalid OTP'}
            return render(request, 'OTPValidation.html', context) 
      
def FinishVote(request):
    if request.method == 'GET':
        global username
        cname = request.GET.get('id', False)
        voter = ''
        today = date.today()
        data = str(username)+"#"+str(cname)+"#"+str(today)
        blockchain.add_new_transaction(data)
        hash = blockchain.mine()
        b = blockchain.chain[len(blockchain.chain)-1]
        print("Previous Hash : "+str(b.previous_hash)+" Block No : "+str(b.index)+" Current Hash : "+str(b.hash))
        bc = "Previous Hash : "+str(b.previous_hash)+"<br/>Block No : "+str(b.index)+"<br/>Current Hash : "+str(b.hash)
        blockchain.save_object(blockchain,'blockchain_contract.txt')
        context= {'data':'<font size=3 color=black>Your Vote Accepted<br/>'+bc}
        return render(request, 'UserScreen.html', context)
    
def getUserImages():
    names = []
    ids = []
    faces = []
    dataset = "EVotingApp/static/profiles"
    count = 0
    for root, dirs, directory in os.walk(dataset):
        for j in range(len(directory)):
            pilImage = Image.open(root+"/"+directory[j]).convert('L')
            imageNp = np.array(pilImage,'uint8')
            name = os.path.splitext(directory[j])[0]
            names.append(name)
            faces.append(imageNp)
            ids.append(count)
            count = count + 1
    print(str(names)+" "+str(ids))        
    return names, ids, faces        


def getName(predict, ids, names):
    name = "Unable to get name"
    for i in range(len(ids)):
        if ids[i] == predict:
            name = names[i]
            break
    return name    

def ValidateUser(request):
    if request.method == 'POST':
        global username,email
        
        status = "unable to predict user"
        img = cv2.imread('EVotingApp/static/photo/test.png')
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        face_component = None
        faces = face_detection.detectMultiScale(img,scaleFactor=1.1,minNeighbors=5,minSize=(30,30),flags=cv2.CASCADE_SCALE_IMAGE)
        status = "Unable to predict.Please retry"
        #for (x, y, w, h) in faces:
        #    face_component = gray[y:y+h, x:x+w]
        faces = sorted(faces, reverse=True,key=lambda x: (x[2] - x[0]) * (x[3] - x[1]))[0]
        (fX, fY, fW, fH) = faces
        face_component = gray[fY:fY + fH, fX:fX + fW]
        if face_component is not None:
            names, ids, faces = getUserImages()
            recognizer.train(faces, np.asarray(ids))
            predict, conf = recognizer.predict(face_component)
            print(str(predict)+" === "+str(conf))
            if(conf < 80):
                validate_user = getName(predict, ids, names)
                print(str(validate_user)+" "+str(username))
                if validate_user == username:
                    status = "success"
        else:
            status = "Unable to detect face"
        if status == "success":
            flag = checkUser(username)
            if flag == 0:                
                otp = generate_otp()
                print(otp)
                db_connection1 = pymysql.connect(host='127.0.0.1',port = 3306,user = 'root', password = 'root', database = 'evoting',charset='utf8')
                db_cursor1 = db_connection1.cursor()
                student_sql_query1 ="select email FROM register where username='"+username+"'"
                db_cursor1.execute(student_sql_query1)
                db_connection1.commit()  
                rows = db_cursor1.fetchall()
                print(rows[0])
                sendmail(rows[0],otp)   
                context= {'data':'Welcome '+username+''}
                db_connection = pymysql.connect(host='127.0.0.1',port = 3306,user = 'root', password = 'root', database = 'evoting',charset='utf8')
                db_cursor = db_connection.cursor()
                student_sql_query = "INSERT INTO otp(username,otp) VALUES('"+username+"','"+otp+"')"
                db_cursor.execute(student_sql_query)
                db_connection.commit()  
                return render(request, 'OTPValidation.html', context)
               # return render(request, 'VotePage.html', context)
            else:
                context= {'data':"You already casted your vote"}
            return render(request, 'UserScreen.html', context)
        else:
            context= {'data':status}
            return render(request, 'UserScreen.html', context)
        

def getCount(name):
    count = 0
    cname=name
    for i in range(len(blockchain.chain)):
          if i > 0:
              print("dddddddddddddddddddddddddddddd")
              print(i)
              b = blockchain.chain[i]             
              data = b.transactions[0]            
              arr = data.split("#")
              print(arr)
              #print(len(arr))
              print(cname)
              print(arr[1])
              if arr[1] == name:
                  count = count + 1
                  #print(arr[i])
                  print(count)
    return count

def ViewVotes(request):
    if request.method == 'GET':
        output = '<table border=1 align=center>'
        output+='<tr><th><font size=3 color=black>Candidate Name</font></th>'
        output+='<th><font size=3 color=black>Party Name</font></th>'
        output+='<th><font size=3 color=black>Area Name</font></th>'
        output+='<th><font size=3 color=black>Image</font></th>'
        output+='<th><font size=3 color=black>Vote Count</font></th>'
        con = pymysql.connect(host='127.0.0.1',port = 3306,user = 'root', password = 'root', database = 'evoting',charset='utf8')
        with con:
            cur = con.cursor()
            cur.execute("select * FROM addparty")
            rows = cur.fetchall()
            for row in rows:
                cname = row[0]
                count = getCount(cname)
                pname = str(row[1])
                area = row[2]
                image = row[3]
                output+='<tr><td><font size=3 color=black>'+cname+'</font></td>'
                output+='<td><font size=3 color=black>'+pname+'</font></td>'
                output+='<td><font size=3 color=black>'+area+'</font></td>'
                output+='<td><img src="/static/parties/'+cname+'.png" width=200 height=200></img></td>'
                output+='<td><font size=3 color=black>'+str(count)+'</font></td></tr>'
        output+="</table><br/><br/><br/><br/><br/><br/>"        
        context= {'data':output}
        return render(request, 'ViewVotes.html', context)    
            
def ViewParty(request):
    if request.method == 'GET':
        output = '<table border=1 align=center>'
        output+='<tr><th><font size=3 color=black>Candidate Name</font></th>'
        output+='<th><font size=3 color=black>Party Name</font></th>'
        output+='<th><font size=3 color=black>Area Name</font></th>'
        output+='<th><font size=3 color=black>Image</font></th>'
        con = pymysql.connect(host='127.0.0.1',port = 3306,user = 'root', password = 'root', database = 'evoting',charset='utf8')
        with con:
            cur = con.cursor()
            cur.execute("select * FROM addparty")
            rows = cur.fetchall()
            for row in rows:
                cname = row[0]
                pname = str(row[1])
                area = row[2]
                image = row[3]
                output+='<tr><td><font size=3 color=black>'+cname+'</font></td>'
                output+='<td><font size=3 color=black>'+pname+'</font></td>'
                output+='<td><font size=3 color=black>'+area+'</font></td>'
                output+='<td><img src="/static/parties/'+cname+'.png" width=200 height=200></img></td></tr>'
        output+="</table><br/><br/><br/><br/><br/><br/>"        
        context= {'data':output}
        return render(request, 'ViewParty.html', context)    

def AddPartyAction(request):
    if request.method == 'POST':
      cname = request.POST.get('t1', False)
      pname = request.POST.get('t2', False)
      area = request.POST.get('t3', False)
      myfile = request.FILES['t4']

      fs = FileSystemStorage()
      filename = fs.save('EVotingApp/static/parties/'+cname+'.png', myfile)
      
      db_connection = pymysql.connect(host='127.0.0.1',port = 3306,user = 'root', password = 'root', database = 'evoting',charset='utf8')
      db_cursor = db_connection.cursor()
      student_sql_query = "INSERT INTO addparty(candidatename,partyname,areaname,image) VALUES('"+cname+"','"+pname+"','"+area+"','"+cname+"')"
      db_cursor.execute(student_sql_query)
      db_connection.commit()
      print(db_cursor.rowcount, "Record Inserted")
      if db_cursor.rowcount == 1:
       context= {'data':'Party Details Added'}
       return render(request, 'AddParty.html', context)
      else:
       context= {'data':'Error in adding party details'}
       return render(request, 'AddParty.html', context)    

def saveSignup(request):
    if request.method == 'POST':
        global username, password, contact, email, address,adhar
        img = cv2.imread('EVotingApp/static/photo/test.png')
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        face_component = None
        faces = face_detection.detectMultiScale(gray, 1.3,5)
        for (x, y, w, h) in faces:
            face_component = img[y:y+h, x:x+w]
        if face_component is not None:
            cv2.imwrite('EVotingApp/static/profiles/'+username+'.png',face_component)
            db_connection = pymysql.connect(host='127.0.0.1',port = 3306,user = 'root', password = 'root', database = 'evoting',charset='utf8')
            db_cursor = db_connection.cursor()
            print(username, password, contact, email, address,adhar)
            student_sql_query = "INSERT INTO register(username,password,contact,email,adhar,address) VALUES('"+username+"','"+password+"','"+contact+"','"+email+"','"+adhar+"','"+address+"')"
            db_cursor.execute(student_sql_query)
            db_connection.commit()
            print(db_cursor.rowcount, "Record Inserted")
            if db_cursor.rowcount == 1:
                context= {'data':'Signup Process Completed'}
                return render(request, 'Register.html', context)
            else:
                context= {'data':'Unable to detect face. Please retry'}
                return render(request, 'Register.html', context)


def Signup(request):
    if request.method == 'POST':
      global username, password, contact, email, address,adhar
      username = request.POST.get('username', False)
      password = request.POST.get('password', False)
      contact = request.POST.get('contact', False)
      email = request.POST.get('email', False)
      adhar = request.POST.get('adhar', False)
      address = request.POST.get('address', False)
      context= {'data':'Capture Your face'}
      return render(request, 'CaptureFace.html', context)
      
def AdminLogin(request):
    if request.method == 'POST':
        global username
        username = request.POST.get('username', False)
        password = request.POST.get('password', False)
        if username == 'admin' and password == 'admin':
            context= {'data':'Welcome '+username}
            return render(request, 'AdminScreen.html', context)
        if status == 'none':
            context= {'data':'Invalid login details'}
            return render(request, 'Admin.html', context)

def UserLogin(request):
    if request.method == 'POST':
        global username
        username = request.POST.get('username', False)
        password = request.POST.get('password', False)
        status = 'none'
        con = pymysql.connect(host='127.0.0.1',port = 3306,user = 'root', password = 'root', database = 'evoting',charset='utf8')
        with con:
            cur = con.cursor()
            cur.execute("select * FROM register")
            rows = cur.fetchall()
            for row in rows:
                if row[0] == username and row[1] == password:
                    db_connection1 = pymysql.connect(host='127.0.0.1',port = 3306,user = 'root', password = 'root', database = 'evoting',charset='utf8')
                    db_cursor1 = db_connection1.cursor()
                    student_sql_query1 = "delete from otp"
                    db_cursor1.execute(student_sql_query1)
                    db_connection1.commit()
                    status = 'success'
                    break
        if status == 'success':
            context= {'data':'<center><font size="3" color="black">Welcome '+username+'<br/><br/><br/><br/><br/>'}
            return render(request, 'UserScreen.html', context)
        else:
            context= {'data':'Invalid login details'}
            return render(request, 'Login.html', context)





        
            
