from dataclasses import asdict

from drf_yasg import openapi
from rest_framework.decorators import action
from rest_framework import viewsets
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from rest_framework.response import Response
from rest_framework import status
from drf_yasg.utils import swagger_auto_schema
from django.utils import timezone  # ✅ Importar timezone correctamente
from yaml import serialize

from appdesercion.Business.comentario_service import ComentarioService
from appdesercion.Business.cuestionario_service import CuestionarioService
from appdesercion.Business.instructor.list_trainees_service import ListTraineesService
from appdesercion.Business.instructor.process_instructor_service import ProcessInstructorService
from appdesercion.Business.pregunta_service import PreguntaService
from appdesercion.Business.proceso_service import ProcesoService
from appdesercion.Business.recuperarContrasena_service import RecuperarContrasenaService
from appdesercion.Business.respuestas_service import RespuestasService
from appdesercion.Business.rolVista_service import RolVistaService
from appdesercion.Business.usuario_service import UsuarioService
from appdesercion.Entity.Dao.aprendiz_dao import AprendizDAO
from appdesercion.Entity.Dao.rolvista_dao import RolVistaDAO
from appdesercion.Entity.Dao.vista_dao import VistaDAO
from appdesercion.models import Cuestionario, Deserciones, Modulo, Proceso, RecuperarContrasena, Respuesta, Rol, \
    RolVista, Usuario, UsuarioRol, Vista, Aprendiz, Comentario, Pregunta, TipoDocumento  # ✅ Importar solo lo necesario
from appdesercion.Apis.serializers.serializer import CuestionarioSerializers, DesercionesSerializer, \
    EnviarCodigoSerializer, ModuloSerializer, ProcesoSerializer, RecuperarContrasenaSerializer, \
    RespuestasSerializer, RolSerializer, RolVistaSerializer, UsuarioLoginSerializer, UsuarioRolSerializer, \
    UsuarioSerializer, VerificarCodigoSerializer, VistaSerializer, AprendizSerializer, \
    ComentarioSerializer, PreguntaSerializer, TipoDocumentoSerializer, \
    ConsultarDocumentoSerializer, ListTraineesSerializer, ProcessInstructorSerializer  # ✅ Importar explícitamente

class ModuloViewSet(viewsets.ModelViewSet):  # ✅ Cambiado ModelViewSet en VistaViewSet
    queryset = Modulo.objects.filter(fechaElimino__isnull=True)  # Filtra solo los activos
    serializer_class = ModuloSerializer

    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs, partial=True)
    
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.fechaElimino = timezone.now()
        instance.save()
        return Response({"message": "Módulo eliminado correctamente"}, status=status.HTTP_204_NO_CONTENT)

class VistaViewSet(viewsets.ModelViewSet):  # ✅ Cambiado ModelViewSet
    queryset = Vista.objects.filter(fechaElimino__isnull=True)
    serializer_class = VistaSerializer

    def get_queryset(self):
        return VistaDAO.obtener_datos()

    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs, partial=True)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.fechaElimino = timezone.now()
        instance.save()
        return Response({"message": "Vista eliminada correctamente"}, status=status.HTTP_204_NO_CONTENT)  # ✅ Mensaje corregido

class RolVistaViewSet(viewsets.ModelViewSet):  # ✅ Cambiado ModelViewSet
    queryset = RolVista.objects.filter(fechaElimino__isnull=True)
    serializer_class = RolVistaSerializer

    def list(self, request):
        try:
            vistarol = RolVistaService.obtener_datos()  # Ahora sí recibe objetos DTO

            if not vistarol:
                return Response({'error': 'No hay contenido'}, status=status.HTTP_204_NO_CONTENT)

            # ✅ Ahora `asdict()` funcionará correctamente
            rolvista_dict = [asdict(rolvista) for rolvista in vistarol]
            return Response(rolvista_dict, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs, partial=True)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.fechaElimino = timezone.now()
        instance.save()
        return Response({"message": "Rol vista eliminada correctamente"}, status=status.HTTP_204_NO_CONTENT)  # ✅ Mensaje corregido
    
class RolViewSet(viewsets.ModelViewSet):  # ✅ Cambiado ModelViewSet
    queryset = Rol.objects.filter(fechaElimino__isnull=True)
    serializer_class = RolSerializer

    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs, partial=True)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.fechaElimino = timezone.now()
        instance.save()
        return Response({"message": "Rol eliminado correctamente"}, status=status.HTTP_204_NO_CONTENT)  # ✅ Mensaje corregido
    
