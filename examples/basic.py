import sys
sys.path.append("../src")

from cq_enclosure_builder import PartFactory as pf

print("available categories: " + str(pf.list_categories()))

print("types of jacks: " + str(pf.list_available_types_of_jack()))

print("\n> trying to list parameters for jack without specifying part_type")
try: pf.list_parameters_for_jack()
except: print("GOT EXCEPTION! (as expected)")

print("\n> trying to list parameters for jack with part_type='6.35mm PJ-612A'")
print(f"params for jack with explicit type: {str(pf.list_parameters_for_jack(part_type='6.35mm PJ-612A'))}")

print("\n> setting default jack type to '6.35mm PJ-612A' and trying again to list parameters for jack without specifying part_type")
pf.set_default_types({
    "jack": '6.35mm PJ-612A',
})
print(f"params for jack using default type '{pf.default_types['jack']}': {str(pf.list_parameters_for_jack())}")

print("\n> Trying to build jack without passing parameter enclosure_wall_thickness...")
try: pf.build_jack()
except: print("GOT EXCEPTION (as expected)")

print("\n> Setting a default enclosure_wall_thickness with set_default_parameters, and trying again...")

pf.set_default_parameters({
    "enclosure_wall_thickness": 2
})
other_jack = pf.build_jack()
print("Success!")