import os
from fastapi import Depends, Header, Request
from pydantic import BaseModel, ConfigDict, Field
from .runtime import make_app, settings
from .service import InterviewService

app, auth, reviewer = make_app("RoundReady")


def service():
    return InterviewService(
        os.path.join(os.environ.get("DATA_DIR", ".data"), "roundready.db")
    )


class Account(BaseModel):
    name: str = Field(min_length=1, max_length=100)


class Start(BaseModel):
    model_config = ConfigDict(extra="forbid")
    resume: str = Field(min_length=1, max_length=20000)
    role: str = Field(min_length=1, max_length=300)
    request_key: str = Field(min_length=1, max_length=100)


class Answer(BaseModel):
    model_config = ConfigDict(extra="forbid")
    question_id: str
    answer: str = Field(min_length=1, max_length=10000)
    request_key: str = Field(min_length=1, max_length=100)


@app.post("/accounts", dependencies=[Depends(auth)])
def account(body: Account):
    return service().create_account(body.name)


@app.post("/interviews")
def start(body: Start, authorization: str = Header(default="")):
    return service().start(authorization.removeprefix("Bearer "), **body.model_dump())


@app.post("/interviews/{identifier}/answers")
def answer(identifier: str, body: Answer, authorization: str = Header(default="")):
    return service().answer(
        authorization.removeprefix("Bearer "), identifier, **body.model_dump()
    )


@app.get("/interviews/{identifier}")
def report(identifier: str, authorization: str = Header(default="")):
    return service().get(authorization.removeprefix("Bearer "), identifier)


@app.post("/billing/test-webhook")
async def webhook(request: Request, stripe_signature: str = Header(default="")):
    return service().billing_event(
        await request.body(),
        stripe_signature,
        settings().get("STRIPE_WEBHOOK_SECRET", ""),
    )
