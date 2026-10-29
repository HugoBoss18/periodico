# cuentas/views.py
from django.urls import reverse_lazy
from django.views.generic import CreateView

from .forms import FormularioCreacionUsuario


class VistaRegistro(CreateView):
    form_class = FormularioCreacionUsuario
    success_url = reverse_lazy("login")
    template_name = "registration/registro.html"