from odoo import models, fields

class CicloFormativo(models.Model):
    _name = 'instituto.ciclo'
    _description = 'Ciclo Formativo'
    
    name = fields.Char(string="Nombre del Ciclo", required=True)
    description = fields.Text(string="Descripción")
    modulo_ids = fields.One2many('instituto.modulo', 'ciclo_id', string="Módulos")

class ModuloFormativo(models.Model):
    _name = 'instituto.modulo'
    _description = 'Módulo Formativo'
    
    name = fields.Char(string="Nombre del Módulo", required=True)
    ciclo_id = fields.Many2one('instituto.ciclo', string="Ciclo Formativo")
    profesor_id = fields.Many2one('instituto.profesor', string="Profesor")
    alumno_ids = fields.Many2many('instituto.alumno', string="Alumnos Matriculados")

class Alumno(models.Model):
    _name = 'instituto.alumno'
    _description = 'Alumno'
    
    name = fields.Char(string="Nombre Alumno", required=True)
    modulo_ids = fields.Many2many('instituto.modulo', string="Módulos")

class Profesor(models.Model):
    _name = 'instituto.profesor'
    _description = 'Profesor'
    
    name = fields.Char(string="Nombre Profesor", required=True)
    modulo_ids = fields.One2many('instituto.modulo', 'profesor_id', string="Docencia")