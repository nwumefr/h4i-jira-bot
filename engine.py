# this will substitute a redis instance 
# and celery workers as a kind of task queue
from utils.pydantic_models import Ticket,TicketCompletion
from uuid import UUID
import copy
import datetime
from typing import Union, List

class Engine:
    def __init__(self):
        # queue to handle priority for tickets
        self._queue:List[Ticket] = []
        self._ticket_store = {}
        # for fatsapi since Tickets arent json serializable
        self._ticket_store_json = {}
        self._backlog_json = {}
        # if a task gets taken on it gets added 
        # to the in progress bucket where we can
        # track the status
        self._in_progress = {}
        self._backlog = {}
        # dict to reverse store which person is assigned to a ticket
        self._assign_reverse = {}
    
    def add_to_queue(self,ticket:Ticket):
        # add to ticket bucket
        self._ticket_store[ticket.id] = ticket
        self._ticket_store_json[ticket.id] = ticket.model_dump()
        self._queue.append(ticket)

    def get_queue(self,limit:int=10):
        lim = limit
        que = []
        for i in self._queue:
            tid = i.id
            tick = self.get_ticket(tid)
            que.append(tick.model_dump())
        return que
    
    def assign_ticket(self,ticket_id:str,assigned_to:str):
        # remove from ticket bucket and move to inprogress
        item:Ticket = self._ticket_store[ticket_id]
        item.assigned_to = assigned_to
        item.status = 'assigned'
        self._in_progress[item.id] = item
        # setup reverse dict
        if not self._assign_reverse.get(assigned_to):
            self._assign_reverse[assigned_to] = []
        self._assign_reverse[assigned_to].append(item)
        return self._in_progress[item.id]

    def complete_ticket(self,
                        ticket_id:str,
                        content:Union[None|str]=None)->TicketCompletion:
        # remove ticket
        new:Ticket = copy.deepcopy(self._in_progress[ticket_id])
        completion = TicketCompletion(
            id = new.id,
            issuer=new.issuer,
            content=new.content,
            assigned_to=new.assigned_to,
            status='completed',
            date_started=new.date_started,
            date_completed=str(datetime.datetime.now()),
            completion_content=content
        )
        self._backlog[ticket_id] = completion
        self._backlog_json[ticket_id] = completion.model_dump()
        # remove from in_progress pile
        self._in_progress.pop(ticket_id)
        self._queue.pop(0)
        return self._backlog[ticket_id]
    
    def get_ticket(self,ticket_id)->Ticket:\
        # try if the ticket is complete
        try:
            return self._backlog[ticket_id]
        except Exception as e:
            # not complete
            pass
        # try if the ticket is in progress
        try:
            return self._in_progress[ticket_id]
        except Exception as e:
            # not complete
            pass
        return self._ticket_store[ticket_id]

    def get_completion(self,ticket_id)->TicketCompletion:
        return self._backlog[ticket_id]
    
    def get_completions(self):
        return self._backlog_json
    
    # function to set ticket status to started
    def start_ticket(self,ticket_id:str):
        tick:Ticket = self._ticket_store[ticket_id]
        tick.status = 'in_progress'
        return self._ticket_store[ticket_id]
    
