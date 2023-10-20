from flask import Flask, render_template, request
import requests
import PyPDF2
import re

app = Flask(__name__)

def read_cv(name):
    #Return the cv as a string from the file uploaded

    #Parameters:
    # name(str): The name of the file to be read

    #Returns:
    #  cv(str): The cv as a string
    pdfReader = PyPDF2.PdfReader(name)
    if len(pdfReader.pages)==0:
        return []
    pageObj = pdfReader.pages[0]
    cv=pageObj.extract_text()
    print(cv)
    return cv

def info_extraction(cv,reg):
    # Check if the info exists in the cv

    # Parameters:
    # cv(str): The CV for extraction
    # reg(str): The regular expression for extraction

    # Returns:
    #  0/1(int): 1 if the cv contains such information, 0 if otherwise
    if len(re.findall(reg,cv))==0:
        return 0
    else:
        return 1

def grading(information,optional):
    total = 100
    missing_mand=[]
    for k,v in information.items():
        if v == 0:
            missing_mand.append(k)
            total -= 20
    for k,v in optional.items():
        if v == 1:
            total += 10
    print(total)
    if total < 60:
        return "Your resume did not pass our checks, please fix the following information: "+ ', '.join(missing_mand)
    elif total >= 60 & len(missing_mand) != 0:
        return "Your resume passed our checks, please fix the following information: " + ', '.join(missing_mand)
    elif total == 100 & len(missing_mand) != 0:
        return "Your resume is really good! However, it will be better if you include: " + ', '.join(missing_mand)
    else:
        print(missing_mand)
        return "Your resume is perfect!"



@app.route('/')
def homepage():
    return render_template('index.html')

@app.route('/cv-upload')
def image_upload():
    return render_template('cv-upload.html')

@app.route('/predict', methods=['POST'])
def evaluate():
    mandatory = {'LinkedIn':0, 'email': 0, 'experience':0, 'education':0, 'phone number': 0}
    optional = {'project': 0, 'certificates': 0}
    file = request.files['file']
    print(file)
    #if file not in request.files:
     #   print('no file1')
      #  return render_template('error.html')
    if file.filename == '':
        print('no file2')
        return render_template('error.html')
    if file:
        cv = read_cv(file)
        project = r'(?i)project'
        certificates = r'(?i)certificates'
        education=r"(?i)EDUCATION"
        experience = r'(?i)experience'
        email = r"(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)"
        LinkedIn = r'^https:\\/\\/[a-z]{2,3}\\.linkedin\\.com\\/.*$'
        phone = r'^(?:\(\d{3}\)|\d{3})-\d{3}-\d{4}$'
        mandatory['LinkedIn']=info_extraction(cv,LinkedIn)
        mandatory['email'] = info_extraction(cv,email)
        mandatory['experience'] = info_extraction(cv, experience)
        mandatory['education'] = info_extraction(cv, education)
        mandatory['phone number'] = info_extraction(cv, phone)
        optional['project'] = info_extraction(cv,project)
        optional['certificates']= info_extraction(cv,certificates)
        result_text = grading(mandatory,optional)
        return render_template('result.html', result=result_text)


if __name__ == '__main__':
    app.run()
