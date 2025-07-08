import opensim as osim
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

# Load a model
model = osim.Model('OSIMs/scaled.osim')

# Print model info
print(model.getName())

# Method 1: Using OpenSim's built-in visualization (opens GUI)
def visualize_with_opensim_gui():
    """
    This opens the OpenSim GUI visualizer
    Note: Requires OpenSim GUI to be installed
    """
    try:
        # Initialize the model
        state = model.initSystem()
        
        # Create a visualizer
        viz = osim.simbody.Visualizer(model.getMultibodySystem())
        viz.setBackgroundType(viz.SolidColor)
        viz.setBackgroundColor(osim.simbody.Vec3(1, 1, 1))  # White background
        
        # Show the model
        viz.show(state)
        print("OpenSim GUI visualizer opened. Close the window when done viewing.")
        
    except Exception as e:
        print(f"GUI visualization failed: {e}")
        print("This might require OpenSim GUI installation or display setup")

# Method 2: Extract and plot body positions with matplotlib
def visualize_with_matplotlib():
    """
    Extract body positions and create a 3D matplotlib visualization
    """
    try:
        # Initialize the model
        state = model.initSystem()
        
        # Get all bodies in the model
        bodySet = model.getBodySet()
        
        # Extract body positions
        body_positions = []
        body_names = []
        
        for i in range(bodySet.getSize()):
            body = bodySet.get(i)
            body_names.append(body.getName())
            
            # Get body's position in ground frame
            transform = body.getTransformInGround(state)
            position = transform.p()
            body_positions.append([position.get(0), position.get(1), position.get(2)])
        
        # Convert to numpy array
        positions = np.array(body_positions)
        
        # Create 3D plot
        fig = plt.figure(figsize=(12, 8))
        ax = fig.add_subplot(111, projection='3d')
        
        # Plot body positions
        ax.scatter(positions[:, 0], positions[:, 1], positions[:, 2], 
                  c='red', s=50, alpha=0.7)
        
        # Add labels for each body
        for i, name in enumerate(body_names):
            ax.text(positions[i, 0], positions[i, 1], positions[i, 2], 
                   name, fontsize=8)
        
        # Set labels and title
        ax.set_xlabel('X (m)')
        ax.set_ylabel('Y (m)')
        ax.set_zlabel('Z (m)')
        ax.set_title(f'OpenSim Model: {model.getName()}\nBody Positions')
        
        # Make axes equal
        max_range = np.array([positions[:, 0].max()-positions[:, 0].min(),
                             positions[:, 1].max()-positions[:, 1].min(),
                             positions[:, 2].max()-positions[:, 2].min()]).max() / 2.0
        mid_x = (positions[:, 0].max()+positions[:, 0].min()) * 0.5
        mid_y = (positions[:, 1].max()+positions[:, 1].min()) * 0.5
        mid_z = (positions[:, 2].max()+positions[:, 2].min()) * 0.5
        
        ax.set_xlim(mid_x - max_range, mid_x + max_range)
        ax.set_ylim(mid_y - max_range, mid_y + max_range)
        ax.set_zlim(mid_z - max_range, mid_z + max_range)
        
        plt.tight_layout()
        plt.show()
        
        return positions, body_names
        
    except Exception as e:
        print(f"Matplotlib visualization failed: {e}")
        return None, None

# Method 3: Print model structure information
def print_model_structure():
    """
    Print detailed information about the model structure
    """
    print("\n" + "="*50)
    print(f"MODEL: {model.getName()}")
    print("="*50)
    
    # Bodies
    bodySet = model.getBodySet()
    print(f"\nBODIES ({bodySet.getSize()}):")
    for i in range(bodySet.getSize()):
        body = bodySet.get(i)
        print(f"  {i+1}. {body.getName()}")
    
    # Joints
    jointSet = model.getJointSet()
    print(f"\nJOINTS ({jointSet.getSize()}):")
    for i in range(jointSet.getSize()):
        joint = jointSet.get(i)
        print(f"  {i+1}. {joint.getName()} ({joint.getConcreteClassName()})")
    
    # Muscles (if any)
    try:
        muscleSet = model.getMuscles()
        print(f"\nMUSCLES ({muscleSet.getSize()}):")
        for i in range(muscleSet.getSize()):
            muscle = muscleSet.get(i)
            print(f"  {i+1}. {muscle.getName()}")
    except:
        print("\nMUSCLES: None found")
    
    # Coordinates
    coordSet = model.getCoordinateSet()
    print(f"\nCOORDINATES ({coordSet.getSize()}):")
    for i in range(coordSet.getSize()):
        coord = coordSet.get(i)
        print(f"  {i+1}. {coord.getName()} (range: {coord.getRangeMin():.2f} to {coord.getRangeMax():.2f})")

# Method 4: Create a simple stick figure visualization
def create_stick_figure():
    """
    Create a simple stick figure representation of the skeleton
    """
    try:
        state = model.initSystem()
        
        # Get joint positions to create stick figure
        jointSet = model.getJointSet()
        joint_positions = []
        joint_names = []
        
        for i in range(jointSet.getSize()):
            joint = jointSet.get(i)
            joint_names.append(joint.getName())
            
            # Get parent and child frames
            try:
                parent_frame = joint.getParentFrame()
                child_frame = joint.getChildFrame()
                
                # Get positions
                parent_pos = parent_frame.getPositionInGround(state)
                child_pos = child_frame.getPositionInGround(state)
                
                joint_positions.append({
                    'name': joint.getName(),
                    'parent': [parent_pos.get(0), parent_pos.get(1), parent_pos.get(2)],
                    'child': [child_pos.get(0), child_pos.get(1), child_pos.get(2)]
                })
            except:
                continue
        
        # Plot stick figure
        fig = plt.figure(figsize=(10, 8))
        ax = fig.add_subplot(111, projection='3d')
        
        # Draw connections between joints
        for joint_info in joint_positions:
            parent = joint_info['parent']
            child = joint_info['child']
            
            # Draw line between parent and child
            ax.plot([parent[0], child[0]], 
                   [parent[1], child[1]], 
                   [parent[2], child[2]], 
                   'b-', linewidth=2, alpha=0.7)
            
            # Mark joint positions
            ax.scatter(*parent, c='red', s=30)
            ax.scatter(*child, c='blue', s=30)
        
        ax.set_xlabel('X (m)')
        ax.set_ylabel('Y (m)')
        ax.set_zlabel('Z (m)')
        ax.set_title(f'Stick Figure: {model.getName()}')
        
        plt.show()
        
    except Exception as e:
        print(f"Stick figure visualization failed: {e}")

if __name__ == "__main__":
    print("OpenSim Model Visualization Options:")
    print("1. Model structure information")
    print("2. 3D body positions (matplotlib)")
    print("3. Stick figure representation")
    print("4. OpenSim GUI (if available)")
    
    # Always show model structure
    print_model_structure()
    
    # Try matplotlib visualization
    print("\nGenerating 3D visualization...")
    positions, names = visualize_with_matplotlib()
    
    # Try stick figure
    print("\nGenerating stick figure...")
    create_stick_figure()
    
    # Uncomment the line below to try OpenSim GUI visualization
    # visualize_with_opensim_gui()