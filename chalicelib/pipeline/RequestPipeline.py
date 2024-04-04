import re
from ..Exceptions import ValidationError
from ..const import ALLOWED_HTTP_METHODS, SUPPORTED_REQUEST_ENCODINGS, \
    SUPPORTED_AUTH_TYPES, SUPPORTED_FIELD_SOURCES, STATIC_TOKEN_TYPE, \
    PREV_PIPELINE_RESP


class RequestPipeline:
    def __init__(self, request_params):
        if not request_params:
            raise ValidationError('Missing meta key "request_params"')
        self.params = request_params

    def validate_method(self, method):
        if not method or method not in ALLOWED_HTTP_METHODS:
            raise ValidationError('Invalid http method')

    def validate_encoding(self, encoding):
        if not encoding or encoding not in SUPPORTED_REQUEST_ENCODINGS:
            raise ValidationError('Invalid request encoding')

    def validate_authorization(self, auth_settings):
        authorization_type = auth_settings.get('type')
        host = auth_settings.get('host')
        credentials = auth_settings.get('credentials')
        token_type = auth_settings.get('token_type')
        token_value = auth_settings.get('token_value')

        if authorization_type == STATIC_TOKEN_TYPE and not token_value:
            raise ValidationError('''Static token authorization
                                    requires a "token_value" field''')

        if authorization_type in SUPPORTED_AUTH_TYPES:
            if not host:
                raise ValidationError('Missing "host" attribute')
            if not token_type:
                raise ValidationError('Missing "token_type" attribute')
            if not credentials:
                raise ValidationError('Missing "credentials" attribute')

    def validate_headers(self, headers):
        if not headers:
            raise ValidationError('Missing "headers" attribute')

        if not isinstance(headers, dict):
            raise ValidationError(
                'Invalid type, "headers" field must be a JSON object')

        for header_value in list(headers.values()):
            # check if header value contains headers
            variables = re.findall("{[\\w]+}", header_value, re.IGNORECASE)
            for variable in variables:
                variable = re.sub(r'[^\w]', '', variable)
                if variable not in ["token_value"]:
                    raise ValidationError(
                        f'Unsupported header variable {variable}')

    def validate_body(self, body):
        for body_field in body:
            field_source = body_field.get('field_source')
            field_path = body_field.get('field_path')
            field_value = body_field.get('field_value')

            if field_source and field_source not in SUPPORTED_FIELD_SOURCES:
                raise ValidationError('Unsupported "field_source" value.')

            if field_source == PREV_PIPELINE_RESP:
                if not field_path:
                    raise ValidationError(
                        '''In order to use a previous pipeline
                        result you must provide a valid path
                        to the response field''')

            if not field_source and not field_value:
                raise ValidationError(
                    '''If a field source is not specified,
                    you must provide a "field_value" field''')

    def validate_pagination(self, pagination):
        if not pagination.get('enabled'):
            return

        options = pagination.get('options')
        if not options:
            raise ValidationError(
                'If you enable pagination you must provide a set of "options"')

        pagination_strategy = options.get('strategy')
        if not pagination_strategy:
            raise ValidationError(
                'To enable pagination you must provide a valid strategy')

        meta = options.get('meta')
        if not meta:
            raise ValidationError(
                'To enable pagination you must provide valid "meta" fields')

        if pagination_strategy == 'page':
            page_count_keyword = meta.get('page_count_keyword')
            current_page_keyword = meta.get('current_page_keyword')

            if not page_count_keyword or not current_page_keyword:
                raise ValidationError('''"page" pagination strategy requires
                    "page_count_keyword" and "current_page_keyword" attrs''')

            query_parameters = options.get('query_parameters')
            if not query_parameters:
                raise ValidationError('''"page" pagination strategy
                    requires a "query_parameters" attribute''')

            page_param = query_parameters.get('page_param')
            if not page_param:
                raise ValidationError('''"page" pagination strategy
                    requires a "query_parameters.page_param" attribute''')

    def validate_aggregation(self, aggr):
        response_path = aggr.get('response_path')
        response_fields = aggr.get('fields')
        if not response_path:
            raise ValidationError(
                'Missing aggregations "response_path" attribute')

        if not response_fields:
            raise ValidationError(
                'Missing aggregations "fields" attribute')

        for response_field in response_fields:
            if not response_field.get('field_name'):
                raise ValidationError(
                    'Missing "field_name" attribute in "fields" list')

            transformation = response_field.get('transformation')
            target_field_name = response_field.get('target_field_name')

            if transformation and not target_field_name:
                raise ValidationError(
                    'Missing "target_field_name" attribute in "fields" list')

    def validate_aggregations(self, aggregations):
        for aggr in aggregations:
            self.validate_aggregation(aggr)

    def validate(self):
        if not self.params.get('url'):
            raise ValidationError('Invalid request URL')

        self.validate_method(self.params.get('method'))

        self.validate_encoding(self.params.get('encoding'))

        self.validate_authorization(self.params.get('authorization'))

        self.validate_headers(self.params.get('headers'))

        self.validate_body(self.params.get('body'))

        response = self.params.get('response')

        self.validate_pagination(response.get('pagination'))

        self.validate_aggregations(response.get('aggregations', []))
