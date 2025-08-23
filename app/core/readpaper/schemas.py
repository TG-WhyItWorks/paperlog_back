import datetime

from pydantic import BaseModel,field_validator,ConfigDict



        

class ReadPaper(BaseModel):
    id:int
   # user_id:int
    paper_id:int
    create_date:datetime.datetime

class ReadPaperCreate(BaseModel):
    
   # user_id:int
    paper_id:int
        

class ReadPaperUpdate(BaseModel):
    readpaper_id:int
    #user_id:int
    paper_id:int

class ReadPaperDelete(BaseModel):
    readpaper_id:int