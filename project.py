import urllib
import requests
import pandas as pd
from github import Github
from bs4 import BeautifulSoup
from flask import Flask, request, jsonify, render_template  

app = Flask(__name__,template_folder='template')
@app.route("/")
def about():
    return render_template('index.html')  

@app.route('/search',methods=['POST'])
def home():
    cities = pd.DataFrame(columns=['Issue Number', 'Issue starting line','Issue end line','Number of comments on issue','Number of operators','Number of operands'])
    owner= request.form['Username']
    repo= request.form['Password']    
    def isOperand(ch):
        return ch.isalpha()
    def isOperator(ch):
        if ch.isalpha()==False:
            return True 
    def rev(s):
        str = ""
        for i in s:
            str = i + str
        return str
    check=False 
    import requests
    own=requests.get('https://api.github.com/repos/'+owner)
    rep = requests.get('https://api.github.com/repos/'+owner+'/'+repo)
    if own.status_code < 200:
        error = "Invalid username"
        return render_template('index.html',error=error)
    if rep.status_code > 200:
        error = "Invalid repo"
        return render_template('index.html',error=error)    

    response = requests.get('https://api.github.com/repos/'+owner+'/'+repo+'/issues')
    issues=response.json()
    size=len(issues)
    for i in range (1,size+1):
        check=True
        response = requests.get('https://api.github.com/repos/'+owner+'/'+repo+'/issues/'+str(i))
        response1 = requests.get('https://api.github.com/repos/'+owner+'/'+repo+'/issues/'+str(i)+'/comments')
        comments=response1.json()
        comments_size=len(comments)
        if response.status_code == 200:
           issue = response.json()
           temp=""
           for s in str(issue['body'])[ :  : -1]:
                   if(s=='#'):
                        break
                   else:
                       temp=temp+s
           temp=rev(temp)     
           counter=0
           num=0
           operator=0
           operand=0
           begin=0
           end=begin 
           for digit in temp:
             if digit=='-':
               counter+=1
             if counter==1:
                begin=num
                num=0
                counter+=1  
             if digit>='0' and digit<='9':
               num=num*10+int(digit) 
           end=num 
           print(begin," ",end)    
           link=issue['body']
           if link and link[1]=='t':
              boxurl = urllib.request.urlopen(link).read()
              #myfile = boxurl.read()
              soup = BeautifulSoup(boxurl)
              #print(soup)
              for b in range(begin,end+1):
                  linescoreA = soup.find("td", {"id": "LC"+str(begin)})
                  elements=list(linescoreA.stripped_strings)
                  for ele in elements:
                    if isOperator(ele):
                      operand+=1
                    else:
                      operator+=1 
           df2 = pd.DataFrame([[i,begin,end,comments_size,operand,operator]],columns=cities.columns)
           cities = pd.concat([cities,df2]) 
           #df3=pd.DataFrame([i,begin,end,comments_size])
           print(df2)              
        else:
           df3 = pd.DataFrame([[i,0,0,comments_size,0,0]],columns=cities.columns)
           cities = pd.concat([cities,df3]) 
           print(df3)
    
    if check==True:
        return render_template('result.html',tables=[cities.to_html()],titles='')  
    else:
        error = 'No issues found in this repository!'
        return render_template('index.html',error=error)  
         

if __name__ == '__main__':
    app.run(port=5000, debug=True)    


