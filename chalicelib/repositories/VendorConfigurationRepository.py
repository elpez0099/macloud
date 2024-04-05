from bson import ObjectId
from .GenericRepository import GenericRepository


class VendorConfigurationRepository(GenericRepository):
    def __init__(self):
        super().__init__('VendorConfig')

    def update_by_id(self, id, body):
        self.update({'_id': ObjectId(id)}, body)
