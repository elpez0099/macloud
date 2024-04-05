from .repositories.VendorConfigurationRepository import \
    VendorConfigurationRepository
from .const import DFLT_LOG_FORMAT, DFLT_LOG_LFTME, \
    PREDEFINED_OCCURRENCE_TYPES, CUSTOM_OCCURENCE_TYPE
from .Exceptions import ValidationError
from .pipeline.PipelineSettings import PipelineSettings


class VendorConfiguration:
    pipeline = []
    config = {}
    config_id = None

    def __init__(self, payload=None, config_id=None):
        if payload and config_id:
            raise AttributeError('''Parameter conflict!,
                 you must provide either a payload or config id.''')

        if payload is not None:
            self.set_config_from_payload(payload)

        self.repository = VendorConfigurationRepository()
        if config_id is not None:
            self.set_config_from_db(config_id)

    def set_config_attribute(self, payload, attribute):
        handlers = {
            'permissions': self.set_permissions,
            'logging': self.set_logging,
            'notifications': self.validate_notifications_settings,
            'execution_settings': self.validate_execution_settings,
            'pipeline': self.validate_pipeline
        }

        validator = handlers.get(attribute)
        validator(payload)

    def set_config_from_payload(self, payload, attribute=None):
        if attribute is not None:
            self.set_config_attribute(payload, attribute)
            return

        # Check notifications settings
        self.validate_permissions_settings(payload.get('permissions'))

        # Check logging settings
        self.validate_logging_settings(payload.get('permissions'))

        # Check notifications settings
        self.validate_notifications_settings(payload.get('notifications'))

        # Check if execution settings exists and if so validate it
        self.validate_execution_settings(payload.get('execution_settings'))
        # Check pipeline items
        self.validate_pipeline(payload.get('pipeline', []))

        # If payload is valid it is set as the config
        self.config = payload

    def set_config_from_db(self, id):
        # Vendor config id lookup and get config paylod
        self.config_id = id
        self.config = self.repository.findById(id)

    def get_configuration(self):
        return self.config

    def get_attribute(self, attribute):
        return self.config.get(attribute, {})

    def validate_permissions_settings(self, permissions_settings):
        # If no permissions were defined in payload
        # we set it with default values
        if permissions_settings is None:
            permissions_settings = {
                "roles": ["admin"]
            }
            self.set_permissions(permissions_settings)

    # permissions settings
    def set_permissions(self, permissions_settings):
        self.config['permissions'] = permissions_settings

    def validate_logging_settings(self, logging_settings):
        if logging_settings is None:
            logging_settings = {
                "enabled": False,
                "format": DFLT_LOG_FORMAT,
                "lifetime": DFLT_LOG_LFTME
            }
            self.set_logging(logging_settings)

    # logging settings
    def set_logging(self, logging_settings):
        self.config['logging'] = logging_settings

        return self.config

    def validate_notifications_settings(self, notifications_settings):
        if notifications_settings is None:
            notifications_settings = {
                "enabled": False,
                "error_recipient_list": [],
                "report_recipient_list": []
            }
            self.set_notifications(notifications_settings)
        elif notifications_settings.get('enabled'):
            error_recipient_list = notifications_settings.get(
                'error_recipient_list')
            report_recipient_list = notifications_settings.get(
                'report_recipient_list')
            if not error_recipient_list and not report_recipient_list:
                raise ValidationError('''Enabling notifications require to add
                                      at least one recipient to either error or
                                      report recipient lists''')
            self.set_notifications(notifications_settings)

    # notification settings
    def set_notifications(self, notification_settings):
        self.config['notifications'] = notification_settings

        return self.config

    def validate_execution_settings(self, execution_settings):
        event_occurrence = execution_settings.get('event_occurrence')
        execute_at = execution_settings.get('execute_at')
        custom_datetime_settings = execution_settings.get(
            'custom_datetime_settings')
        """
        If event occurrence contains a predefined type like daily, weekly, etc
        the execution settings payload must contain "execute_at" field with
        a list of times with HH:MM:SS format
        """
        if event_occurrence in PREDEFINED_OCCURRENCE_TYPES:
            if not execute_at:
                raise ValidationError(
                    '''When choosing a predefined event occurrence
                    you must set at least one time in HH:MM:SS''')

        elif event_occurrence == CUSTOM_OCCURENCE_TYPE:
            """
            if event occurence is custom we make sure the
            payload contains date and time settings
            """
            if not custom_datetime_settings:
                raise ValidationError('''A custom execution settings
                                      requires a "custom_datetime_settings"''')

            for custom_setting in custom_datetime_settings:
                day = custom_setting.get('day')
                time_list = custom_setting.get('execute_at')

                if not day or not time_list:
                    raise ValidationError('''A custom execution settings
                                          requires a "day" and "time" lists''')

        self.set_execution_settings(execution_settings)

    # execution settings
    def set_execution_settings(self, execution_settings):
        self.config['execution_settings'] = execution_settings
        return self.config

    def validate_pipeline(self, pipeline_settings):
        pipeline = PipelineSettings(pipeline_settings)
        pipeline.validate()
        self.set_pipeline(pipeline_settings)

    # pipeline definition
    def set_pipeline(self, pipeline_settings):
        self.config['pipeline'] = pipeline_settings

    def save(self):
        if not self.config_id:
            self.repository.create(self.config)
        else:
            self.repository.update_by_id(self.config_id, self.config)

    def get_config_list(self, filter={}):
        return list(self.repository.find(filter))
