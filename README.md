# Prototipo B-HDT de confort

Gemelo digital edificio-humano para ensayar prácticas de confort residencial en México. Creado por la Dra. Juana Isabel Méndez Garduño, Tecnológico de Monterrey, 2026.



Dos páginas.
- `index.html`, versión para público general, en verano (julio y agosto, aire acondicionado) e invierno (enero y febrero, calefacción con minisplit de bomba de calor y tarifa fuera de verano). Tres pasos (tu casa hoy, tus opciones, antes de decidir) y cuatro perspectivas con rol que corresponden a las dimensiones del marco. Especialista en confort (habitabilidad), Ingeniera de la vivienda (factibilidad técnica), Mediadora del hogar (legitimidad social) y Asesor de tarifa (gobernanza y costo).
- `laboratorio.html`, versión para investigadores con calibración, casos guiados, bitácora y lectura con LLM.

Demo del marco Building–Human Digital Twin (B-HDT) para prácticas de confort residencial. Recorrido ilustrativo; el clima y la envolvente provienen del modelo de Honeybee, mientras que el hogar, las prácticas y los testimonios son sintéticos.

## Clima de cualquier lugar

La página ofrece tres caminos.
1. Buscar un lugar o usar la ubicación del dispositivo. El navegador consulta el geocodificador y el archivo histórico de Open-Meteo (ERA5, año 2025, hora por hora) y calcula la temperatura de cielo con Berdahl y Martin. Funciona en GitHub Pages porque Open-Meteo permite llamadas desde el navegador.
2. Climas típicos preparados con PVGIS. PVGIS no acepta llamadas desde el navegador, así que `tools/pvgis_epw.py` (adaptado del componente de Ladybug) se ejecuta desde la acción de GitHub "Agregar clima PVGIS" (pestaña Actions, botón Run workflow, con coordenadas y nombre). La acción guarda el EPW en `epw/` y lo registra en `epw/index.json`; la página lo muestra en "Otras fuentes de clima".
3. Subir un EPW propio.

En todos los casos se simula la misma casa modelo; sus parámetros se calibraron con el clima de Monterrey. La tarifa sigue siendo la 1C de verano.

## Capas de voz

El registro distingue tres capas que nunca se promedian.
- Testimonios del hogar (T), sintéticos y editables.
- Voces públicas (V), personas reales de Monterrey tomadas de prensa local. Los comentarios de redes van parafraseados y sin nombre de usuario, siguiendo las guías de ética de AoIR; las citas de prensa van literales con su fuente.
- Estadística poblacional (E), ENCEVI 2018 de INEGI vía la infografía de CONUEE.

## Modelo térmico

Modelo 2R2C de las tres zonas acondicionadas (63.2 m²), ajustado por mínimos cuadrados contra las cargas horarias de EnergyPlus del caso 22/18 °C y verificado en modo de control contra los casos 26/18 °C y aire ideal, y en cargas contra el caso custom.

| Caso | Rol | NMBE mensual | CV(RMSE) mensual | NMBE horario | CV(RMSE) horario |
|---|---|---|---|---|---|
| 22/18 °C | entrenamiento (control) | 0.6% | 6.0% | 0.6% | 19.6% |
| 26/18 °C | validación (control) | −1.4% | 11.0% | −1.3% | 35.6% |
| Aire ideal 24.4/21.7 °C | validación (control) | −0.9% | 7.4% | −0.8% | 27.5% |
| Custom, apagado 7 a 13 h | validación (cargas) | −4.0% | 9.6% | −3.7% | 30.4% |

Valores de enfriamiento. Corridas con tabique rojo recocido de 12 cm con aplanados (15 cm), vidrio claro sencillo de 6 mm (U 5.80, SHGC 0.816) y muros sin capas de convección. El horario de 26/18 °C rebasa por poco el 30%; el mensual cumple en los cuatro casos.

Criterios de ASHRAE Guideline 14 con p = 1. Mensual ±5% y 15%; horario ±10% y 30%. Mide la fidelidad del sustituto frente a EnergyPlus, no una calibración contra mediciones.

Supuestos físicos clave
- Carga total de enfriamiento igual a la sensible entre 0.7, la razón de calor sensible por defecto de `ZoneHVAC:IdealLoadsAirSystem`.
- Solar por ventanas proporcional a la irradiancia sobre la fachada sur (R² = 0.94 contra EnergyPlus).
- Ganancias internas y consumo de iluminación y equipos tomados de los horarios del modelo.
- La ventilación por ventanas del modelo de Honeybee entra como dato conocido durante la calibración; en la demo solo existe si la práctica abre ventanas.


## Autoría y cita

Concepto, diseño, modelo térmico, calibración y desarrollo de la Dra. Juana Isabel Méndez Garduño, Escuela de Arquitectura, Arte y Diseño, Tecnológico de Monterrey. La casa modelo deriva de Méndez, J. I., Ibarra, L., Ponce, P., Meier, A., & Molina, A. (2024), Heliyon, 10, e31599.

Cita sugerida. Méndez, J. I. (2026). Tu recibo de luz, prototipo de gemelo digital edificio-humano [Software]. GitHub.

## Criterios de confort y reglas para la IA

- Despierto con el aire apagado: modelo adaptativo de ASHRAE 55-2020 al 80% de aceptabilidad, límite superior 0.31·Tpma + 17.8 + 3.5 °C, con Tpma como media móvil exponencial (α = 0.8) de la temperatura exterior diaria, acotada entre 10 y 33.5 °C. Con ventilador se suman 1.8 °C.
- Dormir, de 23 a 7 h: no más de 26 °C (CIBSE TM59 para recámaras), 27.8 °C con ventilador.
- Invierno: mínimo 18 °C (OMS, Housing and Health Guidelines, 2018).
- Con el aire encendido manda el setpoint.

Las lecturas con IA y el asistente reciben estos criterios como un item fijo del registro (N1) y reglas obligatorias de salud, seguridad, dinero, privacidad y género. No pueden proponer umbrales propios, prometer ahorros, sugerir ventanas abiertas si el hogar dijo que no es seguro, calentadores de combustión en cuartos cerrados ni manipular la instalación eléctrica. La revisión automática rechaza números que no estén en el registro.
