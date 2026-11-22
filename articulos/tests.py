# articulos/tests.py
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from .models import Articulo, Comentario


class PruebasArticulos(TestCase):
    @classmethod
    def setUpTestData(cls):
        Usuario = get_user_model()
        cls.autora = Usuario.objects.create_user(
            username="autora", email="autora@ejemplo.mx", password="Clave-segura-2026"
        )
        cls.otro = Usuario.objects.create_user(
            username="otro", email="otro@ejemplo.mx", password="Clave-segura-2026"
        )
        cls.articulo = Articulo.objects.create(
            titulo="Un buen título", cuerpo="Texto del artículo.", autor=cls.autora
        )

    def test_modelo(self):
        self.assertEqual(str(self.articulo), "Un buen título")
        self.assertEqual(
            self.articulo.get_absolute_url(), f"/articulos/{self.articulo.pk}/"
        )

    def test_lista_publica(self):
        respuesta = self.client.get(reverse("articulo_lista"))
        self.assertEqual(respuesta.status_code, 200)
        self.assertTemplateUsed(respuesta, "articulos/lista.html")
        self.assertContains(respuesta, "Un buen título")

    def test_detalle_publico(self):
        respuesta = self.client.get(self.articulo.get_absolute_url())
        self.assertEqual(respuesta.status_code, 200)
        self.assertContains(respuesta, "Texto del artículo.")
        self.assertNotContains(respuesta, "Editar")

    def test_crear_requiere_sesion(self):
        respuesta = self.client.get(reverse("articulo_nuevo"))
        self.assertRedirects(
            respuesta, f"{reverse('login')}?next={reverse('articulo_nuevo')}"
        )

    def test_crear_asigna_autor(self):
        self.client.force_login(self.otro)
        respuesta = self.client.post(
            reverse("articulo_nuevo"), {"titulo": "Nuevo", "cuerpo": "Hola."}
        )
        nuevo = Articulo.objects.get(titulo="Nuevo")
        self.assertRedirects(respuesta, nuevo.get_absolute_url())
        self.assertEqual(nuevo.autor, self.otro)

    def test_autor_puede_editar(self):
        self.client.force_login(self.autora)
        respuesta = self.client.post(
            reverse("articulo_editar", args=[self.articulo.pk]),
            {"titulo": "Título corregido", "cuerpo": "Texto del artículo."},
        )
        self.assertRedirects(respuesta, self.articulo.get_absolute_url())
        self.articulo.refresh_from_db()
        self.assertEqual(self.articulo.titulo, "Título corregido")

    def test_otro_usuario_no_puede_editar(self):
        self.client.force_login(self.otro)
        respuesta = self.client.get(reverse("articulo_editar", args=[self.articulo.pk]))
        self.assertEqual(respuesta.status_code, 403)

    def test_otro_usuario_no_puede_eliminar(self):
        self.client.force_login(self.otro)
        respuesta = self.client.post(
            reverse("articulo_eliminar", args=[self.articulo.pk])
        )
        self.assertEqual(respuesta.status_code, 403)
        self.assertTrue(Articulo.objects.filter(pk=self.articulo.pk).exists())

    def test_autor_puede_eliminar(self):
        self.client.force_login(self.autora)
        respuesta = self.client.post(
            reverse("articulo_eliminar", args=[self.articulo.pk])
        )
        self.assertRedirects(respuesta, reverse("articulo_lista"))
        self.assertFalse(Articulo.objects.filter(pk=self.articulo.pk).exists())

    def test_usuario_staff_puede_editar_cualquier_articulo(self):
        Usuario = get_user_model()
        editor = Usuario.objects.create_user(
            username="editor",
            email="editor@ejemplo.mx",
            password="Clave-segura-2026",
            is_staff=True,
        )
        self.client.force_login(editor)

        respuesta = self.client.post(
            reverse("articulo_editar", args=[self.articulo.pk]),
            {"titulo": "Editado por el editor", "cuerpo": "Texto corregido."},
        )

        self.assertRedirects(respuesta, self.articulo.get_absolute_url())
        self.articulo.refresh_from_db()
        self.assertEqual(self.articulo.titulo, "Editado por el editor")

    def test_usuario_staff_puede_eliminar_cualquier_articulo(self):
        Usuario = get_user_model()
        editor = Usuario.objects.create_user(
            username="editor",
            email="editor@ejemplo.mx",
            password="Clave-segura-2026",
            is_staff=True,
        )
        self.client.force_login(editor)

        respuesta = self.client.post(
            reverse("articulo_eliminar", args=[self.articulo.pk])
        )

        self.assertRedirects(respuesta, reverse("articulo_lista"))
        self.assertFalse(Articulo.objects.filter(pk=self.articulo.pk).exists())

    def test_mis_articulos_requiere_sesion(self):
        respuesta = self.client.get(reverse("articulo_mios"))
        self.assertRedirects(
            respuesta, f"{reverse('login')}?next={reverse('articulo_mios')}"
        )

    def test_mis_articulos_muestra_solo_articulos_del_usuario(self):
        Articulo.objects.create(
            titulo="Artículo ajeno",
            cuerpo="Texto ajeno.",
            autor=self.otro,
        )
        self.client.force_login(self.autora)

        respuesta = self.client.get(reverse("articulo_mios"))

        self.assertEqual(respuesta.status_code, 200)
        self.assertContains(respuesta, "Un buen título")
        self.assertNotContains(respuesta, "Artículo ajeno")

    def test_detalle_muestra_formulario_de_comentario(self):
        self.client.force_login(self.otro)
        respuesta = self.client.get(self.articulo.get_absolute_url())
        self.assertContains(respuesta, "Comentarios (0)")
        self.assertContains(respuesta, "Comentar")

    def test_usuario_puede_comentar_articulo(self):
        self.client.force_login(self.otro)
        respuesta = self.client.post(
            reverse("articulo_comentar", args=[self.articulo.pk]),
            {"comentario": "Excelente artículo."},
        )
        self.assertRedirects(respuesta, self.articulo.get_absolute_url())
        comentario = Comentario.objects.get()
        self.assertEqual(comentario.articulo, self.articulo)
        self.assertEqual(comentario.autor, self.otro)
        self.assertEqual(comentario.comentario, "Excelente artículo.")

    def test_comentar_requiere_sesion(self):
        respuesta = self.client.post(
            reverse("articulo_comentar", args=[self.articulo.pk]),
            {"comentario": "Sin sesión."},
        )
        self.assertRedirects(
            respuesta,
            f"{reverse('login')}?next={reverse('articulo_comentar', args=[self.articulo.pk])}",
        )


