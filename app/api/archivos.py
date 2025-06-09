columns_mapping = {
    "CODIGO_REGIONAL": "cod_regional",  # INT UNSIGNED, tabla: regional, campo: cod_regional
    "NOMBRE_REGIONAL": "nombre_regional",  # VARCHAR(80), tabla: regional, campo: nombre
    "CODIGO_CENTRO": "cod_centro",  # INT UNSIGNED, tabla: centro_formacion, campo: cod_centro
    "NOMBRE_CENTRO": "nombre_centro",  # VARCHAR(80), tabla: centro_formacion, campo: nombre_centro
    "IDENTIFICADOR_FICHA": "cod_ficha",  # INT UNSIGNED, tabla: grupo, campo: cod_ficha
    "IDENTIFICADOR_UNICO_FICHA": "cod_ficha",  # INT UNSIGNED, tabla: grupo, campo: cod_ficha (mismo valor)
    "ESTADO_CURSO": "estado_grupo",  # VARCHAR(30), tabla: grupo, campo: estado_grupo
    #"CODIGO_NIVEL_FORMACION": "cod_nivel_formacion",  # (No existe, puedes ignorar o crear campo)
    "NIVEL_FORMACION": "nombre_nivel",  # VARCHAR(40), tabla: grupo, campo: nombre_nivel
    #"CODIGO_JORNADA": "cod_jornada",  # (No existe, puedes ignorar o crear campo)
    "NOMBRE_JORNADA": "jornada",  # VARCHAR(15), tabla: grupo, campo: jornada
    #"TIPO_DE_FORMACION": "tipo_de_formacion",  # (No existe, puedes ignorar o crear campo)
    "FECHA_INICIO_FICHA": "fecha_inicio",  # DATE, tabla: grupo, campo: fecha_inicio
    "FECHA_TERMINACION_FICHA": "fecha_fin",  # DATE, tabla: grupo, campo: fecha_fin
    "ETAPA_FICHA": "etapa",  # VARCHAR(20), tabla: grupo, campo: etapa
    "MODALIDAD_FORMACION": "modalidad",  # VARCHAR(30), tabla: grupo, campo: modalidad
    "NOMBRE_RESPONSABLE": "responsable",  # VARCHAR(60), tabla: grupo, campo: responsable
    #"NUMERO_IDENTIFICACION_EMPRESA": "numero_identificacion_empresa",  # (No existe, puedes ignorar o crear campo)
    #"TIPO_IDENTIFICACION_EMPRESA": "tipo_identificacion_empresa",  # (No existe, puedes ignorar o crear campo)
    "NOMBRE_EMPRESA": "nombre_empresa",  # VARCHAR(40), tabla: grupo, campo: nombre_empresa
    #"CODIGO_SECTOR_PROGRAMA": "cod_sector_programa",  # (No existe, puedes ignorar o crear campo)
    #"NOMBRE_SECTOR_PROGRAMA": "nombre_sector_programa",  # (No existe, puedes ignorar o crear campo)
    #"CODIGO_OCUPACION": "cod_ocupacion",  # (No existe, puedes ignorar o crear campo)
    #"NOMBRE_OCUPACION": "nombre_ocupacion",  # (No existe, puedes ignorar o crear campo)
    "CODIGO_PROGRAMA": "cod_programa",  # INT UNSIGNED, tabla: grupo, campo: cod_programa
    "VERSION_PROGRAMA": "la_version",  # TINYINT UNSIGNED, tabla: grupo, campo: la_version
    #"NOMBRE_PROGRAMA_FORMACION": "nombre_programa_formacion",  # (No existe, puedes ignorar o crear campo)
    #"CODIGO_PAIS_CURSO": "cod_pais_curso",  # (No existe, puedes ignorar o crear campo)
    #"NOMBRE_PAIS_CURSO": "nombre_pais_curso",  # (No existe, puedes ignorar o crear campo)
    #"CODIGO_DEPARTAMENTO_CURSO": "cod_departamento_curso",  # (No existe, puedes ignorar o crear campo)
    #"NOMBRE_DEPARTAMENTO_CURSO": "nombre_departamento_curso",  # (No existe, puedes ignorar o crear campo)
    #"CODIGO_MUNICIPIO_CURSO": "cod_municipio_curso",  # (No existe, puedes ignorar o crear campo)
    "NOMBRE_MUNICIPIO_CURSO": "nombre_municipio",  # VARCHAR(30), tabla: grupo, campo: nombre_municipio
    #"CODIGO_CONVENIO": "cod_convenio",  # (No existe, puedes ignorar o crear campo)
    #"NOMBRE_CONVENIO": "nombre_convenio",  # (No existe, puedes ignorar o crear campo)
    #"AMPLIACION_COBERTURA": "ampliacion_cobertura",  # (No existe, puedes ignorar o crear campo)
    #"CODIGO_PROGRAMA_ESPECIAL": "cod_programa_especial",  # (No existe, puedes ignorar o crear campo)
    "NOMBRE_PROGRAMA_ESPECIAL": "nombre_programa_especial",  # VARCHAR(60), tabla: grupo, campo: nombre_programa_especial
    #"NUMERO_CURSOS": "numero_cursos",  # (No existe, puedes ignorar o crear campo)
    "TOTAL_APRENDICES_MASCULINOS": "num_aprendices_masculinos",  # TINYINT UNSIGNED, tabla: datos_grupo, campo: num_aprendices_masculinos
    "TOTAL_APRENDICES_FEMENINOS": "num_aprendices_femenino",  # TINYINT UNSIGNED, tabla: datos_grupo, campo: num_aprendices_femenino
    "TOTAL_APRENDICES_NOBINARIO": "num_aprendices_no_binario",  # TINYINT UNSIGNED, tabla: datos_grupo, campo: num_aprendices_no_binario
    "TOTAL_APRENDICES": "num_total_aprendices",  # TINYINT UNSIGNED, tabla: datos_grupo, campo: num_total_aprendices
    #"HORAS_PLANTA": "horas_planta",  # (No existe, puedes ignorar o crear campo)
    #"HORAS_CONTRATISTAS": "horas_contratistas",  # (No existe, puedes ignorar o crear campo)
    #"HORAS_CONTRATISTAS_EXTERNOS": "horas_contratistas_externos",  # (No existe, puedes ignorar o crear campo)
    #"HORAS_MONITORES": "horas_monitores",  # (No existe, puedes ignorar o crear campo)
    #"HORAS_INST_EMPRESA": "horas_inst_empresa",  # (No existe, puedes ignorar o crear campo)
    #"TOTAL_HORAS": "total_horas",  # (No existe, puedes ignorar o crear campo)
    "TOTAL_APRENDICES_ACTIVOS": "num_total_aprendices_activos",  # TINYINT UNSIGNED, tabla: datos_grupo, campo: num_total_aprendices_activos
    #"DURACION_PROGRAMA": "duracion_programa",  # (No existe, puedes ignorar o crear campo)
    #"NOMBRE_NUEVO_SECTOR": "nombre_nuevo_sector"  # (No existe, puedes ignorar o crear campo)
}


