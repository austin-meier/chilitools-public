DEFAULT_TASKPRIORITY = 5
DEFAULT_TASKUPDATETIME = 1
USER_TYPE = 'user'
STAFF_TYPE = 'staff'

statusCodes = {
  200:"Request has succeeded",
  201:"Request has succeeded and new resource has been created",
  400:"Request failed, incorrect syntax",
  401:"Request failed, unauthorized",
  403:"Request failed, forbidden",
  404:"Request failed, resource not found",
  408:"Request timeout",
  500:"Internal server error",
  502:"Server Error, invalid gateway",
  503:"Server is not ready to handle the request",
  504:"Gateway Timeout, server cannot get a response in time for request"
}