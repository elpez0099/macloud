import re
from .EmailValidator import EmailAddressValidator
from .TimeValidator import Time24HrsValidator
from ..lib.DictDotNotation import ItemAccessor


class PayloadValidator:
    @staticmethod
    def get_validator(validation_pattern):
        validator_map = {
            "email": EmailAddressValidator,
            "24_hour_time": Time24HrsValidator
        }
        return validator_map.get(validation_pattern)

    @staticmethod
    def get_type(type_str):
        type_map = {
            "str": str,
            "dict": dict,
            "int": int,
            "list": list,
            "bool": bool
        }

        return type_map.get(type_str)

    @staticmethod
    def validate_payload_keys(schema, payload):
        # find allowed keys by schema
        allowed_fields = []
        for rule in schema.get('validation_rules'):
            allowed_fields.append(rule.get('name'))

        field_list = list(payload.keys())
        for field in field_list:
            if field not in allowed_fields:
                raise AttributeError(f'{field} field not supported.')

    @staticmethod
    def validate_field_type(field_type, field_name, field_value):
        # Validate field value type
        if field_type == 'any':
            return

        expected_type = PayloadValidator.get_type(field_type)
        valid_type = isinstance(field_value, expected_type)

        if field_value is not None and not valid_type:
            raise TypeError(
                f'{field_name} invalid value, expected {field_type}')

    @staticmethod
    def validate_restricted_values(field_name, field_value, restricted_values):
        # Validate field value in case there is a restricted list of values
        if restricted_values:
            restricted_values_str = ', '.join(restricted_values)

            if isinstance(field_value, str):
                if field_value not in restricted_values:
                    raise ValueError(f'''"{field_name}" invalid value,
                                possible values: {restricted_values_str}''')

            elif isinstance(field_value, list):
                for item_list in field_value:
                    PayloadValidator.validate_restricted_values(
                        field_name, item_list, restricted_values)

            else:
                raise TypeError(f'''Unable to validate field "{field_name}"
                    restricted values for non list or string values,
                    given {type(field_value)}''')

    @staticmethod
    def validate_field_variables(field_value, allowed_variables):
        # Validate if field value is allowed to contain variables
        if allowed_variables:
            if isinstance(field_value, str):
                # find variables in field value
                variables = re.findall("{[\\w]+}", field_value, re.IGNORECASE)

                # loop over variables found and check if those are allowed
                for variable in variables:
                    variable = re.sub(r'[^\w]', '', variable)
                    if variable not in allowed_variables:
                        raise ValueError(f'Unsupported Variable "{variable}"')

            elif isinstance(field_value, list):
                # loop over field value items
                for list_item in field_value:
                    PayloadValidator.validate_field_variables(
                        list_item, allowed_variables)
            else:
                raise TypeError('''Unable to validate variables
                                on non list or string values''')

    @staticmethod
    def validate_numeric_constraints(field_name, field_value,
                                     min_value, max_value):
        # Validate integer numbers in case the is a min/max value constraint
        if not isinstance(field_value, int):
            return

        if min_value:
            if field_value < min_value:
                raise ValueError(f'{field_name} minimum value is {min_value}')

        if max_value:
            if field_value > max_value:
                raise ValueError(f'{field_name} maximum value is {max_value}')

    @staticmethod
    def validate_upon_pattern(validation_pattern, field_value):
        # Validate string value for specific pattern
        if not validation_pattern:
            return

        if isinstance(field_value, str):
            # string field value
            validator = PayloadValidator.get_validator(validation_pattern)
            if not validator.is_valid(field_value):
                raise TypeError(f'Invalid {validation_pattern} format.')

        if isinstance(field_value, list):
            # list field value
            for list_item in field_value:
                PayloadValidator.validate_upon_pattern(
                    validation_pattern, list_item)

    @staticmethod
    def validate_upon_related_field(field_name, field_value,
                                    related_field, payload):
        # Validate field value depending on another field value
        if related_field is None:
            return

        field_path = related_field.get('field_path')
        expected_value = related_field.get('has_value')

        if '$.' in field_path:
            related_field = re.sub("\\$\\.", field_path)
            related_field_value = payload.get('related_field')
        else:
            path_nodes = ItemAccessor.decompose_path(field_path)
            related_field_value = ItemAccessor.get_node(payload, path_nodes)
            related_field = path_nodes[-1]

        if related_field_value == expected_value:
            if field_value is None:
                raise ValueError(f'''{field_name} is mandatory
                    when field {related_field} is {expected_value}''')

    @staticmethod
    def validate(schema, payload, current_node=None):
        full_payload = payload
        payload = current_node if current_node is not None else payload
        validation_rules = schema.get('validation_rules')

        # Validate payload keys
        PayloadValidator.validate_payload_keys(schema, payload)

        # Loop over validation rules
        for rule in validation_rules:
            # Get rule definitions
            rule_field_name = rule.get('name')
            rule_field_type = rule.get('type')
            skip_validation = rule.get('skip_validation')
            rule_field_required = rule.get('required')
            rule_restricted_field_values = rule.get('from_list')
            rule_field_allowed_variables = rule.get('allowed_variables')
            rule_field_min_int_value = rule.get('min_value')
            rule_field_max_int_value = rule.get('max_value')
            rule_field_validation_pattern = rule.get('validation_pattern')
            rule_field_validation_rules = rule.get('validation_rules')

            if skip_validation:
                continue

            # Get actual payload item
            field_value = payload.get(rule_field_name)

            # Validate field is required
            if field_value is None and rule_field_required:
                raise AttributeError(
                    f'Field not found, expected: "{rule_field_name}"')

            # Validate field value type
            PayloadValidator.validate_field_type(
                rule_field_type, rule_field_name, field_value)

            # In Case field type is dictionary and "validation_rules"
            # We use recurssion to step into the next nested node

            if rule_field_validation_rules and field_value is not None:
                if rule_field_type == 'dict':
                    PayloadValidator.validate(
                        rule, full_payload, current_node=field_value)

                if rule_field_type == 'list':
                    for node in field_value:
                        PayloadValidator.validate(
                            rule, full_payload, current_node=node)

            # Validate field value in case there is a restricted list of values
            if field_value is not None:
                PayloadValidator.validate_restricted_values(
                    rule_field_name, field_value, rule_restricted_field_values)

            # Validate if field value is allowed to contain variables
            PayloadValidator.validate_field_variables(
                field_value, rule_field_allowed_variables)

            # Validate int numbers in case the is a min/max value constraint
            PayloadValidator.validate_numeric_constraints(
                rule_field_name, field_value,
                rule_field_min_int_value, rule_field_max_int_value)

            # Validate string value for specific pattern
            PayloadValidator.validate_upon_pattern(
                rule_field_validation_pattern, field_value)
