-- gestion_formacion.competencia definition

CREATE TABLE `competencia` (
  `cod_competencia` int unsigned NOT NULL,
  `nombre` varchar(60) DEFAULT NULL,
  `horas` int unsigned DEFAULT NULL,
  PRIMARY KEY (`cod_competencia`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3;


-- gestion_formacion.festivos definition

CREATE TABLE `festivos` (
  `festivo` date NOT NULL,
  PRIMARY KEY (`festivo`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3;


-- gestion_formacion.metas definition

CREATE TABLE `metas` (
  `id_meta` int unsigned NOT NULL AUTO_INCREMENT,
  `anio` year DEFAULT NULL,
  `concepto` varchar(100) DEFAULT NULL,
  `valor` int unsigned DEFAULT NULL,
  PRIMARY KEY (`id_meta`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3;


-- gestion_formacion.programa_formacion definition

CREATE TABLE `programa_formacion` (
  `cod_programa` int unsigned NOT NULL,
  `la_version` tinyint unsigned NOT NULL,
  `nombre` varchar(30) DEFAULT NULL,
  `horas_lectivas` int DEFAULT NULL,
  `horas_productivas` int DEFAULT NULL,
  PRIMARY KEY (`cod_programa`,`la_version`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3;


-- gestion_formacion.regional definition

CREATE TABLE `regional` (
  `cod_regional` int unsigned NOT NULL,
  `nombre` varchar(80) DEFAULT NULL,
  PRIMARY KEY (`cod_regional`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3;


-- gestion_formacion.rol definition

CREATE TABLE `rol` (
  `id_rol` int unsigned NOT NULL,
  `nombre` varchar(30) DEFAULT NULL,
  PRIMARY KEY (`id_rol`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3;


-- gestion_formacion.centro_formacion definition

CREATE TABLE `centro_formacion` (
  `cod_centro` int unsigned NOT NULL,
  `nombre_centro` varchar(80) DEFAULT NULL,
  `cod_regional` int unsigned DEFAULT NULL,
  PRIMARY KEY (`cod_centro`),
  KEY `cod_regional` (`cod_regional`),
  CONSTRAINT `centro_formacion_ibfk_1` FOREIGN KEY (`cod_regional`) REFERENCES `regional` (`cod_regional`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3;


-- gestion_formacion.grupo definition

CREATE TABLE `grupo` (
  `cod_ficha` int unsigned NOT NULL,
  `cod_centro` int unsigned DEFAULT NULL,
  `cod_programa` int unsigned DEFAULT NULL,
  `la_version` tinyint unsigned DEFAULT NULL,
  `estado_grupo` varchar(30) DEFAULT NULL,
  `nombre_nivel` varchar(40) DEFAULT NULL,
  `jornada` varchar(15) DEFAULT NULL,
  `fecha_inicio` date DEFAULT NULL,
  `fecha_fin` date DEFAULT NULL,
  `etapa` varchar(20) DEFAULT NULL,
  `modalidad` varchar(30) DEFAULT NULL,
  `responsable` varchar(60) DEFAULT NULL,
  `nombre_empresa` varchar(40) DEFAULT NULL,
  `nombre_municipio` varchar(30) DEFAULT NULL,
  `nombre_programa_especial` varchar(60) DEFAULT NULL,
  `hora_inicio` time DEFAULT NULL,
  `hora_fin` time DEFAULT NULL,
  `aula_actual` char(20) DEFAULT NULL,
  PRIMARY KEY (`cod_ficha`),
  KEY `cod_centro` (`cod_centro`),
  KEY `cod_programa` (`cod_programa`,`la_version`),
  CONSTRAINT `grupo_ibfk_1` FOREIGN KEY (`cod_centro`) REFERENCES `centro_formacion` (`cod_centro`),
  CONSTRAINT `grupo_ibfk_2` FOREIGN KEY (`cod_programa`, `la_version`) REFERENCES `programa_formacion` (`cod_programa`, `la_version`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3;


-- gestion_formacion.programa_competencia definition

CREATE TABLE `programa_competencia` (
  `cod_prog_competencia` int unsigned NOT NULL,
  `cod_programa` int unsigned DEFAULT NULL,
  `la_version` tinyint unsigned DEFAULT NULL,
  `cod_competencia` int unsigned DEFAULT NULL,
  PRIMARY KEY (`cod_prog_competencia`),
  KEY `cod_programa` (`cod_programa`,`la_version`),
  KEY `cod_competencia` (`cod_competencia`),
  CONSTRAINT `programa_competencia_ibfk_1` FOREIGN KEY (`cod_programa`, `la_version`) REFERENCES `programa_formacion` (`cod_programa`, `la_version`),
  CONSTRAINT `programa_competencia_ibfk_2` FOREIGN KEY (`cod_competencia`) REFERENCES `competencia` (`cod_competencia`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3;


-- gestion_formacion.resultado_aprendizaje definition

CREATE TABLE `resultado_aprendizaje` (
  `cod_resultado` int unsigned NOT NULL,
  `nombre` varchar(30) DEFAULT NULL,
  `cod_competencia` int unsigned DEFAULT NULL,
  PRIMARY KEY (`cod_resultado`),
  KEY `cod_competencia` (`cod_competencia`),
  CONSTRAINT `resultado_aprendizaje_ibfk_1` FOREIGN KEY (`cod_competencia`) REFERENCES `competencia` (`cod_competencia`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3;


-- gestion_formacion.usuario definition

CREATE TABLE `usuario` (
  `id_usuario` int unsigned NOT NULL AUTO_INCREMENT,
  `nombre_completo` varchar(80) DEFAULT NULL,
  `identificacion` char(12) DEFAULT NULL,
  `id_rol` int unsigned DEFAULT NULL,
  `correo` varchar(100) DEFAULT NULL,
  `pass_hash` varchar(150) CHARACTER SET utf8mb3 COLLATE utf8mb3_general_ci DEFAULT NULL,
  `tipo_contrato` varchar(50) DEFAULT NULL,
  `telefono` varchar(15) DEFAULT NULL,
  `estado` tinyint(1) DEFAULT NULL,
  `cod_centro` int unsigned DEFAULT NULL,
  PRIMARY KEY (`id_usuario`),
  UNIQUE KEY `correo` (`correo`),
  KEY `id_rol` (`id_rol`),
  KEY `cod_centro` (`cod_centro`),
  CONSTRAINT `usuario_ibfk_1` FOREIGN KEY (`id_rol`) REFERENCES `rol` (`id_rol`),
  CONSTRAINT `usuario_ibfk_2` FOREIGN KEY (`cod_centro`) REFERENCES `centro_formacion` (`cod_centro`)
) ENGINE=InnoDB AUTO_INCREMENT=10 DEFAULT CHARSET=utf8mb3;


-- gestion_formacion.ambiente_formacion definition

CREATE TABLE `ambiente_formacion` (
  `id_ambiente` int unsigned NOT NULL AUTO_INCREMENT,
  `nombre_ambiente` varchar(40) DEFAULT NULL,
  `num_max_aprendices` tinyint unsigned DEFAULT NULL,
  `municipio` varchar(40) DEFAULT NULL,
  `ubicacion` varchar(80) DEFAULT NULL,
  `cod_centro` int unsigned DEFAULT NULL,
  `estado` tinyint(1) DEFAULT NULL,
  PRIMARY KEY (`id_ambiente`),
  KEY `cod_centro` (`cod_centro`),
  CONSTRAINT `ambiente_formacion_ibfk_1` FOREIGN KEY (`cod_centro`) REFERENCES `centro_formacion` (`cod_centro`)
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8mb3;


-- gestion_formacion.datos_grupo definition

CREATE TABLE `datos_grupo` (
  `cod_ficha` int unsigned NOT NULL,
  `num_aprendices_masculinos` tinyint unsigned DEFAULT NULL,
  `num_aprendices_femenino` tinyint unsigned DEFAULT NULL,
  `num_aprendices_no_binario` tinyint unsigned DEFAULT NULL,
  `num_total_aprendices` tinyint unsigned DEFAULT NULL,
  `num_total_aprendices_activos` tinyint unsigned DEFAULT NULL,
  `cupo_total` tinyint unsigned DEFAULT NULL,
  `en_transito` tinyint unsigned DEFAULT NULL,
  `induccion` tinyint unsigned DEFAULT NULL,
  `formacion` tinyint unsigned DEFAULT NULL,
  `condicionado` tinyint unsigned DEFAULT NULL,
  `aplazado` tinyint unsigned DEFAULT NULL,
  `retiro_voluntuario` tinyint unsigned DEFAULT NULL,
  `cancelado` tinyint unsigned DEFAULT NULL,
  `cancelamiento_vit_comp` tinyint unsigned DEFAULT NULL,
  `desercion_vit_comp` tinyint unsigned DEFAULT NULL,
  `por_certificar` tinyint unsigned DEFAULT NULL,
  `certificados` tinyint unsigned DEFAULT NULL,
  `traslados` tinyint unsigned DEFAULT NULL,
  `otro` tinyint unsigned DEFAULT NULL,
  PRIMARY KEY (`cod_ficha`),
  CONSTRAINT `datos_grupo_ibfk_1` FOREIGN KEY (`cod_ficha`) REFERENCES `grupo` (`cod_ficha`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3;


-- gestion_formacion.programacion definition

CREATE TABLE `programacion` (
  `id_programacion` int unsigned NOT NULL AUTO_INCREMENT,
  `id_instructor` int unsigned DEFAULT NULL,
  `cod_ficha` int unsigned DEFAULT NULL,
  `fecha_programada` date DEFAULT NULL,
  `horas_programadas` int DEFAULT NULL,
  `hora_inicio` time DEFAULT NULL,
  `hora_fin` time DEFAULT NULL,
  `cod_competencia` int unsigned DEFAULT NULL,
  `cod_resultado` int unsigned DEFAULT NULL,
  `id_user` int unsigned DEFAULT NULL,
  PRIMARY KEY (`id_programacion`),
  KEY `id_instructor` (`id_instructor`),
  KEY `cod_ficha` (`cod_ficha`),
  KEY `cod_competencia` (`cod_competencia`),
  KEY `cod_resultado` (`cod_resultado`),
  KEY `id_user` (`id_user`),
  CONSTRAINT `programacion_ibfk_1` FOREIGN KEY (`id_instructor`) REFERENCES `usuario` (`id_usuario`),
  CONSTRAINT `programacion_ibfk_2` FOREIGN KEY (`cod_ficha`) REFERENCES `grupo` (`cod_ficha`),
  CONSTRAINT `programacion_ibfk_3` FOREIGN KEY (`cod_competencia`) REFERENCES `competencia` (`cod_competencia`),
  CONSTRAINT `programacion_ibfk_4` FOREIGN KEY (`cod_resultado`) REFERENCES `resultado_aprendizaje` (`cod_resultado`),
  CONSTRAINT `programacion_ibfk_5` FOREIGN KEY (`id_user`) REFERENCES `usuario` (`id_usuario`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3;