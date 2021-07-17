from .utils import *
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login as do_login
from django.contrib.auth import logout as do_logout
from django.contrib.auth.models import User
# ----- 77
from datetime import timedelta
# ----- 77


def order_list_alm(json):
    try:
        # Also convert to int since update_time will be string.  When comparing
        # strings, "10" is smaller than "2".
        return int(json['porcent'])
    except KeyError:
        return 0


def welcome(request):

    # Si estamos identificados devolvemos la portada
    if request.user.is_authenticated:

        cursor = get_from_db()
        queries = []

        #School selector

        activate_letra_filter = False
        if request.GET.get('letra') and request.GET.get('letra') != "0":
            activate_letra_filter = True
            letra_filter = ' AND pertenece.letra_id=' + request.GET.get('letra')
        if request.GET.get('nivel') and request.GET.get('letra') != 0:
            activate_nivel_filter = True
            nivel_filter = ' pertenece.nivel_id=' + request.GET.get('nivel')
        cursor.execute(
            'SELECT colegio.id, colegio.nombre FROM pertenece INNER JOIN usuario ON pertenece.usuario_id = usuario.id INNER JOIN colegio ON pertenece.colegio_id = colegio.id WHERE usuario.username="'
            + request.user.username + '" GROUP BY colegio.id')
        schools = cursor.fetchall()
        schools_response = []
        for row in schools:
            schools_response.append({'id': row[0], 'name': row[1]})

        # Nivel selector
        school_filter = ''
        activate_school_filter = False
        if request.GET.get('school') and request.GET.get('school') != "0":
            activate_school_filter = True
            school_filter = ' AND p.colegio_id=' + request.GET.get('school')
        cursor.execute(
            'SELECT nivel_id, concat(n.nombre) as Nivelcurso FROM pertenece p, nivel n, letra l, usuario u where p.letra_id = l.id && p.nivel_id = n.id && p.usuario_id = u.id AND u.username="'
            + request.user.username + '"' + school_filter + " GROUP BY nivel_id"
            )
        niveles = cursor.fetchall()
        niveles_response = []
        for row in niveles:
            niveles_response.append({'id': row[0], 'name': row[1]})


        # letra selector
        course_filter = ''
        activate_school_filter = False
        if request.GET.get('school') and request.GET.get('school') != "0":
            activate_school_filter = True
            course_filter = ' AND p.colegio_id=' + request.GET.get('school')
        if request.GET.get('nivel') and request.GET.get('letra') != 0:
            activate_nivel_filter = True
            course_filter = ' AND p.nivel_id=' + request.GET.get('nivel')
        cursor.execute(
            'SELECT letra_id, concat(l.nombre) as Nivelcurso FROM pertenece p, nivel n, letra l, usuario u where p.letra_id = l.id && p.nivel_id = n.id && p.usuario_id = u.id AND u.username="'
            + request.user.username + '"' + school_filter + " GROUP BY letra_id"
            )
        letras = cursor.fetchall()
        letras_response = []
        for row in letras:
            letras_response.append({'id': row[0], 'name': row[1]})

        # Reim selector
        course_filter = ''

        activate_course_filter = False
        if request.GET.get('letra') and request.GET.get('letra') != "0":
            activate_letra_filter = True
            letra_filter = 'where letra_id =' + request.GET.get('letra')
        if request.GET.get('nivel') and request.GET.get('nivel') != 0:
            activate_nivel_filter = True
            nivel_filter = 'nivel_id =' + request.GET.get('nivel')
        if request.GET.get('school') and request.GET.get('school') != "0":
            activate_school_filter = True
            school_filter = ' AND p.colegio_id=' + request.GET.get('school')

        # cursor.execute('SELECT DISTINCT reim.id, reim.nombre from actividad inner join reim on id_reim = reim.id inner join asigna_reim on reim_id = reim_id inner join pertenece on asigna_reim.colegio_id = pertenece.colegio_id  inner join colegio on asigna_reim.colegio_id = colegio.id inner join curso on asigna_reim.curso_id = curso.id  inner join usuario on pertenece.usuario_id = usuario.id where usuario.username ="' + request.user.username + '"' + course_filter +' GROUP BY reim.id')
        cursor.execute(
            'SELECT DISTINCT reim.id, reim.nombre from asigna_reim inner join reim on reim_id = reim.id '
            + course_filter + ' GROUP BY reim.id')
        reims = cursor.fetchall()
        reims_response = []
        for row in reims:
            reims_response.append({'id': row[0], 'name': row[1]})
        #Activity selector
        reim_filter = ''
        activate_reim_filter = False
        if request.GET.get('reim') and request.GET.get('reim') != "0":
            activate_reim_filter = True
            reim_filter = ' AND alumno_respuesta_actividad.id_reim=' + request.GET.get('reim')

        cursor.execute(
            'SELECT actividad.id, actividad.nombre from actividad, alumno_respuesta_actividad, usuario where actividad.id = alumno_respuesta_actividad.id_actividad && usuario.id = alumno_respuesta_actividad.id_user AND usuario.username="'
            + request.user.username + '"' + reim_filter +
            ' AND actividad.id != 2 GROUP BY actividad.id')
        activities = cursor.fetchall()
        activities_response = []
        for row in activities:
            activities_response.append({'id': row[0], 'name': row[1]})

        # Touch
        touch_query = get_touch_query(request)
        queries.append({"name": 'Touch query', "query": touch_query})
        cursor.execute(touch_query)
        touch_quantity = cursor.fetchall()
        touch_quantity_response = []
        for row in touch_quantity:
            touch_quantity_response.append({
                'id': row[0],
                'name': row[1],
                'quantity': row[2]
            })
        touch_quantity_graph = len(touch_quantity) * 40 + 20

        #Cantidad de Usuarios
        cant_usuarios = get_alumnos(request)
        #print("largo de graficos")
        #print(cant_usuarios)
        #actividad seleccionada
        activity_num = request.GET.get('activity')
        activate_activity_filter = True
        if request.GET.get('activity') and request.GET.get('activity') != "0":
            activate_activity_filter = False
        #REIM SELECCIONADO
        reim_num = request.GET.get('reim')

        student_num = request.GET.get('student')
        students_response = []
        if request.GET.get('school') and request.GET.get('school') != '0':
            if request.GET.get('letra') and request.GET.get('letra') != '0':
                cursor.execute(
                    'SELECT DISTINCT u.id, concat(u.nombres ," " , u.apellido_paterno ," " , u.apellido_materno) as nombre FROM alumno_respuesta_actividad a, usuario u, pertenece b WHERE a.id_user = u.id && b.usuario_id = a.id_user && b.colegio_id IN (SELECT colegio_id from pertenece INNER JOIN usuario ON usuario.id = pertenece.usuario_id WHERE username="'
                    + request.user.username + '")' +
                    'AND b.letra_id IN (SELECT letra_id FROM pertenece WHERE usuario_id = (SELECT id FROM usuario WHERE username ="'
                    + request.user.username + '"))' + 'AND a.id_reim="' +
                    request.GET.get('reim') + '"' + 'AND b.letra_id ="' +
                    request.GET.get('letra') + '"' + 'AND b.colegio_id ="' +
                    request.GET.get('school') + '";')
                students = cursor.fetchall()
                for row in students:
                    students_response.append({'id': row[0], 'name': row[1]})




        return render(
            request,
            "users/welcome.html",
            {

                # Other context var
                'queries':
                queries,
                'schools':
                schools_response,
                'reims':
                reims_response,
                'letras':
                letras_response,
                'niveles':
                niveles_response,
                'activities':
                activities_response,
                'students':
                students_response,
                'touch_quantity':
                touch_quantity_response,
                'touch_quantity_len':
                len(touch_quantity_response),
                'student_num':
                student_num,
                'reim_num':
                reim_num,





            })
    # En otro caso redireccionamos al login
    return redirect('/login')


