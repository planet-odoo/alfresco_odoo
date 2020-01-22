# -*- coding: utf-8 -*-
{
    'name': 'Alfresco API',
    'version': '1.0',
    'summary': 'Alfresco Document Management System integration with Odoo',
    'category': 'API',
    'author': 'Planet-Odoo',
    'maintainer': 'Planet-Odoo',
    'company': 'Planet-Odoo',
    'website': '',
    'depends': ['base'],
    'data': [
        'security/ir.model.access.csv',
        'view/alfresco_operation_view.xml',
        'wizard/alfresco_files_folder_view.xml',
        'wizard/alfresco_site_view.xml',
        'wizard/pop_up_wizard_view.xml',
    ],
    'images': [],
    'license': 'AGPL-3',
    'installable': True,
    'application': False,
    'auto_install': False,
}
