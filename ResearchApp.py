from app import create_app, db
from app.Model.models import Post, Field, Language, Elective

app = create_app()

@app.before_first_request
def initDB(*args, **kwargs):
    db.create_all()
    if Field.query.count() == 0:
        fields = ['Computer Science','Biology', 'Physics', 'Psychology']
        for t in fields:
            db.session.add(Field(name=t))

    if Language.query.count() == 0:
        langs = ['C++', 'Scratch', 'Python', 'HTML', 'Haskell']
        for t in langs:
            db.session.add(Language(name=t))
        db.session.commit()

    if Elective.query.count() == 0:
        electives = ['Machine Learning', 'Big Data', 'Introduction to Killer AI', 'OOP', 'Finite Automata', 'Programming Language Design']
        for t in electives:
            db.session.add(Elective(title=t))
        db.session.commit()
    

if __name__ == "__main__":
    app.run(debug=True)