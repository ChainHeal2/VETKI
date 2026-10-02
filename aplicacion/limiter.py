""" Este módulo proporciona un limitador de solicitudes para la aplicación Flask. 
de esta manera, se puede controlar la cantidad de solicitudes que un usuario puede realizar en un período de tiempo determinado,
lo que ayuda a prevenir abusos y ataques de denegación de servicio (DoS). """
try:
    from flask_limiter import Limiter
    from flask_limiter.util import get_remote_address

    limiter = Limiter(key_func=get_remote_address, default_limits=[])
except ImportError:
    class _NoopLimiter:
        def limit(self, _limit):
            return lambda view: view

        def init_app(self, _app):
            return None

    limiter = _NoopLimiter()