from pydantic import BaseModel,Field
from typing import Annotated,Any



class Response(BaseModel):
    status : Annotated[
        int,
        Field(description= "This is the HTTPS status code for any of the concerned request"
              ,default=200)
    ]
    message : Annotated[
        str,
        Field(description="This is the description of the response",
              default="")
    ]
    anotherValid : Any