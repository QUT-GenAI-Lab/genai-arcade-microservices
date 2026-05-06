from typing import Callable
import gc
import torch
import os

LAZY_LOAD_ENABLED = os.getenv("LAZY_LOAD", "false").lower() == "true"


class LazyModel:
    unload_func = None
    init_func: Callable | None = None
    is_loaded = False

    def __init__(self, model_id: str):
        self.model_id = model_id

    def load(self):
        def decorator(init_func):
            if not LAZY_LOAD_ENABLED:
                # Even if eager loading, the model should only be initialized once.
                if not self.is_loaded:
                    init_func()
                    self.is_loaded = True
                self.init_func = init_func
                return init_func

            def wrapper():
                global current_model
                if current_model is not None and current_model != self.model_id:
                    print(
                        f"Unloading currently loaded model '{current_model}' before loading '{self.model_id}'..."
                    )
                    _unload()

                if current_model == self.model_id and self.is_loaded:
                    print(
                        f"Model '{self.model_id}' is already loaded. Skipping initialization."
                    )
                    return

                print(f"Loading model '{self.model_id}'...")
                init_func()
                self.is_loaded = True
                current_model = self
                print(f"Model '{self.model_id}' loaded successfully.")

            # Ensure the init_func also loads lazily
            self.init_func = wrapper
            return wrapper

        return decorator

    def unload(self):
        # Create a decorator to set the unload callback function for this model. This allows the lazy loading mechanism to call the specified function when unloading the model, ensuring proper cleanup of resources.
        def decorator(func):
            def wrapper():
                print(f"Unloading model '{self.model_id}'...")
                func()
                self.is_loaded = False
                print(f"Model '{self.model_id}' unloaded successfully.")

            self.unload_func = wrapper
            return wrapper

        return decorator

    def entry(self):
        def decorator(func):
            def wrapper(*args, **kwargs):
                if not self.init_func:
                    raise RuntimeError(
                        f"Model '{self.model_id}' does not have an initialization function defined."
                    )

                # Ensure the model is loaded before executing the main function
                if self.init_func and not self.is_loaded:
                    print(f"Model '{self.model_id}' is not loaded. Loading now...")
                    self.init_func()

                print(f"Executing main function for model '{self.model_id}'...")
                return func(*args, **kwargs)

            return wrapper

        return decorator


def _unload():
    global current_model
    if current_model and current_model.unload_func:
        current_model.unload_func()
    current_model = None
    # Ensure garbage collection and CUDA cache clearing
    gc.collect()
    if torch.cuda.is_available():
        torch.cuda.empty_cache()


# Global variaable to keep track of the currently loaded LazyModel instance. This allows the lazy loading mechanism to determine if a model is already loaded and manage unloading of other models when necessary.
current_model: LazyModel | None = None
