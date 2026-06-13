PRAGMA foreign_keys = ON;

INSERT OR IGNORE INTO categories (name, description) VALUES
  ('Académico', 'Cursos, evaluaciones y entregas'),
  ('Soporte técnico', 'Instalación y solución de errores'),
  ('Administrativo', 'Panel, usuarios y configuración'),
  ('Telegram', 'Bot, token, chat y comandos');

INSERT INTO questions (id, text, keywords, category_id, is_active) VALUES
  (1, '¿Cuál es el usuario del panel?', 'login usuario credenciales administrador', (SELECT id FROM categories WHERE name='Administrativo'), 1),
  (2, '¿Cuál es la contraseña del panel?', 'password contraseña credenciales administrador', (SELECT id FROM categories WHERE name='Administrativo'), 1),
  (3, '¿Cómo levanto el proyecto?', 'docker compose ejecutar levantar instalar', (SELECT id FROM categories WHERE name='Soporte técnico'), 1),
  (4, '¿Dónde veo la documentación de la API?', 'api docs swagger fastapi', (SELECT id FROM categories WHERE name='Soporte técnico'), 1),
  (5, '¿Dónde abro el panel administrativo?', 'frontend panel web url', (SELECT id FROM categories WHERE name='Administrativo'), 1),
  (6, '¿Cómo creo el bot de Telegram?', 'telegram botfather token crear bot', (SELECT id FROM categories WHERE name='Telegram'), 1),
  (7, '¿Qué hago si el bot no responde?', 'telegram bot error no responde', (SELECT id FROM categories WHERE name='Telegram'), 1),
  (8, '¿Cómo configuro el chat ID?', 'chat id grupo telegram configurar', (SELECT id FROM categories WHERE name='Telegram'), 1),
  (9, '¿Qué información guarda SmartBot?', 'base datos persistencia registros', (SELECT id FROM categories WHERE name='Administrativo'), 1),
  (10, '¿Cómo agrego una pregunta frecuente?', 'crear pregunta faq panel', (SELECT id FROM categories WHERE name='Administrativo'), 1),
  (11, '¿Cómo agrego una respuesta?', 'crear respuesta faq panel', (SELECT id FROM categories WHERE name='Administrativo'), 1),
  (12, '¿Cuántas categorías mínimas debe tener el sistema?', 'categorias minimo requisito', (SELECT id FROM categories WHERE name='Académico'), 1),
  (13, '¿Cuántas preguntas frecuentes incluye el sistema?', 'preguntas frecuentes faq veinte', (SELECT id FROM categories WHERE name='Académico'), 1),
  (14, '¿Qué pasa si no existe una respuesta?', 'sin respuesta desconocida fallback', (SELECT id FROM categories WHERE name='Soporte técnico'), 1),
  (15, '¿Dónde veo las estadísticas?', 'estadisticas consultas usuarios categorias', (SELECT id FROM categories WHERE name='Administrativo'), 1),
  (16, '¿Cómo cierro sesión del panel?', 'logout cerrar sesion token', (SELECT id FROM categories WHERE name='Administrativo'), 1),
  (17, '¿La base de datos persiste al reiniciar Docker?', 'sqlite volumen persistencia docker', (SELECT id FROM categories WHERE name='Soporte técnico'), 1),
  (18, '¿Cómo pruebo una consulta sin Telegram?', 'buscar probar consulta panel', (SELECT id FROM categories WHERE name='Soporte técnico'), 1),
  (19, '¿Qué arquitectura utiliza SmartBot?', 'arquitectura capas api repositorio servicios', (SELECT id FROM categories WHERE name='Académico'), 1),
  (20, '¿Cómo consulto SmartBot desde Telegram?', 'mensaje comando start ayuda telegram', (SELECT id FROM categories WHERE name='Telegram'), 1);

INSERT INTO answers (id, question_id, text, priority, is_active) VALUES
  (1, 1, 'El usuario preconfigurado es IA1-User.', 1, 1),
  (2, 2, 'La contraseña preconfigurada es IA1-password@_new.', 1, 1),
  (3, 3, 'Copia .env.example a .env y ejecuta docker compose up --build.', 1, 1),
  (4, 4, 'La documentación OpenAPI está disponible en http://localhost:8100/docs.', 1, 1),
  (5, 5, 'El panel administrativo se abre en http://localhost:8090.', 1, 1),
  (6, 6, 'Abre @BotFather, usa /newbot y guarda el token en TELEGRAM_BOT_TOKEN dentro de .env.', 1, 1),
  (7, 7, 'Verifica el token, los logs de telegram-bot y que el contenedor pueda acceder a api-gateway.', 1, 1),
  (8, 8, 'Inicia sesión, abre Configuración y actualiza telegram_chat_id.', 1, 1),
  (9, 9, 'Guarda categorías, preguntas, respuestas, administradores, configuración y registros de consultas en SQLite.', 1, 1),
  (10, 10, 'En el panel abre Preguntas, completa el formulario, selecciona una categoría y presiona Guardar.', 1, 1),
  (11, 11, 'En el panel abre Respuestas, elige la pregunta asociada, escribe el texto y presiona Guardar.', 1, 1),
  (12, 12, 'El requisito mínimo es de 3 categorías; la semilla inicial incluye 4.', 1, 1),
  (13, 13, 'La semilla SQL inicial registra 20 preguntas y 20 respuestas.', 1, 1),
  (14, 14, 'El bot devuelve el mensaje configurable unknown_message y registra la consulta como desconocida.', 1, 1),
  (15, 15, 'El Dashboard muestra consultas totales, usuarios únicos, preguntas frecuentes y categorías consultadas.', 1, 1),
  (16, 16, 'Presiona Cerrar sesión; el panel elimina el token JWT almacenado en el navegador.', 1, 1),
  (17, 17, 'Sí. SQLite se almacena en el volumen smartbot_data, que no se elimina al reiniciar contenedores.', 1, 1),
  (18, 18, 'Usa la sección Probar consulta del panel; esa búsqueda usa la misma API y base de datos que Telegram.', 1, 1),
  (19, 19, 'Usa una arquitectura por capas: frontend, API REST FastAPI, servicios de dominio, persistencia SQL y bot Telegram.', 1, 1),
  (20, 20, 'Envía /start para ver la ayuda o escribe directamente una pregunta; el bot consultará la API REST.', 1, 1);

INSERT OR IGNORE INTO settings (key, value, description) VALUES
  ('telegram_chat_id', '', 'Chat o grupo de Telegram para mensajes de prueba'),
  ('unknown_message', 'No encontré una respuesta registrada. Intenta reformular la consulta.', 'Mensaje para consultas sin coincidencia'),
  ('welcome_message', 'Hola, soy SmartBot. Escribe una pregunta y consultaré la base de datos.', 'Mensaje de bienvenida del bot');
