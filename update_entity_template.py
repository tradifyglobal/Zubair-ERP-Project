#!/usr/bin/env python3
"""Update Entity form template to include company_currency field"""

import sys

file_path = '/var/www/tradifyerp/accounting/templates/accounting/entity_form.html'

with open(file_path, 'r') as f:
    content = f.read()

# Find the Description section and insert company_currency field after it
old_section = '''                                <!-- Description -->
                                <div class="row mb-3">
                                    <label for="{{ form.description.id_for_label }}" class="col-md-3 col-form-label">
                                        Description
                                    </label>
                                    <div class="col-md-9">
                                        {{ form.description }}
                                        {% if form.description.errors %}
                                        <div class="invalid-feedback d-block">
                                            {{ form.description.errors.0 }}
                                        </div>
                                        {% endif %}
                                    </div>
                                </div>

                                <!-- Is Active -->'''

new_section = '''                                <!-- Description -->
                                <div class="row mb-3">
                                    <label for="{{ form.description.id_for_label }}" class="col-md-3 col-form-label">
                                        Description
                                    </label>
                                    <div class="col-md-9">
                                        {{ form.description }}
                                        {% if form.description.errors %}
                                        <div class="invalid-feedback d-block">
                                            {{ form.description.errors.0 }}
                                        </div>
                                        {% endif %}
                                    </div>
                                </div>

                                <!-- Base Currency -->
                                <div class="row mb-3">
                                    <label for="{{ form.company_currency.id_for_label }}" class="col-md-3 col-form-label">
                                        Base Currency <span class="text-danger">*</span>
                                    </label>
                                    <div class="col-md-9">
                                        {{ form.company_currency }}
                                        {% if form.company_currency.errors %}
                                        <div class="invalid-feedback d-block">
                                            {{ form.company_currency.errors.0 }}
                                        </div>
                                        {% endif %}
                                    </div>
                                </div>

                                <!-- Is Active -->'''

if old_section in content:
    content = content.replace(old_section, new_section)
    
    with open(file_path, 'w') as f:
        f.write(content)
    
    print(f"✓ Successfully updated {file_path}")
    print(f"  Added Base Currency field between Description and Is Active")
    sys.exit(0)
else:
    print(f"✗ Could not find template section in {file_path}")
    sys.exit(1)
