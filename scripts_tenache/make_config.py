from jinja2 import Template
import yaml

def make_config(
        config_name, 
        informacion_disponible,
        informacion_de_contacto,
        data, 
        out_config
        ):
    # Load template
    with open(config_name) as file:
        template = Template(file.read())

    # Use the old-school "%" formatting to substitute the 
    config_with_variables = template.render(data)

    # Save it to a new YAML file
    with open(out_config, 'w') as file:
        file.write(config_with_variables)

if __name__ == "__main__":
    # Variables to replace in the template
    informacion_disponible = """
            * Servicios_programados: Selecciona esta opción si el usuario solicita información específica sobre un servicio que ya ha sido programado, como el domicilio donde se realizará el servicio y el horario del mismo.  
            * Horarios_pub:  contiene Horarios de atención al público.
            * Informacion_general: Usa esta opción para preguntas sobre teléfonos de contacto,dirección de la empresa, páginas web, y tipos de servicios que ofrecen, especialmente si el usuario pregunta sobre qué tipo de plagas pueden controlar o\
            servicios generales que provee la empresa.
    """
    informacion_de_contacto = """ 
            📞   Telefono: {TELEFONO}. \n

        📱  Celular: {CELULAR}\n

        U+F618 Whatsapp: {WHATSAPP}\n
    """

    data = {
        'nombre_de_empresa': "O.FRE.SER - Gestión Integral de Plagas",
        'informacion_disponible':informacion_disponible,
        'informacion_de_contacto':informacion_de_contacto, 
    }
    make_config(
        "config_template.yaml",
        informacion_disponible,
        informacion_de_contacto,
        data,
        "config_out.yaml"
        )
	

	


