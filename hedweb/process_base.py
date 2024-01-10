from abc import ABC, abstractmethod

class ProcessBase(ABC):

    @abstractmethod
    def set_input_from_dict(self, input_dict):
        """ Set input for processing from a JSON service request.

        parameters:
            input_dict (dict): A dict object containing user data from a JSON service request.

        """
        raise NotImplementedError
    
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
    
