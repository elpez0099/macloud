from chalice import Chalice,  BadRequestError, Response
from chalicelib.controllers.ConfigController import ConfigController
from chalicelib.utils.encoders.ErrorFormatter import ErrorFormatter

app = Chalice(app_name='macloud-inventory')


@app.route('/api/v1/vendor/configuration', methods=['POST'])
def add_vendor_configuration():
    try:
        body = app.current_request.json_body
        controller = ConfigController()
        result = controller.create_config(body)
        return Response(result, status_code=201)
    except Exception as ex:
        raise BadRequestError(ErrorFormatter.prettify(str(ex)))

@app.route('/api/v1/vendor/configuration/{config_id}', methods=['GET'])
def get_vendor_configuration(config_id):
    controller = ConfigController()
    try:
        print(f'Config id: {config_id}')
        config = controller.get_vendor_configuration_by_id(config_id)
        return Response(config, status_code=200)
    except Exception as ex:
        return Response({'error': str(ex)}, status_code=500)


@app.route('/api/v1/vendor/configuration', methods=['GET'])
def get_vendor_configuration_list():
    controller = ConfigController()
    try:
        config_list = controller.get_vendor_configuration_list()
        return Response(config_list, status_code=200)
    except Exception as ex:
        return Response({'error': str(ex)}, status_code=500)