class UsuarioViewSet(viewsets.ModelViewSet):  # ✅ Cambiado ModelViewSet
    queryset = Usuario.objects.filter(fechaElimino__isnull=True)
    serializer_class = UsuarioSerializer

    def create(self, request, *args, **kwargs):
        """Sobrescribe el método create para usar UsuarioService."""
        data = request.data
        tipo_documento_id = data.get("tipoDocumento")  # Clave corregida

        # Convertir el ID en una instancia de TipoDocumento
        tipo_documento = get_object_or_404(TipoDocumento, id=tipo_documento_id)

        usuario = UsuarioService.crear(
            correo=data.get("correo"),
            nombres=data.get("nombres"),
            apellidos=data.get("apellidos"),
            documento=data.get("documento"),
            contrasena=data.get("contrasena"),
            tipoDocumento=tipo_documento,  # Pasamos la instancia
        )

        serializer = self.get_serializer(usuario)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def update(self, request, *args, **kwargs):
        instance = self.get_object()  # Obtiene el usuario actual
        data = request.data

        # Obtener el tipoDocumento de la solicitud o mantener el actual
        tipo_documento_id = data.get("tipoDocumento")
        tipo_documento = get_object_or_404(TipoDocumento, id=tipo_documento_id) if tipo_documento_id else instance.tipoDocumento

        usuario_actualizado = UsuarioService.actualizar(
            instance.id,
            correo=data.get("correo", instance.correo),
            nombres=data.get("nombres", instance.nombres),
            apellidos=data.get("apellidos", instance.apellidos),
            documento=data.get("documento", instance.documento),
            contrasena=data.get("contrasena") if "contrasena" in data else None,
            tipoDocumento=tipo_documento  # Mantenemos o actualizamos el tipo de documento
        )

        if usuario_actualizado:
            serializer = self.get_serializer(usuario_actualizado)
            return Response(serializer.data, status=status.HTTP_200_OK)

        return Response({"error": "No se pudo actualizar el usuario."}, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.fechaElimino = timezone.now()
        instance.save()
        return Response({"message": "Usuario eliminado correctamente"}, status=status.HTTP_204_NO_CONTENT)  # ✅ Mensaje corregido

    @action(detail=False, methods=['get'])
    def usuario_sin_rol(self, request):
        usuarios_sin_rol = UsuarioService.listusuarios_sin_rol()

        if not usuarios_sin_rol:
            return Response({'message': 'No hay usuarios sin rol'}, status=status.HTTP_204_NO_CONTENT)

        return Response([usuario.__dict__ for usuario in usuarios_sin_rol], status=status.HTTP_200_OK)

    
class UsuarioRolViewSet(viewsets.ModelViewSet):  # ✅ Cambiado ModelViewSet
    queryset = UsuarioRol.objects.filter(fechaElimino__isnull=True)
    serializer_class = UsuarioRolSerializer

    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs, partial=True)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.fechaElimino = timezone.now()
        instance.save()
        return Response({"message": "Usuario Rol eliminado correctamente"}, status=status.HTTP_204_NO_CONTENT)  # ✅ Mensaje corregido
        
class RecuperarContrasenaViewSet(viewsets.GenericViewSet):  # ✅ Cambiado ModelViewSet
    queryset = RecuperarContrasena.objects.filter(usado=True)
    serializer_class = RecuperarContrasenaSerializer
    
    @swagger_auto_schema(
        request_body=EnviarCodigoSerializer, 
        responses={200: "Codigo enviado", 400: "Correo inválido"}
    )
    
    @action(detail=False, methods=["post"], url_path="enviar-codigo", url_name="enviar_codigo")
    def enviar_codigo(self, request):
        serializer = EnviarCodigoSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        correo = request.data.get("correo")
        if not correo:  
            return Response({"error": "El correo es obligatorio"}, status=status.HTTP_400_BAD_REQUEST)

        resultado = RecuperarContrasenaService.EnviarCodigo(correo)

        if isinstance(resultado, str): 
            return Response({"error": resultado}, status=status.HTTP_404_NOT_FOUND)

        return Response({"message": "Código enviado correctamente", "usuario_id": resultado.usuario_id.id, "codigo": resultado.codigo}, status=status.HTTP_200_OK)
    
    @swagger_auto_schema(
        request_body=VerificarCodigoSerializer, 
        responses={200: "Código verificado", 400: "Código inválido"}
    )
    
    @action(detail=False, methods=["post"], url_path="verificar-codigo", url_name="verificar_codigo")
    def verificar_codigo(self, request):
        serializer = VerificarCodigoSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        codigo = request.data.get("codigo")
        usuario_id = request.data.get("usuario_id")
        if not codigo or not usuario_id:
            return Response({"error": "El código y el usuario son obligatorios"}, status=status.HTTP_400_BAD_REQUEST)

        resultado = RecuperarContrasenaService.VerificarCodigo(codigo, usuario_id)

        if isinstance(resultado, str):
            return Response({"error": resultado}, status=status.HTTP_404_NOT_FOUND)

        return Response({"message": "Código verificado correctamente"}, status=status.HTTP_200_OK)
    
    def destroy(self):
        instance = self.get_object()
        instance.fechaElimino = timezone.now()
        instance.save()
        return Response({"message": "Vista eliminada correctamente"}, status=status.HTTP_204_NO_CONTENT)  # ✅ Mensaje corregido
    
