# this file is the entrypoint for dispatched functions; the only purpose is to
# provide a function (`execute_dispatched`) for cloud functions to call,
# and to ensure all the functions are imported and registered (any function
# that is not imported at startup will not be visible to
# `cloud_functions_dispatch`)

from cloud_functions_dispatch import execute as execute_dispatched  # noqa
import functions  # noqa
