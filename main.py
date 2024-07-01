from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from typing import List
from sqlalchemy.orm import Session
from database import engine, SessionLocal
import models

app = FastAPI()

# Create the database tables
models.Base.metadata.create_all(bind=engine)


class ChoiceBase(BaseModel):
    choice_text: str
    is_correct: bool


class QuestionBase(BaseModel):
    question_text: str
    choices: List[ChoiceBase]


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.post("/questions/")
async def create_questions(question: QuestionBase, db: Session = Depends(get_db)):
    db_question = models.Questions(question_text=question.question_text)
    db.add(db_question)
    db.commit()
    db.refresh(db_question)

    for choice in question.choices:
        db_choice = models.Choices(
            choice_text=choice.choice_text,
            is_correct=choice.is_correct,
            question_id=db_question.id
        )
        db.add(db_choice)

    db.commit()

    return {"question_id": db_question.id}


@app.get("/questions/{question_id}")
async def read_question(question_id: int, db: Session = Depends(get_db)):
    result = db.query(models.Questions).filter(models.Questions.id == question_id).first()

    if not result:
        raise HTTPException(status_code=404, detail="Question not found")
    return result


@app.get("/choices/{question_id}")
async def read_choices(question_id: int, db: Session = Depends(get_db)):
    results = db.query(models.Choices).filter(models.Choices.question_id == question_id).all()

    if not results:
        raise HTTPException(status_code=404, detail="Choices not found")
    return results