class CuestionarioViewSet(viewsets.ModelViewSet):  # ✅ Cambiado ModelViewSet
    queryset = Cuestionario.objects.filter(fechaElimino__isnull=True)
    serializer_class = CuestionarioSerializers

    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter(
                "cuestionario_id",
                openapi.IN_QUERY,
                description="Id del cuestionario",
                type=openapi.TYPE_INTEGER,
                required=True
            )
        ],
        responses={200: "exitoso", 404: "No se encontró un cuestionario con ese id."}
    )
    @action(detail=False, methods=["get"], url_path="cuestionariosid")
    def listar_cuestionarios(self, request):
        cuestionario_id = request.GET.get("cuestionario_id")

        if not cuestionario_id:
            return Response({"error": "Se requiere el parámetro 'cuestionario_id'."}, status=400)

        try:
            cuestionario_id = int(cuestionario_id)  # Convertir a entero
        except ValueError:
            return Response({"error": "El parámetro 'cuestionario_id' debe ser un número."}, status=400)

        cuestionario = CuestionarioService.obtener_cuestionarios(cuestionario_id)

        if not cuestionario:
            return Response({"error": "No se encontró un cuestionario con ese ID."}, status=404)

        return Response([item.__dict__ for item in cuestionario], status=200)

    @action(detail=False, methods=["get"], url_path="list_all_questionnaries")
    def listar_all_questionnaries(self, request):
        try:
            cuestionarios = CuestionarioService.list_all_questionnaries()

            if not cuestionarios:
                return Response({'message': 'No hay cuestionarios disponibles'}, status=status.HTTP_204_NO_CONTENT)

            cuestionarios_dict = [vars(cuestionario) for cuestionario in cuestionarios]

            return Response(cuestionarios_dict, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs, partial=True)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.fechaElimino = timezone.now()
        instance.save()
        return Response({"message": "Cuestionario eliminado correctamente"}, status=status.HTTP_204_NO_CONTENT)  # ✅ Mensaje corregido
    
class AprendizViewSet(viewsets.ModelViewSet):  # ✅ Cambiado ModelViewSet
    queryset = Aprendiz.objects.filter(fechaElimino__isnull=True)
    serializer_class = AprendizSerializer

    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs, partial=True)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.fechaElimino = timezone.now()
        instance.save()
        return Response({"message": "Aprendiz eliminado correctamente"}, status=status.HTTP_204_NO_CONTENT)  # ✅ Mensaje corregido

    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter(
                "documento",
                openapi.IN_QUERY,
                description="Número de documento del aprendiz",
                type=openapi.TYPE_STRING,
                required=True
            )
        ],
        responses={200: "exitoso", 400: "El documento es requerido.", 404: "No se encontró un aprendiz con ese documento."}
    )
    @action(detail=False, methods=["get"], url_path="documento")
    def buscar_por_documento(self, request):
        documento = request.query_params.get("documento")
        if not documento:
            return Response({"error": "El documento es requerido."}, status=status.HTTP_400_BAD_REQUEST)

        aprendiz = AprendizDAO.consultar_por_documento(documento)
        if not aprendiz:
            return Response({"error": "No se encontró un aprendiz con ese documento."},
                            status=status.HTTP_404_NOT_FOUND)

        serializer = ConsultarDocumentoSerializer(aprendiz)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
