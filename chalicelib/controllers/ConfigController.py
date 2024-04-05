from ..utils.validators.PayloadValidator import PayloadValidator
from ..utils.lib.JsonReader import JsonReader
from ..VendorConfiguration import VendorConfiguration
from ..utils.encoders.JsonEncoder import JSONEncoder


class ConfigController:
    def __init__(self):
        # Open validation schema
        self.schema = JsonReader.read_from_file(
            'chalicelib/utils/validators/schemas/VendorConfigSchema.json')

    def create_config(self, json_payload):
        # Validate Json payload
        PayloadValidator.validate(self.schema, json_payload)

        # 1) create vendor config instance for basic info (ok)
        vendor_config = VendorConfiguration(json_payload)
        vendor_config.save()

        # Pipeline validations here
        return JSONEncoder().encode(json_payload)

    def get_vendor_configuration_by_id(self, config_id):
        vendor_config = VendorConfiguration(config_id=config_id)
        return JSONEncoder().encode(vendor_config.get_configuration())

    def get_vendor_configuration_list(self):
        vendor_config = VendorConfiguration()
        return JSONEncoder().encode(vendor_config.get_config_list())

    def _set_validation_schema(self, attribute):
        found = False
        for rule in self.schema.get('validation_rules'):
            if rule.get('name') == attribute and rule.get('validation_rules'):
                self.schema = rule
                found = True
                break
        if not found:
            raise AttributeError(f'''attribute "{attribute}" could not be found
                                in given configuration.''')

    def update_config(self, config_id, json_payload, attribute=None):
        # if attribute is node it means it is a full update
        if attribute is not None:
            self._set_validation_schema(attribute)

        # Validate Json payload
        PayloadValidator.validate(self.schema, json_payload)
        vendor_config = VendorConfiguration(config_id=config_id)
        vendor_config.set_config_from_payload(json_payload, attribute=attribute)
        vendor_config.save()
