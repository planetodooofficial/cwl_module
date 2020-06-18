from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError


class timesheet_entry(models.Model):
    _name = 'cwl.module.timesheet.approval'
    _rec_name = 'time_entry_id'

    time_entry_id = fields.Char(string='Time Entry ID', readonly=True, required=True, copy=False, index=True,
                                default=lambda self: _('New'))
    employee_id = fields.Many2one('res.users', 'Employee', default=lambda self: self.env.user.id, readonly=True)
    date = fields.Date('Date', default=fields.Date.today, readonly=True)
    project_id = fields.Many2one('project.project', 'Project')
    task_id = fields.Many2one('project.task', 'Project Task')
    category_timesheet = fields.Selection(
        [('reg', 'Regular'), ('regot', 'Regular OT'), ('port', 'Portable'), ('portot', 'Portable OT'),
         ('stat', 'Stat Holiday'), ('vacnopay', 'Vacation Not Paid'), ('safe', 'Safety'), ('other', 'Other')],
        'Timesheet Category')
    description = fields.Text('Description')
    duration = fields.Float("Duration (Hours)")
    status = fields.Selection([('pending', 'Pending'), ('approved', 'Approved')], default='pending')

    @api.model
    def create(self, vals):
        if vals.get('time_entry_id', _('New')) == _('New'):
            vals['time_entry_id'] = self.env['ir.sequence'].next_by_code('Time_Entry_ID') or _('New')
        result = super(timesheet_entry, self).create(vals)
        return result

    def approve_timesheet(self):
        if self.status == 'pending':
            employee = self.env['hr.employee'].search([('user_id', '=', self.employee_id.id)])
            time_sheet = self.env['account.analytic.line'].create({
                'employee_id': employee.id,
                'date': self.date,
                'name': self.description,
                'project_id': self.project_id.id,
                'task_id': self.task_id.id,
                'unit_amount': float(self.duration)
            })
            if time_sheet:
                self.update({
                    'status': 'approved'
                })
        else:
            raise ValidationError(_("Time Entry has already been approved and processed."))


class Material_Entry(models.Model):
    _name = 'cwl.module.material.approval'
    _rec_name = 'material_entry_id'

    material_entry_id = fields.Char(string='Material Entry ID', readonly=True, required=True, copy=False, index=True,
                                    default=lambda self: _('New'))
    date = fields.Date('Date', default=fields.Date.today, readonly=True)
    employee_id = fields.Many2one('res.users', 'Employee', default=lambda self: self.env.user.id, readonly=True)
    project_id = fields.Many2one('project.project', 'Project')
    task_id = fields.Many2one('project.task', 'Project Task')
    product_id = fields.Many2one('product.template', 'Material')
    lot_id = fields.Many2one('stock.production.lot', 'Lots/Serial Numbers')
    qty = fields.Float('Quantity Used')
    status = fields.Selection([('pending', 'Pending'), ('approved', 'Approved')], default='pending')

    @api.model
    def create(self, vals):
        if vals.get('material_entry_id', _('New')) == _('New'):
            vals['material_entry_id'] = self.env['ir.sequence'].next_by_code('Material_Entry_ID') or _('New')
        result = super(Material_Entry, self).create(vals)
        return result