class RespuestasViewSet(viewsets.ModelViewSet):
    queryset = Respuesta.objects.filter(fechaElimino__isnull=True)
    serializer_class = RespuestasSerializer

    def create(self, request, *args, **kwargs):
        datos = request.data

        if  isinstance(datos, dict):
            datos = [datos]

        if not isinstance(datos, list):
            return Response({"error": "se espera un array o un objeto de respuesat"}, status=status.HTTP_400_BAD_REQUEST)

        resultado = RespuestasService.guardar_respuestas(datos)

        if "error" in resultado:
            return Response({"error": resultado["error"]}, status=status.HTTP_400_BAD_REQUEST)

        serializer = RespuestasSerializer(resultado["data"], many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs, partial=True)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.fechaElimino = timezone.now()
        instance.save()
        return Response({"message": "Respuestas eliminadas correctamente"}, status=status.HTTP_204_NO_CONTENT)  # ✅ Mensaje corregido
    
class ProcesoViewSet(viewsets.ModelViewSet):  # ✅ Cambiado ModelViewSet
    queryset = Proceso.objects.filter(fechaElimino__isnull=True)
    serializer_class = ProcesoSerializer

    def create(self, request):

        resultado = ProcesoService.registrar_proceso(request.data)

        if "error" in resultado:
            return Response({"error": resultado["error"]}, status=status.HTTP_400_BAD_REQUEST)

        return Response(resultado["data"], status=status.HTTP_201_CREATED)

    def update(self, request, *args, **kwargs):
        kwargs["partial"] = request.method == "PATCH"
        response = super().update(request, *args, **kwargs)  # Llamada original

        if request.method == "PATCH":
            response.status_code = status.HTTP_200_OK  # Cambia solo si es PATCH

        return response

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.fechaElimino = timezone.now()
        instance.save()
        return Response({"message": "Proceso eliminado correctamente"}, status=status.HTTP_204_NO_CONTENT)  # ✅ Mensaje corregido

    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter(
                "approved_status",
                openapi.IN_QUERY,
                description="nombre del rol que aprueba el proceso",
                type=openapi.TYPE_STRING,
                required=True
            )
        ],
        responses={200: "Exitoso", 400: "No hay data"}
    )
    @action(detail=False, methods=["get"], url_path="data")
    def data_proces(self, request):
        try:
            approved_status = request.query_params.get("approved_status")

            # Validar que el parámetro no esté vacío
            if not approved_status:
                return Response(
                    {"message": "El parámetro 'approved_status' es requerido"},
                    status=status.HTTP_400_BAD_REQUEST
                )

            data_proces = ProcesoService.obtener_procesos(approved_status)

            if not data_proces:
                return Response({"message": "no hay procesos"}, status=status.HTTP_400_BAD_REQUEST)

            data_proces_dict = [
                {
                    **vars(proces),
                    "preguntas": [
                        {
                            **vars(pregunta),
                            "respuestas": [vars(respuesta) for respuesta in pregunta.respuestas]
                        }
                        for pregunta in proces.preguntas
                    ]
                }
                for proces in data_proces
            ]

            return Response(data_proces_dict, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
class DesercionesViewSet(viewsets.ModelViewSet):  # ✅ Cambiado ModelViewSet
    queryset = Deserciones.objects.filter(fechaElimino__isnull=True)
    serializer_class = DesercionesSerializer

    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs, partial=True)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.fechaElimino = timezone.now()
        instance.save()
        return Response({"message": "Deserciones eliminadas correctamente"}, status=status.HTTP_204_NO_CONTENT)  # ✅ Mensaje corregido

