-- ESMIL, ESFORSE y Zamorano en el catálogo de universidades (se puede ejecutar varias veces).
-- Pegar en Supabase > SQL Editor > Run. El portal de NEXUS se regenera solo esa misma noche.

-- 1) Escuelas militares del Ejército de Ecuador
delete from public.carreras where universidad_id in (select id from public.universidades where fuente = 'escuelas-militares');
delete from public.universidades where fuente = 'escuelas-militares';

insert into public.universidades (nombre, tipo_ies, tipo, pais, sitio_web, ciudad, region, acronimo, descripcion, visible, destacada, fuente) values
('Escuela Superior Militar Eloy Alfaro (ESMIL)', 'Escuela militar', 'pública', 'Ecuador', 'https://esmil.mil.ec/', 'Quito', 'Pichincha', 'ESMIL',
 'Forma a los oficiales del Ejército Ecuatoriano. Cuatro años de formación con internado; se egresa como subteniente con la Licenciatura en Ciencias Militares, avalada por la Universidad de las Fuerzas Armadas ESPE. Admite hombres y mujeres. Requisitos habituales: ser bachiller, ecuatoriano, soltero y sin hijos, edad máxima cercana a los 22 años y estatura mínima. La convocatoria se abre cada año en ejercitoecuatoriano.mil.ec (Reclutamiento) y exige también la inscripción en el registro nacional de educación superior.',
 true, true, 'escuelas-militares'),
('Escuela de Formación de Soldados del Ejército «Vencedores del Cenepa» (ESFORSE)', 'Escuela militar', 'pública', 'Ecuador', 'https://www.ejercitoecuatoriano.mil.ec/', 'Ambato', 'Tungurahua', 'ESFORSE',
 'Forma a los soldados de arma y servicios del Ejército Ecuatoriano. Dos años de formación con internado; se egresa como soldado con la Tecnología Superior en Ciencias Militares, avalada por la Universidad de las Fuerzas Armadas ESPE. Requisitos habituales: ser bachiller, ecuatoriano, soltero y sin hijos, edad máxima cercana a los 22 años y estatura mínima. La convocatoria se abre cada año en ejercitoecuatoriano.mil.ec (Reclutamiento > Armas y Servicios).',
 true, true, 'escuelas-militares');

insert into public.carreras (universidad_id, nombre, campo_amplio, nivel_categoria, modalidad, provincia, canton, nivel_detalle)
select u.id, c.nombre, 'Servicios', c.nivel, 'Presencial', c.provincia, c.canton, 'programa'
from public.universidades u
join (values
  ('ESMIL', 'Ciencias Militares (oficial del Ejército)', 'Universitario (grado)', 'Pichincha', 'Quito'),
  ('ESFORSE', 'Tecnología Superior en Ciencias Militares (soldado del Ejército)', 'Técnico/Tecnológico superior', 'Tungurahua', 'Ambato')
) as c(acr, nombre, nivel, provincia, canton) on c.acr = u.acronimo
where u.fuente = 'escuelas-militares';

-- 2) Zamorano (Honduras): ya estaba en el catálogo, se completan datos y carreras
update public.universidades set
  sitio_web = 'https://zamorano.edu/lp-ecuador-2025/',
  ciudad = 'Valle del Yeguare', region = 'Francisco Morazán', acronimo = 'Zamorano', destacada = true,
  descripcion = 'Universidad agrícola privada de Honduras, conocida como Zamorano, con estudiantes de toda América Latina y una página específica para aspirantes de Ecuador. Modelo «aprender haciendo» con residencia en el campus. Requisitos publicados: ser bachiller o estar en el último año, tener menos de 24 años, promedio de colegio mínimo del 80 % y examen de admisión (PAA o ePAA del College Board, o SAT, con 1000 puntos como mínimo).'
where nombre = 'Escuela Agrícola Panamericana Zamorano';

delete from public.carreras where universidad_id = (select id from public.universidades where nombre = 'Escuela Agrícola Panamericana Zamorano' limit 1);
insert into public.carreras (universidad_id, nombre, campo_amplio, nivel_categoria, modalidad, provincia, canton, nivel_detalle)
select u.id, c.nombre, 'Agricultura, Silvicultura, Pesca y Veterinaria', 'Universitario (grado)', 'Presencial', 'Francisco Morazán', 'San Antonio de Oriente', 'programa'
from public.universidades u,
(values ('Ingeniería Agronómica'), ('Ingeniería en Agroindustria Alimentaria'), ('Ingeniería en Agronegocios'), ('Ingeniería en Ambiente y Desarrollo')) as c(nombre)
where u.nombre = 'Escuela Agrícola Panamericana Zamorano';

-- comprobación: deben salir 3 filas (2 + 4 carreras)
select u.nombre, count(c.id) as carreras from public.universidades u left join public.carreras c on c.universidad_id = u.id
where u.fuente = 'escuelas-militares' or u.nombre = 'Escuela Agrícola Panamericana Zamorano' group by u.nombre;
