from fastapi import FastAPI, Depends
from fastapi.responses import Response, JSONResponse
from contextlib import asynccontextmanager
from engine import Engine
from utils.pydantic_models import Ticket,TicketRequest, AssignRequest, CompleteRequest
import uuid
@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Starting up...")

    app.state.engine = Engine()  # store resource in app.state
    yield
    print("Shutting down...")

app = FastAPI(lifespan=lifespan)

# Dependency to get resource from app.state
def get_engine():
    return app.state.engine

@app.get("/")
async def read_root(engine=Depends(get_engine)):
    return Response({'engine':engine})

# endpoint to add ticket to bucket
@app.post('/push')
async def add_ticket(data: Ticket):
    engine:Engine = app.state.engine
    # add ticket to engine pile
    engine.add_to_queue(data)
    return JSONResponse({'ticket': data.model_dump()})

# load the engine unprocessed pile of tasks
@app.get('/pile')
async def load_pile():
    engine:Engine = app.state.engine
    # convert ticket bucket into list of json
    return JSONResponse({'tickets':engine._ticket_store_json})

@app.get('/pile/ticket/')
async def load_ticket(id:str):
    engine:Engine = app.state.engine
    # convert ticket bucket into list of json
    curr = engine.get_ticket(id)
    return JSONResponse({'ticket':curr.model_dump()})

@app.get('/pile/completions')
async def load_completions():
    engine:Engine = app.state.engine
    # convert ticket bucket into list of json
    curr = engine.get_completions()
    return JSONResponse({'completions':curr})

# assign ticket to someone
@app.post('/assign')
async def assign(data: AssignRequest):
    engine:Engine = app.state.engine
    # search for ticket from request
    curr:Ticket = engine.assign_ticket(data.id,data.assigned_to)
    # convert ticket bucket into list of json
    return JSONResponse({'ticket':curr.model_dump()})

# set ticket status to in progress
@app.post('/start')
async def start(data: AssignRequest):
    engine:Engine = app.state.engine
    # search for ticket from request
    curr:Ticket = engine.start_ticket(data.id)
    # convert ticket bucket into list of json
    return JSONResponse({'ticket':curr.model_dump()})

# mark ticket as complete
@app.post('/complete')
async def complete(data: CompleteRequest):
    engine:Engine = app.state.engine
    curr = engine.complete_ticket(data.id,data.content)
    return JSONResponse({'ticket':curr.model_dump()})

