from marshmallow import Schema, fields

class JobShiftSchema(Schema):
    id = fields.Int(dump_only=True)
    day_of_week = fields.Str()
    start_time = fields.Time()
    end_time = fields.Time()
    is_flexible = fields.Bool()

class JobSchema(Schema):
    id = fields.Int(dump_only=True)
    title = fields.Str()
    company_name = fields.Str()
    description = fields.Str()
    salary_min = fields.Float()
    salary_max = fields.Float()
    currency = fields.Str()
    salary_type = fields.Str()
    location = fields.Str()
    latitude = fields.Float()
    longitude = fields.Float()
    source = fields.Str()
    external_url = fields.Str()
    posted_at = fields.DateTime()
    is_active = fields.Bool()
    
    # Nested
    shifts = fields.List(fields.Nested(JobShiftSchema))
    match_score = fields.Float(dump_only=True) # Computed field
    match_analysis = fields.Dict(dump_only=True) # Computed field

class ApplicationSchema(Schema):
    id = fields.Int(dump_only=True)
    job_id = fields.Int()
    student_id = fields.Int()
    status = fields.Str()
    applied_at = fields.DateTime()
    job_title = fields.Str() # Flattened
    company = fields.Str() # Flattened

class ScheduleSlotSchema(Schema):
    id = fields.Int(dump_only=True)
    day_of_week = fields.Str(required=True)
    start_time = fields.Time(format='%H:%M', required=True) # Expect string input for PUT
    end_time = fields.Time(format='%H:%M', required=True)
    activity_type = fields.Str()
    location = fields.Str()