class ComentarioViewSet(viewsets.ModelViewSet):
    queryset = Comentario.objects.filter(fechaElimino__isnull=True)
    serializer_class = ComentarioSerializer

    def create(self, request, *args, **kwargs):

        datos = request.data  # Recibe los datos enviados en el body
        resultado = ComentarioService.registrar_comentario(datos)  # Llama al servicio

        if "error" in resultado:
            return Response({"error": resultado["error"]}, status=status.HTTP_400_BAD_REQUEST)

        # Serializar la respuesta con los datos del comentario guardado
        comentario_serializado = ComentarioSerializer(resultado["data"])
        return Response(comentario_serializado.data, status=status.HTTP_201_CREATED)

    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs, partial=True)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.fechaElimino = timezone.now()
        instance.save()
        return Response({"message": "Comentario Eliminado correctamente"}, status=status.HTTP_204_NO_CONTENT)

    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter(
                "usuario_id",
                openapi.IN_QUERY,
                description="Id del usuario",
                type=openapi.TYPE_STRING,
                required=True
            ),
            openapi.Parameter(
                "approval_status",
                openapi.IN_QUERY,
                description="Estatus que aprueba el proceso",
                type=openapi.TYPE_STRING,
                required=True
            )
        ]
    )
    @action(detail=False, methods=["get"], url_path="data")
    def data_comment(self, request):
        usuario_id = request.query_params.get("usuario_id")
        approval_status = request.query_params.get("approval_status")

        if not usuario_id or not approval_status:
            return Response(
                {"error": "Faltan parámetros obligatorios: usuario_id y approval_status"},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Llamamos al servicio para obtener los comentarios
        resultado = ComentarioService.list_comment(usuario_id, approval_status)

        if "error" in resultado:
            return Response({"error": resultado["error"]}, status=status.HTTP_400_BAD_REQUEST)

        return Response(resultado, status=status.HTTP_200_OK)

class PreguntaViewSet(viewsets.ModelViewSet):
    queryset = Pregunta.objects.filter(fechaElimino__isnull=True)
    serializer_class = PreguntaSerializer

    def create(self, request, *args, **kwargs):
        datos = request.data

        if isinstance(datos, dict):
            datos = [datos]

        if not isinstance(datos, list):
            return Response({"error": "Se espera un array o un objeto de pregunta."}, status=status.HTTP_400_BAD_REQUEST)

        resultado = PreguntaService.save_question(datos)

        if "error" in resultado:
            return Response({"error": resultado["error"]}, status=status.HTTP_400_BAD_REQUEST)

        serializer = PreguntaSerializer(resultado["data"], many=True)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs, partial=True)
class LoginView(APIView):

    @swagger_auto_schema(
        request_body=UsuarioLoginSerializer,
        responses={200: "Login exitoso", 400: "Credenciales inválidas", 403: "Usuario sin rol asignado"}
    )
    def post(self, request):
        serializer = UsuarioLoginSerializer(data=request.data)

        if serializer.is_valid():
            correo = serializer.validated_data["correo"]
            contrasena = serializer.validated_data["contrasena"]

            usuario = UsuarioService.autenticar_usuario(correo, contrasena)

            if usuario:
                if not usuario.get("rol_id"):
                    return Response({"error": "Usuario sin rol asignado"}, status=status.HTTP_403_FORBIDDEN)

                return Response(usuario, status=status.HTTP_200_OK)

            return Response({"error": "Credenciales incorrectas"}, status=status.HTTP_401_UNAUTHORIZED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class TipoDocumentoViewSet(viewsets.ModelViewSet):
    queryset = TipoDocumento.objects.filter(fechaElimino__isnull=True)
    serializer_class = TipoDocumentoSerializer

    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs, partial=True)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.fechaElimino = timezone.now()
        instance.save()

        return Response({'message':'Tipo de documento eliminado correctamente'}, status=status.HTTP_204_NO_CONTENT)

class ListTraineesViewSet(viewsets.ViewSet):

    @swagger_auto_schema(
        request_body=ListTraineesSerializer,
        responses={ 200: 'OK, end of data loading'}
    )
    @action(detail=False, methods=["post"], url_path="list_trainees")
    def list_trainees(self, request):

        serializer = ListTraineesSerializer(data=request.data)

        if serializer.is_valid():
            id_instructor = request.data.get('id_instructor')

            if not id_instructor:
                return Response(
                    {'Error: ': 'The params are required'}, status=status.HTTP_404_NOT_FOUND
                )

            result = ListTraineesService.list_for_instructor(id_instructor)
            result_dict = [vars(resultTrainees) for resultTrainees in result]
            return Response(result_dict, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter(
                "user_id",
                openapi.IN_QUERY,
                description="Id del usuario",
                type=openapi.TYPE_STRING,
                required=True
            ),
            openapi.Parameter(
                "state",
                openapi.IN_QUERY,
                description="Estatus que aprueba el proceso",
                type=openapi.TYPE_STRING,
                required=True
            )
        ],
        responses={200: "OK, end of data loading"}
    )
    @action(detail=False, methods=["get"], url_path="process_instructor")
    def get_process(self, request):

        user_id = request.query_params.get("user_id")
        state = request.query_params.get("state")

        if not user_id or not state:
            return Response({'Error': 'The params are required'}, status=status.HTTP_404_NOT_FOUND)

        result = ProcessInstructorService.process_instructor(user_id, state)
        return Response(result, status=status.HTTP_200_OK)