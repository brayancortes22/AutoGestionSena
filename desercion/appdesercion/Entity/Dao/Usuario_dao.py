from django.db import connection
from appdesercion.Entity.Dao.base_dao import BaseDAO
from appdesercion.models import Usuario
from django.db.models import Q


class UsuarioDAO(BaseDAO):
    model=Usuario

    @staticmethod
    def obtener_usuario_por_correo(correo):

        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT U.Id AS usuario_id, 
                U.contrasena, 
                ur.rol_id_id AS rol_id,
                R.nombre AS nombre_rol
                FROM sena.Usuario AS U
                LEFT JOIN sena.UsuarioRol AS ur ON ur.usuario_id_id = U.Id
                LEFT JOIN sena.Rol AS R ON R.id = ur.rol_id_id
                WHERE U.correo = %s;
            """, [correo])
            columnas= [col[0] for col in cursor.description]
            resultados= [dict(zip(columnas, fila)) for fila in cursor.fetchall()]
        return resultados

    @staticmethod
    def list_usuarios_sin_rol():
        return Usuario.objects.filter(
            Q(usuariorol__isnull=True)
        ).select_related('tipoDocumento').values(
            'id', 'nombres', 'apellidos', 'correo', 'documento', 'tipoDocumento__nombre'
        )

    @staticmethod
    def obtener_datos(cls):
        return cls.model.objects.select_related('tipoDocumento').all()