columns_mapping2 = {
    "CODIGO_REGIONAL": "cod_regional",  # INT UNSIGNED, tabla: regional, campo: cod_regional
    "REGIONAL": "nombre_regional",  # VARCHAR(80), tabla: regional, campo: nombre
    "CODIGO_CENTRO": "cod_centro",  # INT UNSIGNED, tabla: centro_formacion, campo: cod_centro
    "CENTRO": "nombre_centro",  # VARCHAR(80), tabla: centro_formacion, campo: nombre_centro
    "CODIGO_PROGRAMA": "cod_programa",  # INT UNSIGNED, tabla: programa_formacion, campo: cod_programa
    "VERSION_PROGRAMA": "la_version",  # TINYINT UNSIGNED, tabla: programa_formacion, campo: la_version
    "PROGRAMA": "nombre_programa",  # VARCHAR(30), tabla: programa_formacion, campo: nombre
    "NIVEL_FORMACION": "nombre_nivel",  # VARCHAR(40), tabla: grupo, campo: nombre_nivel
    "DURACION_MAXIMA": "duracion_maxima",  # (No existe, puedes ignorar o crear campo)
    "DURACION_ETAPA_LECTIVA": "horas_lectivas",  # INT, tabla: programa_formacion, campo: horas_lectivas
    "DURACION_ETAPA_PRODUCTIVA": "horas_productivas",  # INT, tabla: programa_formacion, campo: horas_productivas
    "FICHA": "cod_ficha",  # INT UNSIGNED, tabla: grupo, campo: cod_ficha
    "FECHA_INICIO_FICHA": "fecha_inicio",  # DATE, tabla: grupo, campo: fecha_inicio
    "FECHA_FIN_FICHA": "fecha_fin",  # DATE, tabla: grupo, campo: fecha_fin
    "CUPO": "cupo_total",  # TINYINT UNSIGNED, tabla: datos_grupo, campo: cupo_total
    "ESTADO_FICHA": "estado_grupo",  # VARCHAR(30), tabla: grupo, campo: estado_grupo
    #"TIPO_RESPUESTA": "tipo_respuesta",  # (No existe, puedes ignorar o crear campo)
    "PROGRAMA_ESPECIAL": "nombre_programa_especial",  # VARCHAR(60), tabla: grupo, campo: nombre_programa_especial
    #"CODIGO_CONVENIO": "cod_convenio",  # (No existe, puedes ignorar o crear campo)
    #"AMPLIACION_COBERTURA": "ampliacion_cobertura",  # (No existe, puedes ignorar o crear campo)
    #"CONVENIO": "nombre_convenio",  # (No existe, puedes ignorar o crear campo)
    #"TIPO_DOCUMENTO_EMPRESA": "tipo_documento_empresa",  # (No existe, puedes ignorar o crear campo)
    #"NUMERO_DOCUMENTO_EMPRESA": "numero_documento_empresa",  # (No existe, puedes ignorar o crear campo)
    "EMPRESA": "nombre_empresa",  # VARCHAR(40), tabla: grupo, campo: nombre_empresa
    "EN_TRANSITO": "en_transito",  # TINYINT UNSIGNED, tabla: datos_grupo, campo: en_transito
    "INDUCCION": "induccion",  # TINYINT UNSIGNED, tabla: datos_grupo, campo: induccion
    "FORMACION": "formacion",  # TINYINT UNSIGNED, tabla: datos_grupo, campo: formacion
    "CONDICIONADO": "condicionado",  # TINYINT UNSIGNED, tabla: datos_grupo, campo: condicionado
    "APLAZADO": "aplazado",  # TINYINT UNSIGNED, tabla: datos_grupo, campo: aplazado
    "RETIRO_VOLUNTARIO": "retiro_voluntuario",  # TINYINT UNSIGNED, tabla: datos_grupo, campo: retiro_voluntuario
    "CANCELAMIENTO_VIRT_COMP": "cancelamiento_vit_comp",  # TINYINT UNSIGNED, tabla: datos_grupo, campo: cancelamiento_vit_comp
    "DESERCION_VIRT_COMP": "desercion_vit_comp",  # TINYINT UNSIGNED, tabla: datos_grupo, campo: desercion_vit_comp
    "CANCELADO": "cancelado",  # TINYINT UNSIGNED, tabla: datos_grupo, campo: cancelado
    "POR_CERTIFICAR": "por_certificar",  # TINYINT UNSIGNED, tabla: datos_grupo, campo: por_certificar
    "CERTIFICADO": "certificados",  # TINYINT UNSIGNED, tabla: datos_grupo, campo: certificados
    "TRASLADADO": "traslados",  # TINYINT UNSIGNED, tabla: datos_grupo, campo: traslados
    "OTRO": "otro"  # TINYINT UNSIGNED, tabla: datos_grupo, campo: otro
}
