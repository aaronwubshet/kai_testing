import opensim as osim

# Load a model
model = osim.Model('OSIMs/scaled.osim')

# Print model info
print(model.getName())