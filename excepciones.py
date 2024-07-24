class Mensaje_Para_Redireccion_de_Exception(Exception):
    def __init__ (self, message: str, path_route: str, path_message: str):
        self.message = message
        self.path_route = path_route
        self.path_message = path_message

class Exception_No_Apto_Para_Cliente(Mensaje_Para_Redireccion_de_Exception):
    def __init__(self, message='Estimado votante, esta función no es válida para su tipo de usuario.', path_route='/', path_message='home.'):
        super().__init__(message, path_route, path_message)

class Exception_No_Apto_Para_Artesano(Mensaje_Para_Redireccion_de_Exception):
    def __init__(self, message='Estimado admnistrador, esta función no es válida para su tipo de usuario.', path_route='/', path_message='home.'):
        super().__init__(message, path_route, path_message)