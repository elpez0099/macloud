from ..utils.validators.PayloadValidator import PayloadValidator
from ..utils.lib.JsonReader import JsonReader
from ..VendorConfiguration import VendorConfiguration
from ..utils.encoders.JsonEncoder import JSONEncoder


class ConfigController:
    def __init__(self):
        pass

    def create_config(self, json_payload):
        # Open validation schema
        schema = JsonReader.read_from_file(
            'chalicelib/utils/validators/schemas/VendorConfigSchema.json')

        # Validate Json payload
        PayloadValidator.validate(schema, json_payload)

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
