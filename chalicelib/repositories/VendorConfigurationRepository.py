from .GenericRepository import GenericRepository


class VendorConfigurationRepository(GenericRepository):
    def __init__(self):
        super().__init__('VendorConfig')
