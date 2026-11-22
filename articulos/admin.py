from django.contrib import admin
from .models import Articulo, Comentario

class ComentarioInline(admin.TabularInline):
    model = Comentario
    extra = 0


# Register your models here.
@admin.register(Articulo)
class ArticuloAdmin(admin.ModelAdmin):
    list_display = ('titulo', 'autor', 'fecha')
    search_fields = ("titulo", "cuerpo", "autor__username")
    list_filter = ('fecha', 'autor')
    inlines = [ComentarioInline]