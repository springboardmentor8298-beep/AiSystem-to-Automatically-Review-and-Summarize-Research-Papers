import requests
import fitz  # PyMuPDF
from pydantic import BaseModel

print("All core libraries imported successfully!")

class Demo(BaseModel):
    name: str

demo = Demo(name="Rihana")
print("Pydantic working:", demo)