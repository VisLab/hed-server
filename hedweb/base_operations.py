from abc import ABC, abstractmethod


class BaseOperations(ABC):
    def set_input_from_dict(self, input_dict):
        """ Sets the child class attributes based on input_dict.
            Only sets attributes that exist.

        parameters:
            input_dict (dict): A dict object containing user data from a JSON service request.
        """
        # Only allowed to set variables from init, and also disallow private variables to avoid possible issues
        for key, value in input_dict.items():
            if not hasattr(self, key) or callable(getattr(self, key)) or key.startswith("_"):
                continue
            setattr(self, key, value)

    @abstractmethod
    def set_input_from_form(self, request):
        """ Set input for processing from a form.

        parameters:
            request (Request): A Request object containing user data from the form.

        """
        raise NotImplementedError

    @abstractmethod
    def process(self):
        """ Perform the requested string processing action.
 
        Returns:
            dict: The results in standard format.
    
        """
        raise NotImplementedError
