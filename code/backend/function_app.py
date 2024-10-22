import azure.functions as func

# from health.function import bp as bp_health
from videoupload.function import bp as bp_videoupload
from blobtest.function import bp as bp_blobtest

app = func.FunctionApp(http_auth_level=func.AuthLevel.FUNCTION)
app.register_functions(bp_videoupload)
app.register_functions(bp_blobtest)
# app.register_functions(bp_health)
