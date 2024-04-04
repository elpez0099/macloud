from ..Exceptions import ValidationError
from .RequestPipeline import RequestPipeline


class PipelineSettings:
    prev_stage = None

    def __init__(self, pipeline_settings):
        if not isinstance(pipeline_settings, list):
            raise TypeError(
                'Invalid pipeline settings data type, expected list.')
        self.pipeline = pipeline_settings

    def validate_order(self):
        # Validate pipeline order
        taken = []
        for stage in self.pipeline:
            # Validate if there is an order attribute
            stage_order = stage.get('order')
            if not stage_order:
                ValidationError('Missing pipeline attribute "order"')

            if not isinstance(stage_order, int):
                ValidationError('"order" attribute must be an integer')

            if stage_order < 1 or stage_order > 15:
                ValidationError('"order" attribute must be between 1 and 15')

            if stage_order in taken:
                raise ValidationError(
                    '"order" attribute value already exists!')

            taken.append(stage_order)

    def reorder_pipeline(self):
        # reorder pipeline by order attribute
        self.pipeline = sorted(self.pipeline, key=lambda x: x['order'])

    def validate_batch_processing(self, batch_processing):
        batch_processing_enabled = batch_processing.get('enabled')
        batch_strategy = batch_processing.get('strategy')
        batch_size = batch_processing.get('batch_size')
        if batch_processing_enabled:
            if not batch_strategy:
                raise ValidationError('''When using batching processing
                    you must provide a "strategy" field''')

            if batch_strategy == 'custom_batch_size':
                if not batch_size or batch_size <= 0 or batch_size > 2000:
                    raise ValidationError('''For custom batch size you musy
                        provide a valid integer between 0 and 2000''')

    def validate_pipeline_request(self, request_params):
        request = RequestPipeline(request_params)
        request.validate()

    def validate(self):
        self.validate_order()
        self.reorder_pipeline()

        for i, stage in enumerate(self.pipeline):
            name = stage.get('name')
            type = stage.get('type')
            order = stage.get('order')
            meta = stage.get('meta')

            if not name or not type or not order or not meta:
                raise ValidationError('''Missing attributes for pipeline stage,
                    expected "name", "type", "order" and "meta"''')

            # Validate batching proceesing
            self.validate_batch_processing(meta.get('batch_processing'))

            # Validate pipeline stage type
            if type == "request":
                self.validate_pipeline_request(meta.get('request_params'))
            self.prev_stage = stage
