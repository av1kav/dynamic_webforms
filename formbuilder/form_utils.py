import yaml
import pandas as pd
import numpy as np
import os
from pprint import pprint
from bs4 import BeautifulSoup as soup

def prettify_raw_html(html_string, engine='bs4'):
    if engine == 'bs4':
        return soup(html_string, features='html.parser').prettify()

def generate_html_for_field(field):
    field_type = field.pop('field_type')
    modifier_keys = {
        'field_required': 'required' if field['required'] == 'Yes' else '',
        'field_required_style': 'required-field' if field['required'] == 'Yes' else '',
        'col_size_modifier': 'col-md-6' if field.get('group_id') else ''
    }   
    if field_type == 'input':    
        input_field_template = \
        """<div class="{col_size_modifier} mb-3">
            <label for="{backend_field_name}" class="form-label {field_required_style}">{field_label}</label>
            <input type="text" class="form-control" id="{backend_field_name}" name="{backend_field_name}" {field_required}>
        </div>"""
        return input_field_template.format(**{**modifier_keys, **field})
    elif field_type == 'select':
        option_list = '\n'.join([f"<option value=\"{option.strip()}\">{option.strip()}</option>" for option in field['select_options'].split(',')])
        select_field_template = \
        """<div class="{col_size_modifier} mb-3">
            <label for="{backend_field_name}" class="form-label {field_required_style}">{field_label}</label>
            <select class="form-select" id="{backend_field_name}" name="{backend_field_name}" {field_required}>
                {option_list}
            </select>
        </div>"""
        return select_field_template.format(**{'option_list': option_list, **modifier_keys, **field})
    elif field_type == 'text':
        text_field_template = \
        """<div class="{col_size_modifier} mb-3">
            <label for="{backend_field_name}" class="form-label {field_required_style}">{field_label}</label>
            <input type="text" class="form-control" id="{backend_field_name}" name="{backend_field_name}" {field_required}>
        </div>"""
        return text_field_template.format(**{**modifier_keys, **field})
    else:
        print(f"Unknown field type '{field_type}' for field '{field['backend_field_name']}'")
        return ''

def generate_html_for_page(page_number, page_config, field_html):
    page_template = \
    """<div class="form-page" id="page{page_number}">
            <h4 class="mt-4" aria-level="2">{page_title}</h4>
            <p class="text-muted">{page_description}</p>
            {field_html}
       </div>"""
    return page_template.format(**{
        'page_number': page_number,
        'field_html': field_html,
        **page_config
        }
    )

def generate_html_for_input_group_start():
    return "<div class=\"row\">"

def generate_html_for_input_group_end():
    return "</div>"

def generate_form_html_from_config_file(config_folder='formbuilder',config_filename='wny_config.xlsx'):
    config_filepath = os.path.join(config_folder, config_filename) if config_folder else config_filename
    config_workbook = pd.ExcelFile(config_filepath)
    form_pages = pd.read_excel(config_workbook, 'Pages').set_index('page_number').to_dict(orient='index')
    form_fields = pd.read_excel(config_workbook, 'Fields')
    generated_form_html = """"""
    for page_number, page_config in form_pages.items():
        # Step 1: Generate HTML for fields inside the page
        generated_field_html = """"""
        # Select subset of data that is associated with the current page, clean up missing group_id values and build a dictionary
        page_fields = form_fields.loc[form_fields['page_number'] == page_number].replace({np.nan:None}).to_dict(orient='records')
        current_group_id = None
        for i, field in enumerate(page_fields):
            if not field['group_id']:
                generated_field_html += generate_html_for_field(field)
            else:
                if current_group_id is None:
                    # First group on the page, so don't end any previous group
                    generated_field_html += generate_html_for_input_group_start()
                elif field['group_id'] != current_group_id:
                    # Non-first group on the page, so end the previous group and start a new one
                    generated_field_html += generate_html_for_input_group_end()
                    generated_field_html += generate_html_for_input_group_start()
                generated_field_html += generate_html_for_field(field)
                current_group_id = field['group_id']
        if current_group_id:
            # If at least 1 group has been created, the last group will need to be closed.
            generated_field_html += generate_html_for_input_group_end()
        # Step 2: Generate HTML for the page using the generated field HTML and page_config information
        generated_page_html = generate_html_for_page(page_number, page_config, generated_field_html)
        # Step 3: Append the generated page HTML to the final form HTML
        generated_form_html += generated_page_html
    # Step 4: Prettify and return the final form content HTML (pages and fields only)
    return prettify_raw_html(generated_form_html)