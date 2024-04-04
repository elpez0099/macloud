# Notifications
DFLT_LOG_FORMAT = "{vendor_config} {execution_type} execution  at {execution_timestamp} by {user}"
DFLT_LOG_LFTME = 864000000  # 10 days in milliseconds

# Scheduled Jobs
DAILY_RECURRING_EVENT = 'daily'
WEEKLY_RECURRING_EVENT = 'weekly'
CUSTOM_RECURRING_EVENT = 'custom'
DFLT_EVENT_OCCURRENCE = DAILY_RECURRING_EVENT
DFLT_INVENTORY_DATA_LFTME = 432000000  # 5 days in milliseconds
DFLT_REPORT_DATA_LFTME = 864000000  # 10 days in milliseconds

# Permissions
ADMIN_USER_ROLE = 'admin'
REGULAR_USER_ROLE = 'user'

# event occurrence
PREDEFINED_OCCURRENCE_TYPES = ["daily", "weekly", "workweek"]
CUSTOM_OCCURENCE_TYPE = "custom"
SUPPORTED_OCCURENCE_TYPES = PREDEFINED_OCCURRENCE_TYPES + [CUSTOM_OCCURENCE_TYPE]

# Requests
ALLOWED_HTTP_METHODS = ["POST", "GET", "PUT"]
SUPPORTED_REQUEST_ENCODINGS = ["json", "formdata"]
SUPPORTED_AUTH_TYPES = ["basic", "jwt", "oauth2/client-credentials"]
SUPPORTED_FIELD_SOURCES = ['authorization_token', 'prev_pipeline_response']
STATIC_TOKEN_TYPE = 'static-token'
PREV_PIPELINE_RESP = 'prev_pipeline_response'
