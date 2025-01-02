import os
import DepthFlow.Resources as DepthFlowResources
from Broken import BrokenProject, __version__

# Add GPU acceleration environment setup
os.environ["PYOPENGL_PLATFORM"] = "egl"
os.environ["__EGL_VENDOR_LIBRARY_FILENAMES"] = "/usr/share/glvnd/egl_vendor.d/10_nvidia.json"
os.environ["NVIDIA_VISIBLE_DEVICES"] = "all"
os.environ["NVIDIA_DRIVER_CAPABILITIES"] = "all"
os.environ["WINDOW_BACKEND"] = "headless"

__version__ = __version__

DEPTHFLOW_ABOUT = """
🌊 Images to → 2.5D Parallax Effect Video. A Free and Open Source ImmersityAI alternative.\n\n
→ See the [blue link=https://brokensrc.dev/depthflow/]Website[/blue link] for examples and more information!\n
"""

DEPTHFLOW = BrokenProject(
    PACKAGE=__file__,
    APP_NAME="DepthFlow",
    APP_AUTHOR="BrokenSource",
    RESOURCES=DepthFlowResources,
    ABOUT=DEPTHFLOW_ABOUT,
)

from Broken import BrokenTorch

# Add numpy array handling patch
import numpy as np
from functools import wraps

def safe_numpy_value(value):
    """Safely convert numpy arrays to float values"""
    if isinstance(value, np.ndarray):
        if value.size == 1:
            return float(value.item())
        return float(value[0])
    return float(value)

def patch_depthflow_scene():
    """Patch DepthFlow Scene to handle numpy arrays properly"""
    try:
        from DepthFlow.Scene import DepthScene
        original_load_inputs = DepthScene._load_inputs

        @wraps(original_load_inputs)
        def _load_inputs_patched(self):
            """Patched version of _load_inputs that safely handles numpy arrays"""
            # Call original method first
            original_load_inputs(self)
            
            # Then safely update state values
            if hasattr(self, 'state'):
                for item in self.animation:
                    state = item.get('state', None)
                    if state is not None and len(state) > 1:
                        try:
                            self.state.origin_x = safe_numpy_value(state[1])
                        except (IndexError, TypeError, ValueError):
                            continue

        # Apply the patch
        DepthScene._load_inputs = _load_inputs_patched
        print("DepthFlow Scene patched successfully")
    except Exception as e:
        print(f"Failed to patch DepthFlow Scene: {e}")

# Apply patches
BrokenTorch.install(exists_ok=True)
patch_depthflow_scene()

# Make DepthScene available at package level
from DepthFlow.Scene import DepthScene
