import tkinter as tk
from tkinter import ttk, messagebox
import traceback

fields = [{'label': 'test', 'selector': '#test', 'value': '123'}]

def test(fields):
    try:
        for field in fields:
            selector = field['selector']
            value = field['value']
            print(f"selector={selector}, value={value}")
    except Exception as e:
        print(f"Error: {e}")
        traceback.print_exc()

print("Testing...")
test(fields)
print("Done")
