from odoo import api, fields, models, _, tools
from odoo.exceptions import UserError, ValidationError
import logging
import requests
import json
import base64

_logger = logging.getLogger(__name__)


class Sites(models.Model):
    _name = 'save.sites'

    name = fields.Char('Site Name')
    site_id = fields.Char('Site ID')


class ManagingSites(models.TransientModel):
    _name = 'manage.sites'

    alf_site_name = fields.Char("Site Name")
    alf_site_description = fields.Char("Site Description")
    alf_site_visibility = fields.Selection([('PUBLIC', 'PUBLIC'), ('PRIVATE', 'PRIVATE'), ('MODERATED', 'MODERATED')],
                                           string="Site Visibility")
    alf_site_search = fields.Many2one('save.sites', string="Select Site")

    def create_site(self):
        """This function Creates an Alfresco Share site."""

        ticket = self.env['alfresco.operations'].search([], limit=1)

        base_url = 'https://afvdpi.trial.alfresco.com/alfresco/api/-default-/public/alfresco/versions/1/sites'

        datas = {
            "title": str(self.alf_site_name),
            "description": str(self.alf_site_description),
            "visibility": str(self.alf_site_visibility)
        }

        headers = {
            'Accept': 'application/json',
            'Content-Type': 'application/json',
            'Authorization': 'Basic' + " " + str(ticket.alf_encoded_ticket)
        }

        response = requests.post(base_url, data=json.dumps(datas), headers=headers)
        if response.status_code == 201:
            data = json.loads(response.text)
            self.env['save.sites'].create({'name': data['entry']['title'],
                                           'site_id': data['entry']['id']})

            wiz_ob = self.env['site'].create(
                {'pop_up': 'Your site' + " " + data['entry']['title'] + " " + 'has been created.'})
            return {
                'name': _('Alert'),
                'view_type': 'form',
                'view_mode': 'form',
                'res_model': 'site',
                'res_id': wiz_ob.id,
                'view_id': False,
                'target': 'new',
                'views': False,
                'type': 'ir.actions.act_window',
            }
        elif response.status_code == 401:
            wiz_ob = self.env['site'].create(
                {'pop_up': 'Authentication Failed.'})
            return {
                'name': _('Alert'),
                'view_type': 'form',
                'view_mode': 'form',
                'res_model': 'site',
                'res_id': wiz_ob.id,
                'view_id': False,
                'target': 'new',
                'views': False,
                'type': 'ir.actions.act_window',
            }
        elif response.status_code == 409:
            wiz_ob = self.env['site'].create(
                {'pop_up': 'Site with the given identifier already exists.'})
            return {
                'name': _('Alert'),
                'view_type': 'form',
                'view_mode': 'form',
                'res_model': 'site',
                'res_id': wiz_ob.id,
                'view_id': False,
                'target': 'new',
                'views': False,
                'type': 'ir.actions.act_window',
            }

    def update_site(self):
        """This function Updates the metadata for an Alfresco Share site."""

        ticket = self.env['alfresco.operations'].search([], limit=1)

        sites = self.env['save.sites'].search([('name', '=', self.alf_site_search.name)])

        headers = {
            'Accept': 'application/json',
            'Content-Type': 'application/json',
            'Authorization': 'Basic' + " " + str(ticket.alf_encoded_ticket)
        }

        datas = {
            "title": str(self.alf_site_name),
            "description": str(self.alf_site_description),
            "visibility": str(self.alf_site_visibility)
        }

        url = 'https://afvdpi.trial.alfresco.com/alfresco/api/-default-/public/alfresco/versions/1/sites/' + str(sites.site_id)

        response = requests.put(url, data=json.dumps(datas), headers=headers)
        data = json.loads(response.text)
        if response.status_code == 200:
            wiz_ob = self.env['site'].create(
                {'pop_up': 'Site with the given identifier updated successfully.'})
            return {
                'name': _('Alert'),
                'view_type': 'form',
                'view_mode': 'form',
                'res_model': 'site',
                'res_id': wiz_ob.id,
                'view_id': False,
                'target': 'new',
                'views': False,
                'type': 'ir.actions.act_window',
            }
        if response.status_code == 401:
            wiz_ob = self.env['site'].create(
                {'pop_up': 'Authentication failed.'})
            return {
                'name': _('Alert'),
                'view_type': 'form',
                'view_mode': 'form',
                'res_model': 'site',
                'res_id': wiz_ob.id,
                'view_id': False,
                'target': 'new',
                'views': False,
                'type': 'ir.actions.act_window',
            }
        if response.status_code == 404:
            wiz_ob = self.env['site'].create(
                {'pop_up': 'This siteId' + " " + str(data['entry']['id']) + " " + 'does not exist.'})
            return {
                'name': _('Alert'),
                'view_type': 'form',
                'view_mode': 'form',
                'res_model': 'site',
                'res_id': wiz_ob.id,
                'view_id': False,
                'target': 'new',
                'views': False,
                'type': 'ir.actions.act_window',
            }

    def add_content_to_site(self):
        """This function Creates folders and add files to an Alfresco Share site's Document Library."""

        list_of_id = []

        ticket = self.env['alfresco.operations'].search([], limit=1)

        base_url = 'https://afvdpi.trial.alfresco.com/alfresco/api/-default-/public/alfresco/versions/1/sites/'

        headers = {
            'Accept': 'application/json',
            'Content-Type': 'application/json',
            'Authorization': 'Basic' + " " + str(ticket.alf_encoded_ticket)
        }

        response_get_id = requests.get(base_url, headers=headers)
        text_id = json.loads(response_get_id.text)
        get_id = text_id['list']['entries']
        for rec in get_id:
            list_of_id.append(rec['entry']['id'])
        print(list_of_id)

        entry_url = 'http://localhost:8080/alfresco/api/-default-/public/alfresco/versions/1/sites/' + list_of_id[1] + \
                    '/containers/documentLibrary'

        response_entry = requests.get(entry_url, headers=headers)
        text_entry = json.loads(response_entry.text)
        get_folder_id = text_entry['entry']['id']

    def add_members_to_site(self):
        """This function add members to an Alfresco Share site."""
