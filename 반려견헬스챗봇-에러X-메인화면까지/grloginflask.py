from flask import Flask, render_template, request
import openai
import mysql.connector
import os

app = Flask(__name__)

# MySQL 연결 설정
mydb = mysql.connector.connect(
    host="localhost",
    user="root",
    password="0000",
    database="aisql"
)

mycursor = mydb.cursor()

# 사용자 생성 함수
def create_user(username, password):
    sql = "INSERT INTO users (username, password) VALUES (%s, %s)"
    val = (username, password)
    mycursor.execute(sql, val)
    mydb.commit()

# 사용자 인증 함수
def authenticate_user(username, password):
    sql = "SELECT * FROM users WHERE username = %s AND password = %s"
    val = (username, password)
    mycursor.execute(sql, val)
    result = mycursor.fetchall()
    return bool(result)

# OpenAI API 인증 정보 설정
from dotenv import load_dotenv

# OPENAI_API_KEY = 
# openai.api_key = OPENAI_API_KEY
load_dotenv('env/data.env')
print(os.getenv('OPENAI_API_KEY'))


# 이전 대화 내용을 저장할 리스트
history_message = [
    {"role": "system", "content": "Companion Pet Healthcare AI Assistant"}
]

# GPT-3 엔진 선택
model_engine = "gpt-3.5-turbo"

# OpenAI API를 호출하여 대화를 생성하는 함수
def generate_chat(question):
    history_message.append({"role": "user", "content": question})
    completions = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=history_message
    )
    message = completions.choices[0].message.to_dict()
    answer = message["content"].strip()

    history_message.append(message)
    return answer

app = Flask(__name__, template_folder='templates')

@app.route('/')
def index():
   return render_template('index.html')

# 정적 파일 경로 설정
@app.route('/static/<path:filename>')
def serve_static(filename):
    return app.send_static_file(filename)

@app.route('/index2')
def index2():
    return render_template('index2.html')

@app.route('/contact')
def contact():
    return render_template('contact.html')

@app.route('/join')
def join_get():
    return render_template('join.html')

@app.route('/join', methods=['POST'])
def join_post():
    username = request.form['username']
    password = request.form['password']
    create_user(username, password)
    return render_template('join_result.html', result='가입되었습니다.')


@app.route('/chat', methods=['POST'])
def chat():
    username = request.form['username']
    password = request.form['password']
    message = request.form['message']

    authenticated = authenticate_user(username, password)

    if authenticated:
        history_message.append({"role": "user", "content": message})
        completions = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=history_message
        )
        message = completions.choices[0].message.to_dict()
        answer = message["content"].strip()

        history_message.append(message)
    else:
        answer = "사용자 인증 실패"

    return render_template('chat.html', answer=answer)

if __name__ == '__main__':
    app.run(debug=True)
