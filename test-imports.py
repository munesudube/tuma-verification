import importlib

thing = "thing1"

module_name = f"my1.things.{thing}"
try:
    country_module = importlib.import_module(module_name)
    print( "Found" )
except ModuleNotFoundError:
    print(f"Error: Module for country '{thing}' not found.")



