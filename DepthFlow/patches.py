import numpy as np
from functools import wraps

def safe_numpy_value(value):
    """Safely convert numpy arrays to float values"""
    if isinstance(value, np.ndarray):
        if value.size == 1:
            return float(value.item())
        return float(value[0])
    return float(value)

def patch_depthflow():
    """Patch DepthFlow to handle numpy arrays properly"""
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
        print("DepthFlow patched successfully")
    except Exception as e:
        print(f"Failed to patch DepthFlow: {e}")
