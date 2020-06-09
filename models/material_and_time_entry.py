from odoo import models, fields, api, _


class timesheet_entry(models.Model):
    _name = 'cwl.module.timesheet.approval'
    _rec_name = 'time_entry_id'

    time_entry_id = fields.Char(string='Near Miss ID', readonly=True, required=True, copy=False, index=True,
                              default=lambda self: _('New'))
    employee_id = fields.Many2one('hr.employee', 'Employee')
    date = fields.Date('Date')
    project_id = fields.Many2one('project.project', 'Project')
    task_id = fields.Many2one('project.task', 'Task')
    category_timesheet = fields.Selection(
        [('reg', 'Regular'), ('regot', 'Regular OT'), ('port', 'Portable'), ('portot', 'Portable OT'),
         ('stat', 'Stat Holiday'), ('vacnopay', 'Vacation Not Paid'), ('safe', 'Safety'), ('other', 'Other')],
        'Timesheet Category')
    description = fields.Text('Description')
    duration = fields.Char("Duration (In Hour's)")
    state = fields.Selection([('pending', 'Pending'), ('approved', 'Approved')], 'State')

    @api.model
    def create(self, vals):
        if vals.get('time_entry_id', _('New')) == _('New'):
            vals['time_entry_id'] = self.env['ir.sequence'].next_by_code('Time_Entry_ID') or _('New')
        result = super(timesheet_entry, self).create(vals)
        return result
