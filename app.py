import os
from flask import Flask, render_template, request, redirect
from datetime import datetime
from sqlalchemy import create_engine, Column, Integer, String, DateTime
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

# Get the database connection string directly from the environment
db_connection_string = os.environ.get('DB_CONNECTION_STRING')

if db_connection_string is None:
    raise ValueError("DB_CONNECTION_STRING environment variable is not set. Please check your environment.")

print(f'DB_CONNECTION_STRING from environment: {db_connection_string}')

app = Flask(__name__)

engine = create_engine(db_connection_string)
Session = sessionmaker(bind=engine)
Base = declarative_base()
session = Session()

class Todo(Base):
    __tablename__ = 'todo'
    id = Column(Integer, primary_key=True)
    description = Column(String)
    assigned_to = Column(String) 
    date_created = Column(DateTime(timezone=True))
Base.metadata.create_all(bind=engine)

@app.route('/', methods=['POST', 'GET'])
def index():
    if request.method == 'POST':
        task_content = request.form['content']
        assigned_to = request.form.get('assigned_to')  
        new_task = Todo(description=task_content, assigned_to=assigned_to, date_created=datetime.now())

        try:
            session.add(new_task)
            session.commit()
            return redirect('/')
        except:
            return 'There was an issue adding your task'
    else:
        todos = session.query(Todo).all()
        return render_template('index.html', tasks=todos)

@app.route('/delete/<int:id>', methods=['GET', 'POST'])
def delete(id):
    task_to_delete = session.get(Todo, id)

    if not task_to_delete:
        return 'Task not found', 404

    try:
        session.delete(task_to_delete)
        session.commit()
        return redirect('/')
    except:
        return 'There was a problem deleting that task'

@app.route('/update/<int:id>', methods=['GET', 'POST'])
def update(id):
    task = session.query(Todo).get(id)

    if not task:
        return 'Task not found', 404

    if request.method == 'POST':
        task.description = request.form['content']
        task.assigned_to = request.form.get('assigned_to')  

        try:
            session.commit()
            return redirect('/')
        except:
            return 'There was an issue updating your task'
    else:
        return render_template('update.html', task=task)

if __name__ == "__main__":
    app.run(debug=True)