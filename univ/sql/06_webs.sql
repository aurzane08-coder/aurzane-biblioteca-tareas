update public.universidades u set sitio_web = v.w from (values
('Venezuela','Universidad Simón Bolívar','https://www.usb.ve'),
('Venezuela','Universidad de Carabobo','http://www.uc.edu.ve'),
('Guatemala','Universidad de San Carlos de Guatemala','https://www.usac.edu.gt'),
('Cuba','Universidad de La Habana','http://www.uh.cu'),
('Cuba','Universidad Tecnológica de La Habana José Antonio Echeverría','https://www.cujae.edu.cu'),
('Cuba','Universidad de Ciencias Médicas de La Habana','https://instituciones.sld.cu/ucmh/'),
('Puerto Rico','Universidad de Puerto Rico, Recinto Universitario de Mayagüez','https://www.uprm.edu'),
('Austria','Universidad Técnica de Graz','https://www.tugraz.at'),
('Egipto','Universidad Ain Shams','https://www.asu.edu.eg'),
('Filipinas','Universidad de Santo Tomás','https://www.ust.edu.ph')
) v(p,n,w) where u.fuente='principales' and u.pais=v.p and u.nombre=v.n;
select count(*) from public.universidades where sitio_web is not null and sitio_web !~ '^https?://';