def validate_age(age, messages):
    age = int(age)
    if age <= 0:
        messages.append(("danger", "Age must be positive."))
    elif age < 1 or age > 120:
        messages.append(("danger", "Age must be between 1 and 120."))

    return age, messages

def validate_gender(gender, messages):
    genders = ['male', 'female', 'other']

    if not gender:
        messages.append(("danger", "Gender is required."))
    else:
        if gender.lower() not in genders:
            messages.append(("danger", "Invalid gender. Choose 'Male', 'Female', or 'Other'."))
    
    return messages

def validate_weight(weight, messages):
    weight = float(weight)
    if weight <= 0:
        messages.append(("danger", "Weight must be positive."))
    
    return weight, messages

def validate_height(height, messages):
    height = float(height)
    if height <= 0:
        messages.append(("danger", "Height must be positive."))
    
    return height, messages

def validate_activity_type(activity_type, messages):
    activities_type = ['running', 'cycling', 'swimming', 'yoga', 'step', 'combat', 'bodybuilding']
    
    if not activity_type:
        messages.append(("danger", "Activity Type is required."))
    else:
        if activity_type.lower() not in activities_type:
            messages.append(("danger", "Invalid activity type. Choose one of the options provided."))

    return messages

def validate_duration(duration, messages):
    duration = int(duration)
    if duration <= 0:
        messages.append(("danger", "Duration must be positive."))
    
    return duration, messages

def validate_intensity(intensity, messages):
    intensities = ['low', 'moderate', 'high']

    if not intensity:
        messages.append(("danger", "Intensity is required."))
    else:
        if intensity.lower() not in intensities:
            messages.append(("danger", "Invalid intensity. Choose one of the options provided."))
    
    return messages

def validate_resting_heart_rate(resting_heart_rate, messages):
    resting_heart_rate = int(resting_heart_rate)
    if resting_heart_rate <= 0:
        messages.append(("danger", "Resting Heart Rate must be positive."))
    elif resting_heart_rate < 30 or resting_heart_rate > 120:
        messages.append(("danger", "Age must be between 30 and 120."))
    
    return resting_heart_rate, messages

def validate_exercise_heart_rate(exercise_heart_rate, messages):
    exercise_heart_rate = int(exercise_heart_rate)
    if exercise_heart_rate <= 0:
        messages.append(("danger", "Exercise Heart Rate must be positive."))
    elif exercise_heart_rate < 50 or exercise_heart_rate > 220:
        messages.append(("danger", "Age must be between 50 and 220."))
    
    return exercise_heart_rate, messages

def validate_body_fat_percentage(body_fat_percentage, messages):
    body_fat_percentage = float(body_fat_percentage)
    if body_fat_percentage <= 0:
        messages.append(("danger", "Body Fat Percentage must be positive."))
    return body_fat_percentage, messages

def validate_muscle_mass(muscle_mass, messages):
    muscle_mass = float(muscle_mass)
    if muscle_mass <= 0:
            messages.append(("danger", "Muscle Mass must be positive."))
    
    return muscle_mass, messages

def validate_water_intake(water_intake, messages):
    water_intake = float(water_intake)
    if water_intake <= 0:
        messages.append(("danger", "Water Intake must be positive."))
    
    return water_intake, messages