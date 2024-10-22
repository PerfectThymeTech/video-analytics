import azure.functions as func
from models.health import HeartbeatResponse
# from videoupload.function import bp as bp_videoupload
from health.function import bp as bp_health

app = func.FunctionApp(http_auth_level=func.AuthLevel.FUNCTION)
# app.register_functions(bp_videoupload)
app.register_functions(bp_health)