def register(request):
    # Creamos el formulario de autenticación vacío
    form = UserCreationForm()
    if request.method == "POST":
        # Añadimos los datos recibidos al formulario
        form = UserCreationForm(data=request.POST)
        # Si el formulario es válido...
        if form.is_valid():

            # Creamos la nueva cuenta de usuario
            user = form.save()

            # Si el usuario se crea correctamente
            if user is not None:
                # Hacemos el login manualmente
                do_login(request, user)
                # Y le redireccionamos a la portada
                return redirect('/')

    form.fields['username'].help_text = None
    form.fields['password1'].help_text = None
    form.fields['password2'].help_text = None

    # Si llegamos al final renderizamos el formulario
    return render(request, "users/register.html", {'form': form})


def login(request):
    # Creamos el formulario de autenticación vacío
    form = AuthenticationForm()
    if request.method == "POST":
        # Añadimos los datos recibidos al formulario
        form = AuthenticationForm(data=request.POST)
        #Conectamos con la db de ulearnet][_h]
        cursor = get_from_db()
        query = 'SELECT username, email, password, nombres FROM usuario WHERE (tipo_usuario_id = 1 OR tipo_usuario_id = 2) AND (username="' + request.POST.get(
            'username') + '" AND password="' + request.POST.get(
                'password') + '")'
        cursor.execute(query)
        data = cursor.fetchone()

        if data:
            user, created = User.objects.get_or_create(username=data[0],
                                                       email=data[1],
                                                       first_name=data[3])
            if created:
                user.set_password(data[2])
                user.save()
        else:
            print("nada")
        # Si el formulario es válido...
        if form.is_valid():
            # Recuperamos las credenciales validadas
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']

            # Verificamos las credenciales del usuario
            user = authenticate(username=username, password=password)

            # Si existe un usuario con ese nombre y contraseña
            if user is not None:
                # Hacemos el login manualmente
                do_login(request, user)
                # Y le redireccionamos a la portada
                return redirect('/')
        else:
            print(form)

    # Si llegamos al final renderizamos el formulario
    return render(request, "users/login.html", {'form': form})


def logout(request):
    # Finalizamos la sesión
    do_logout(request)
    # Redireccionamos a la portada
    return redirect('/')