class PruebasComentarios(TestCase):
    @classmethod
    def setUpTestData(cls):
        Usuario = get_user_model()
        cls.autora = Usuario.objects.create_user(
            username="autora",
            email="autora@ejemplo.mx",
            password="Clave-segura-2026",
        )
        cls.lector = Usuario.objects.create_user(
            username="lector",
            email="lector@ejemplo.mx",
            password="Clave-segura-2026",
        )
        cls.articulo = Articulo.objects.create(
            titulo="Un buen título",
            cuerpo="Texto del artículo.",
            autor=cls.autora,
        )
        cls.comentario = Comentario.objects.create(
            articulo=cls.articulo,
            comentario="Muy interesante.",
            autor=cls.lector,
        )
        cls.url_comentar = reverse("articulo_comentar", args=[cls.articulo.pk])

    def test_modelo(self):
        self.assertEqual(str(self.comentario), "Muy interesante.")
        self.assertEqual(self.articulo.comentarios.count(), 1)

    def test_detalle_muestra_comentarios(self):
        respuesta = self.client.get(self.articulo.get_absolute_url())
        self.assertContains(respuesta, "Comentarios (1)")
        self.assertContains(respuesta, "Muy interesante.")
        self.assertContains(respuesta, "Inicia sesión")

    def test_comentar_requiere_sesion(self):
        respuesta = self.client.post(self.url_comentar, {"comentario": "Hola."})
        self.assertRedirects(respuesta, f"{reverse('login')}?next={self.url_comentar}")
        self.assertEqual(Comentario.objects.count(), 1)

    def test_comentar(self):
        self.client.force_login(self.autora)
        respuesta = self.client.post(self.url_comentar, {"comentario": "¡Gracias!"})
        self.assertRedirects(respuesta, self.articulo.get_absolute_url())
        nuevo = Comentario.objects.get(comentario="¡Gracias!")
        self.assertEqual(nuevo.autor, self.autora)
        self.assertEqual(nuevo.articulo, self.articulo)

    def test_comentario_vacio(self):
        self.client.force_login(self.autora)
        respuesta = self.client.post(self.url_comentar, {"comentario": ""})
        self.assertEqual(respuesta.status_code, 200)
        self.assertContains(respuesta, "Este campo es obligatorio")
        self.assertEqual(Comentario.objects.count(), 1)

    def test_comentar_solo_por_post(self):
        self.client.force_login(self.autora)
        respuesta = self.client.get(self.url_comentar)
        self.assertEqual(respuesta.status_code, 405)