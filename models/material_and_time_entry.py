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
    sale_id = fields.Many2one('sale.order', 'Project')
    status = fields.Selection([('pending', 'Pending'), ('approved', 'Approved')], default='pending')
    material_list_ids = fields.One2many('material.list', 'material_list_id', string='List of Materials')

    @api.model
    def create(self, vals):
        if vals.get('material_entry_id', _('New')) == _('New'):
            vals['material_entry_id'] = self.env['ir.sequence'].next_by_code('Material_Entry_ID') or _('New')
        result = super(Material_Entry, self).create(vals)
        return result

    def approve_material(self):
        if self.status == 'pending':
            sale_order = self.env['sale.order'].search([('id', '=', self.sale_id.id)])
            for rec in self.material_list_ids:
                product = self.env['product.product'].search([('name', '=', rec.product_id.name)])
                sale_order_line = self.env['sale.order.line'].create({
                    'product_id': product.id,
                    'name': product.description if product.description else product.name,
                    'product_uom': product.uom_id.id,
                    'product_uom_qty': rec.qty,
                    'price_unit': product.list_price,
                    'order_id': sale_order.id
                })
            sale_order.action_confirm()

            picking = self.env['stock.picking'].search([('origin', '=', sale_order.name)])
            for record in self.material_list_ids:
                for rec in picking.move_ids_without_package:
                    if record.product_id.name == rec.name:
                        rec.update({
                            'quantity_done': record.qty
                        })
            picking.button_validate()

            self.update({
                'status': 'approved'
            })


class ProductOne2many(models.Model):
    _name = 'material.list'

    material_list_id = fields.Many2one('cwl.module.material.approval', 'Material List ID')
    product_id = fields.Many2one('product.template', string='Material')
    lot_id = fields.Many2one('stock.production.lot', string='Lots/Serial Numbers')
    qty = fields.Float('Quantity Used')


class SaleOrderInherit(models.Model):
    _inherit = 'sale.order.line'

    lot_id = fields.Many2one('stock.production.lot', string='Lots/Serial Numbers')
