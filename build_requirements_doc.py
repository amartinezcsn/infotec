from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_BREAK, WD_LINE_SPACING
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_CELL_VERTICAL_ALIGNMENT
from docx.enum.section import WD_SECTION
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.enum.style import WD_STYLE_TYPE
from docx.enum.text import WD_TAB_ALIGNMENT
from docx.enum.text import WD_TAB_LEADER
from docx.enum.section import WD_ORIENT
from pathlib import Path
from datetime import date


OUT = Path(r"C:\Infotec\Documento_de_requerimientos_proyecto_IA_Microsoft_Foundry.docx")

NAVY = "17365D"
BLUE = "2F75B5"
PALE_BLUE = "EAF2F8"
PALE_GRAY = "F4F6F7"
MID_GRAY = "6B7280"
LIGHT_BORDER = "D9D9D9"
WHITE = "FFFFFF"
BLACK = "000000"


def set_cell_shading(cell, fill):
    tc_pr = cell._tc.get_or_add_tcPr()
    shd = tc_pr.find(qn("w:shd"))
    if shd is None:
        shd = OxmlElement("w:shd")
        tc_pr.append(shd)
    shd.set(qn("w:fill"), fill)


def set_cell_margins(cell, top=110, start=120, bottom=110, end=120):
    tc = cell._tc
    tc_pr = tc.get_or_add_tcPr()
    tc_mar = tc_pr.first_child_found_in("w:tcMar")
    if tc_mar is None:
        tc_mar = OxmlElement("w:tcMar")
        tc_pr.append(tc_mar)
    for margin, value in (("top", top), ("start", start), ("bottom", bottom), ("end", end)):
        node = tc_mar.find(qn(f"w:{margin}"))
        if node is None:
            node = OxmlElement(f"w:{margin}")
            tc_mar.append(node)
        node.set(qn("w:w"), str(value))
        node.set(qn("w:type"), "dxa")


def set_table_borders(table, color=LIGHT_BORDER, size="6"):
    tbl_pr = table._tbl.tblPr
    borders = tbl_pr.first_child_found_in("w:tblBorders")
    if borders is None:
        borders = OxmlElement("w:tblBorders")
        tbl_pr.append(borders)
    for edge in ("top", "left", "bottom", "right", "insideH", "insideV"):
        tag = f"w:{edge}"
        element = borders.find(qn(tag))
        if element is None:
            element = OxmlElement(tag)
            borders.append(element)
        element.set(qn("w:val"), "single")
        element.set(qn("w:sz"), size)
        element.set(qn("w:space"), "0")
        element.set(qn("w:color"), color)


def set_repeat_table_header(row):
    tr_pr = row._tr.get_or_add_trPr()
    tbl_header = OxmlElement("w:tblHeader")
    tbl_header.set(qn("w:val"), "true")
    tr_pr.append(tbl_header)


def set_cell_width(cell, inches):
    tc_pr = cell._tc.get_or_add_tcPr()
    tc_w = tc_pr.find(qn("w:tcW"))
    if tc_w is None:
        tc_w = OxmlElement("w:tcW")
        tc_pr.append(tc_w)
    tc_w.set(qn("w:w"), str(int(inches * 1440)))
    tc_w.set(qn("w:type"), "dxa")


def no_row_split(row):
    tr_pr = row._tr.get_or_add_trPr()
    cant_split = OxmlElement("w:cantSplit")
    tr_pr.append(cant_split)


def add_hyperlink(paragraph, text, url):
    part = paragraph.part
    rel_id = part.relate_to(url, "http://schemas.openxmlformats.org/officeDocument/2006/relationships/hyperlink", is_external=True)
    hyperlink = OxmlElement("w:hyperlink")
    hyperlink.set(qn("r:id"), rel_id)
    new_run = OxmlElement("w:r")
    r_pr = OxmlElement("w:rPr")
    color = OxmlElement("w:color")
    color.set(qn("w:val"), BLUE)
    r_pr.append(color)
    underline = OxmlElement("w:u")
    underline.set(qn("w:val"), "single")
    r_pr.append(underline)
    new_run.append(r_pr)
    text_node = OxmlElement("w:t")
    text_node.text = text
    new_run.append(text_node)
    hyperlink.append(new_run)
    paragraph._p.append(hyperlink)
    return hyperlink


def add_page_number(paragraph):
    run = paragraph.add_run()
    fld_char1 = OxmlElement("w:fldChar")
    fld_char1.set(qn("w:fldCharType"), "begin")
    instr_text = OxmlElement("w:instrText")
    instr_text.set(qn("xml:space"), "preserve")
    instr_text.text = " PAGE "
    fld_char2 = OxmlElement("w:fldChar")
    fld_char2.set(qn("w:fldCharType"), "end")
    run._r.extend([fld_char1, instr_text, fld_char2])


def set_keep_with_next(paragraph):
    p_pr = paragraph._p.get_or_add_pPr()
    keep = OxmlElement("w:keepNext")
    p_pr.append(keep)


def remove_paragraph_borders(paragraph):
    p_pr = paragraph._p.get_or_add_pPr()
    p_bdr = p_pr.find(qn("w:pBdr"))
    if p_bdr is not None:
        p_pr.remove(p_bdr)


def configure_document(doc):
    section = doc.sections[0]
    section.top_margin = Inches(0.72)
    section.bottom_margin = Inches(0.68)
    section.left_margin = Inches(0.78)
    section.right_margin = Inches(0.78)
    section.header_distance = Inches(0.3)
    section.footer_distance = Inches(0.3)

    styles = doc.styles
    normal = styles["Normal"]
    normal.font.name = "Aptos"
    normal._element.rPr.rFonts.set(qn("w:ascii"), "Aptos")
    normal._element.rPr.rFonts.set(qn("w:hAnsi"), "Aptos")
    normal.font.size = Pt(9.4)
    normal.font.color.rgb = RGBColor.from_string(BLACK)
    normal.paragraph_format.space_after = Pt(5)
    normal.paragraph_format.line_spacing = 1.08

    title = styles["Title"]
    title.font.name = "Aptos Display"
    title._element.rPr.rFonts.set(qn("w:ascii"), "Aptos Display")
    title._element.rPr.rFonts.set(qn("w:hAnsi"), "Aptos Display")
    title.font.size = Pt(27)
    title.font.bold = True
    title.font.color.rgb = RGBColor.from_string(BLACK)
    title.paragraph_format.space_after = Pt(14)

    for name, size, before, after in (("Heading 1", 17, 16, 7), ("Heading 2", 13, 11, 5), ("Heading 3", 10.5, 8, 3)):
        st = styles[name]
        st.font.name = "Aptos Display"
        st._element.rPr.rFonts.set(qn("w:ascii"), "Aptos Display")
        st._element.rPr.rFonts.set(qn("w:hAnsi"), "Aptos Display")
        st.font.size = Pt(size)
        st.font.bold = True
        st.font.color.rgb = RGBColor.from_string(BLACK)
        st.paragraph_format.space_before = Pt(before)
        st.paragraph_format.space_after = Pt(after)
        st.paragraph_format.keep_with_next = True

    for name in ("List Bullet", "List Number"):
        st = styles[name]
        st.font.name = "Aptos"
        st.font.size = Pt(9.4)
        st.paragraph_format.space_after = Pt(2.5)

    if "Requirement ID" not in styles:
        req = styles.add_style("Requirement ID", WD_STYLE_TYPE.CHARACTER)
        req.font.name = "Aptos"
        req.font.size = Pt(8.5)
        req.font.bold = True
        req.font.color.rgb = RGBColor.from_string(NAVY)


def add_footer(doc):
    for section in doc.sections:
        footer = section.footer
        table = footer.add_table(rows=1, cols=2, width=Inches(6.8))
        table.alignment = WD_TABLE_ALIGNMENT.CENTER
        table.autofit = False
        set_cell_width(table.cell(0, 0), 5.9)
        set_cell_width(table.cell(0, 1), 0.9)
        left = table.cell(0, 0).paragraphs[0]
        left.alignment = WD_ALIGN_PARAGRAPH.LEFT
        run = left.add_run("Requerimientos del proyecto de IA con Microsoft Foundry")
        run.font.name = "Aptos"
        run.font.size = Pt(7.5)
        run.font.color.rgb = RGBColor.from_string(MID_GRAY)
        right = table.cell(0, 1).paragraphs[0]
        right.alignment = WD_ALIGN_PARAGRAPH.RIGHT
        r = right.add_run("Página ")
        r.font.size = Pt(7.5)
        r.font.color.rgb = RGBColor.from_string(MID_GRAY)
        add_page_number(right)
        for cell in table.rows[0].cells:
            tc_pr = cell._tc.get_or_add_tcPr()
            borders = OxmlElement("w:tcBorders")
            for edge in ("top", "left", "bottom", "right", "insideH", "insideV"):
                e = OxmlElement(f"w:{edge}")
                e.set(qn("w:val"), "nil")
                borders.append(e)
            tc_pr.append(borders)


def add_para(doc, text="", bold_lead=None, style=None):
    p = doc.add_paragraph(style=style)
    if bold_lead and text.startswith(bold_lead):
        p.add_run(bold_lead).bold = True
        p.add_run(text[len(bold_lead):])
    else:
        p.add_run(text)
    return p


def add_bullets(doc, items, level=0):
    for item in items:
        p = doc.add_paragraph(style="List Bullet" if level == 0 else "List Bullet 2")
        if isinstance(item, tuple):
            lead, rest = item
            p.add_run(lead).bold = True
            p.add_run(rest)
        else:
            p.add_run(item)


def add_table(doc, headers, rows, widths=None, font_size=8.2, header_fill=NAVY, header_text=WHITE, repeat=True):
    table = doc.add_table(rows=1, cols=len(headers))
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    table.autofit = False
    set_table_borders(table)
    hdr = table.rows[0]
    if repeat:
        set_repeat_table_header(hdr)
    for i, text in enumerate(headers):
        cell = hdr.cells[i]
        set_cell_shading(cell, header_fill)
        set_cell_margins(cell)
        cell.vertical_alignment = WD_CELL_VERTICAL_ALIGNMENT.CENTER
        if widths:
            set_cell_width(cell, widths[i])
        p = cell.paragraphs[0]
        set_keep_with_next(p)
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p.paragraph_format.space_after = Pt(0)
        r = p.add_run(str(text))
        r.bold = True
        r.font.size = Pt(font_size)
        r.font.color.rgb = RGBColor.from_string(header_text)
    for row_idx, row_data in enumerate(rows):
        row = table.add_row()
        no_row_split(row)
        for i, value in enumerate(row_data):
            cell = row.cells[i]
            if row_idx % 2 == 1:
                set_cell_shading(cell, PALE_BLUE)
            set_cell_margins(cell)
            cell.vertical_alignment = WD_CELL_VERTICAL_ALIGNMENT.CENTER
            if widths:
                set_cell_width(cell, widths[i])
            p = cell.paragraphs[0]
            p.paragraph_format.space_after = Pt(0)
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER if i == 0 and len(headers) > 2 else WD_ALIGN_PARAGRAPH.LEFT
            r = p.add_run(str(value))
            r.font.size = Pt(font_size)
            if i == 0 and str(value).startswith(("F1-", "F2-", "RF-", "RNF-", "SEG-", "DAT-", "ACE-", "R-")):
                r.bold = True
                r.font.color.rgb = RGBColor.from_string(NAVY)
    doc.add_paragraph().paragraph_format.space_after = Pt(1)
    return table


def add_section_break(doc):
    p = doc.add_paragraph()
    p.add_run().add_break(WD_BREAK.PAGE)


def build():
    doc = Document()
    configure_document(doc)
    doc.core_properties.title = "Documento de requerimientos para la construcción de una solución de inteligencia artificial con Microsoft Foundry"
    doc.core_properties.subject = "Requerimientos integrales de Fase 1 y Fase 2"
    doc.core_properties.author = "Infotec"
    doc.core_properties.keywords = "Microsoft Foundry, agentes de IA, Azure, requerimientos, arquitectura, Fase 1, Fase 2"

    p = doc.add_paragraph(style="Title")
    p.add_run("Documento de requerimientos para la construcción de una solución de inteligencia artificial con Microsoft Foundry")
    remove_paragraph_borders(p)
    title_style_ppr = doc.styles["Title"]._element.get_or_add_pPr()
    title_style_border = title_style_ppr.find(qn("w:pBdr"))
    if title_style_border is not None:
        title_style_ppr.remove(title_style_border)
    sub = doc.add_paragraph()
    sub.alignment = WD_ALIGN_PARAGRAPH.LEFT
    r = sub.add_run("Alcance integral de Fase 1 y Fase 2")
    r.bold = True
    r.font.size = Pt(15)
    r.font.color.rgb = RGBColor.from_string(NAVY)
    p2 = doc.add_paragraph()
    p2.paragraph_format.space_before = Pt(18)
    p2.add_run("Propósito  ").bold = True
    p2.add_run("Definir el alcance funcional, técnico y operativo necesario para planear y construir un producto de IA basado en agentes, Microsoft Foundry y servicios de Microsoft Azure.")
    p3 = doc.add_paragraph()
    p3.add_run("Base de análisis  ").bold = True
    p3.add_run("Dieciséis archivos de transcripción del curso Fundamentos de IA con Tecnologías Microsoft y documentación oficial vigente de Microsoft consultada el 7 de noviembre de 2026.")
    p4 = doc.add_paragraph()
    p4.add_run("Estado  ").bold = True
    p4.add_run("Línea base para estimación, diseño, backlog y construcción. Requiere validación de las decisiones abiertas señaladas en la sección 18.")
    p5 = doc.add_paragraph()
    p5.paragraph_format.space_before = Pt(28)
    r = p5.add_run("Versión 1.0")
    r.font.size = Pt(11)
    r.bold = True
    p6 = doc.add_paragraph("7 de noviembre de 2026")
    p6.runs[0].font.size = Pt(10)
    p6.runs[0].font.color.rgb = RGBColor.from_string(MID_GRAY)

    add_section_break(doc)

    doc.add_heading("Control del documento", level=1)
    add_table(doc,
              ["Campo", "Valor"],
              [
                  ["Objetivo", "Convertir las instrucciones dispersas del curso en una especificación ejecutable y trazable."],
                  ["Audiencia", "Responsables de producto, arquitectura, desarrollo, datos, seguridad, operaciones, evaluación y patrocinio."],
                  ["Alcance", "Fase 1 de descubrimiento y planeación; Fase 2 de construcción, despliegue, validación y evidencia."],
                  ["Convención", "E = explícito en transcripción; D = derivado necesario para hacerlo construible; P = propuesta recomendada."],
                  ["Idioma", "Español como idioma principal de la solución y de sus evidencias."],
              ], widths=[1.45, 5.35], font_size=8.7, header_fill=BLUE)

    doc.add_heading("Resumen ejecutivo", level=1)
    add_para(doc, "El proyecto se divide en dos resultados consecutivos. La Fase 1 produce un plan de adopción de inteligencia artificial para una organización que parte sin capacidades de IA. La Fase 2 convierte ese plan o un caso alternativo en una solución utilizable, desplegada en Azure, accesible como producto y respaldada por documentación. La entrega no puede limitarse a código o a una presentación: debe poder probarse como lo haría un usuario final.")
    add_para(doc, "La línea base recomendada es una plataforma multiagente para Distribuidora Río Claro, empresa ficticia de productos de limpieza e higiene con 22 años, 140 empleados, cinco sucursales, alrededor de 60 proveedores y 1,800 clientes activos. La primera versión integra captura y control de facturas, un asistente para clientes y empleados, consulta móvil y por voz, normalización de catálogo e inventario y reportes consistentes entre sucursales, con aprobación humana antes de acciones sensibles.")
    add_para(doc, "La arquitectura utiliza Microsoft Foundry Agent Service para alojar agentes, Microsoft Agent Framework para orquestar el flujo, Azure Document Intelligence para comprender documentos, Azure AI Search para recuperación aumentada con generación, Azure App Service para la experiencia web y API, Azure SQL y Blob Storage para datos, Microsoft Entra ID y Managed Identities para acceso, Key Vault para secretos y Azure Monitor con Application Insights para trazas, métricas y evaluaciones.")

    doc.add_heading("Contenido", level=1)
    add_bullets(doc, [
        "1 Origen alcance y nivel de certeza",
        "2 Contexto y visión del producto",
        "3 Requerimientos de la Fase 1",
        "4 Requerimientos de la Fase 2",
        "5 Alcance funcional recomendado del MVP",
        "6 Usuarios y recorridos",
        "7 Requerimientos funcionales",
        "8 Arquitectura de agentes",
        "9 Arquitectura tecnológica Microsoft",
        "10 Datos integraciones y contratos",
        "11 Requerimientos no funcionales",
        "12 Seguridad privacidad e IA responsable",
        "13 Evaluación pruebas y observabilidad",
        "14 Criterios de aceptación",
        "15 Plan de construcción asistido por agentes",
        "16 Backlog hitos y entregables",
        "17 Riesgos dependencias y mitigaciones",
        "18 Decisiones abiertas",
        "19 Matriz de trazabilidad",
        "Anexos de fuentes y referencias técnicas",
    ])

    doc.add_heading("1 Origen alcance y nivel de certeza", level=1)
    add_para(doc, "El requerimiento fue reconstruido a partir de las transcripciones disponibles y del PDF final de Distribuidora Río Claro. No se encontró el archivo de transcripción numerado como 4. El documento separa la evidencia directa de las decisiones técnicas necesarias para convertir el encargo en un proyecto construible.")
    add_table(doc,
              ["Clase", "Significado", "Tratamiento"],
              [
                  ["E", "Requerimiento explícito", "Debe cumplirse salvo aprobación formal de cambio."],
                  ["D", "Requerimiento derivado", "Se necesita para operar, asegurar o verificar la solución."],
                  ["P", "Propuesta recomendada", "Define una línea base concreta y puede sustituirse mediante decisión de arquitectura."],
              ], widths=[0.7, 2.0, 4.1], font_size=8.7)
    add_para(doc, "Hallazgo principal  ", bold_lead="Hallazgo principal  ")
    add_para(doc, "El PDF del proyecto limita la Fase 2 a dos opciones: resolver Distribuidora Río Claro o implementar con Microsoft Foundry el proyecto trabajado en la Fase 1. Para producir una especificación concreta, este documento adopta Río Claro como línea base. Si se elige la opción de Fase 1, se conserva la plataforma tecnológica y se reemplazan únicamente dominio, datos, actores y reglas de negocio mediante control de cambios.")

    doc.add_heading("2 Contexto y visión del producto", level=1)
    doc.add_heading("2.1 Contexto empresarial reconstruido", level=2)
    add_bullets(doc, [
        ("Organización  ", "Distribuidora familiar con 22 años, 140 empleados y sucursales en Guadalajara, Zapopan, León, Querétaro y Aguascalientes."),
        ("Actividad  ", "Venta de productos de limpieza e higiene a hoteles, restaurantes, escuelas y pequeñas tiendas; cerca de 60 proveedores y 1,800 clientes activos."),
        ("Capacidad técnica  ", "No existe un área de TI; una sola persona atiende soporte, correo y red."),
        ("Situación actual  ", "Facturas en correos personales y WhatsApp; catálogos Excel incompatibles por sucursal; quejas no centralizadas; políticas contradictorias; contraseñas compartidas y datos sensibles expuestos."),
        ("Motivación  ", "Recuperar velocidad de atención, evitar pagos duplicados, reducir captura manual y convertir 22 años de información en conocimiento utilizable."),
    ])
    doc.add_heading("2.2 Problema del producto", level=2)
    add_para(doc, "Las facturas llegan como PDF o foto a tres compradores y Laura dedica cerca de 12 horas semanales a renombrarlas y capturarlas, con un error aproximado de uno por cada veinte documentos. La empresa ya pagó dos veces una factura duplicada y perdió dos clientes hoteleros por falta de respuesta. Cada sucursal maneja catálogos y reportes distintos; las quejas no se registran y las políticas internas tienen versiones incompatibles. Se requiere una experiencia web y móvil que ordene los datos sin detener la operación, coordine agentes especializados, ofrezca voz, solicite aprobación humana y produzca resultados verificables con evidencia de origen.")
    doc.add_heading("2.3 Visión", level=2)
    add_para(doc, "Proveer una plataforma web segura que permita a una persona cargar un comprobante o consultar información empresarial; que un orquestador delegue el trabajo a agentes especializados; y que el sistema entregue una respuesta explicable, un registro estructurado o un borrador de operación listo para revisión humana.")
    doc.add_heading("2.4 Inventario del desorden", level=2)
    add_table(doc,
              ["Fuente", "Situación actual", "Consecuencia"],
              [
                  ["Facturas", "PDF y fotos en correos personales, sin carpeta ni nombre estándar.", "Datos no estructurados y riesgo de duplicidad."],
                  ["Catálogo", "Un Excel por sucursal con columnas, nombres y claves diferentes.", "Precios y existencias contradictorios."],
                  ["Quejas", "WhatsApp, llamadas y correos sin repositorio central.", "No hay seguimiento, análisis de sentimiento ni detección de recurrencia."],
                  ["Políticas", "Documentos Word desactualizados en USB y conocimiento informal.", "El agente puede responder con una versión incorrecta."],
                  ["Permisos", "Contraseña compartida para nómina, precios y datos de clientes.", "Exposición de datos y ausencia de trazabilidad individual."],
              ], widths=[1.15, 3.55, 2.1], font_size=7.9)
    doc.add_heading("2.5 Restricciones del caso", level=2)
    add_bullets(doc, [
        "El piloto tiene presupuesto limitado y cada servicio de Azure debe justificarse.",
        "La empresa no cuenta con personal técnico especializado; la operación debe ser sencilla.",
        "Parte del personal de bodega y ventas trabaja desde el celular o mediante voz.",
        "La operación no puede detenerse mientras se ordenan y migran los datos.",
        "La solución debe reforzar la confianza: la IA apoya, muestra evidencia y una persona revisa.",
    ])
    doc.add_heading("2.6 Objetivos medibles", level=2)
    add_table(doc,
              ["Objetivo", "Indicador inicial", "Meta de MVP"],
              [
                  ["Reducir captura manual", "Minutos por documento", "Reducir al menos 60 por ciento en un conjunto piloto."],
                  ["Mejorar calidad de datos", "Campos válidos por documento", "Al menos 90 por ciento en campos prioritarios del conjunto de prueba."],
                  ["Aumentar trazabilidad", "Operaciones con evidencia y auditoría", "100 por ciento de las ejecuciones del MVP."],
                  ["Acelerar atención", "Tiempo de primera respuesta", "Menos de 15 minutos en el piloto."],
                  ["Unificar información", "Sucursales con catálogo y reporte coherentes", "Cinco sucursales sobre una fuente normalizada."],
                  ["Evitar acciones no autorizadas", "Operaciones sensibles con aprobación", "100 por ciento antes de simular emisión o cierre."],
                  ["Entregar respuestas fundamentadas", "Respuestas de conocimiento con cita", "Al menos 95 por ciento cuando exista fuente aplicable."],
              ], widths=[2.0, 2.1, 2.7], font_size=8.2)

    doc.add_heading("3 Requerimientos de la Fase 1", level=1)
    add_para(doc, "La Fase 1 es un ejercicio de diagnóstico y planeación. Su producto principal no es una aplicación operativa, sino un plan de implementación de IA desde cero para una empresa que aún no utiliza estas capacidades.")
    add_table(doc,
              ["ID", "Tipo", "Requerimiento", "Evidencia de cumplimiento"],
              [
                  ["F1-01", "E", "Seleccionar una empresa ficticia, propia o conocida. Si se usa información real, respetar acuerdos de confidencialidad.", "Descripción de empresa y declaración de tratamiento de datos."],
                  ["F1-02", "E", "Asumir que la organización inicia sin una implementación previa de IA.", "Línea base de madurez y capacidades actuales."],
                  ["F1-03", "E", "Elaborar un plan de implementación de IA desde cero y adaptado al giro de la empresa.", "Documento con etapas, responsables, dependencias y resultados."],
                  ["F1-04", "E", "Usar Microsoft Copilot como herramienta principal de apoyo y revisar críticamente su salida.", "Registro de prompts, respuestas útiles, correcciones y decisiones humanas."],
                  ["F1-05", "E", "Entregar evidencia de los prompts y del proceso seguido.", "Anexo de prompts o capturas legibles y vinculadas con decisiones."],
                  ["F1-06", "D", "Identificar procesos, dolores, datos, riesgos y oportunidades antes de seleccionar tecnología.", "Mapa de procesos y cartera priorizada de casos de uso."],
                  ["F1-07", "D", "Definir arquitectura objetivo, gobierno, seguridad, IA responsable, métricas, costos y plan de cambio.", "Secciones específicas y decisiones trazables."],
                  ["F1-08", "E", "La entrega original se planteó como individual y en formato Word o PDF compartido desde OneDrive mediante formulario.", "Archivo legible, enlace accesible y metadatos de autor."],
                  ["F1-09", "D", "Cerrar la fase con un caso implementable; en Fase 2 podrá construirse ese proyecto o el caso Río Claro.", "Acta de priorización y alcance del MVP."],
              ], widths=[0.72, 0.55, 3.65, 1.9], font_size=7.7)

    doc.add_heading("3.1 Contenido mínimo del plan de Fase 1", level=2)
    add_bullets(doc, [
        "Resumen ejecutivo y decisión solicitada.",
        "Descripción de la empresa, usuarios, sucursales, procesos y situación tecnológica.",
        "Inventario de problemas y datos disponibles con clasificación de sensibilidad.",
        "Matriz de casos de uso valor versus factibilidad y selección del MVP.",
        "Arquitectura conceptual Microsoft y justificación de cada servicio.",
        "Modelo operativo de agentes, herramientas, límites y aprobaciones humanas.",
        "Riesgos de seguridad, privacidad, sesgo, alucinación, abuso y dependencia tecnológica.",
        "Roadmap, estimación de costos, indicadores de éxito, responsables y estrategia de adopción.",
        "Evidencias de Copilot y registro de cambios realizados por criterio humano.",
    ])

    doc.add_heading("4 Requerimientos de la Fase 2", level=1)
    add_para(doc, "La Fase 2 exige materializar una solución de IA. Solo se admite continuar el proyecto trabajado en la Fase 1 o resolver el caso de Distribuidora Río Claro. En ambos casos la solución debe ser utilizable, estar desplegada y demostrar la integración de inteligencia artificial con Microsoft Foundry y Azure.")
    add_para(doc, "El PDF permite que el prototipo académico omita un login completo y no exige calidad de producción. Este documento conserva esa flexibilidad para la evaluación del curso, pero la planeación de construcción incorpora identidad, seguridad y operación como requisitos derivados porque la solución procesa precios, datos de clientes y potencialmente nómina.")
    add_table(doc,
              ["ID", "Tipo", "Requerimiento", "Criterio verificable"],
              [
                  ["F2-01", "E", "Elegir exclusivamente una de dos opciones: Distribuidora Río Claro o el proyecto trabajado en la Fase 1.", "Opción declarada y alcance aprobado."],
                  ["F2-02", "E", "Integrar inteligencia artificial y usar al menos un agente de IA de Azure Microsoft Foundry.", "Agente invocable desde la solución y evidencia de su configuración."],
                  ["F2-03", "E", "Desplegar la solución en Azure y usar únicamente herramientas de Azure para el prototipo; proporcionar enlace funcional o instalable utilizable.", "Acceso de usuario final fuera del curso sin depender del repositorio."],
                  ["F2-04", "E", "Entregar el producto funcionando, no solamente el repositorio, el diseño o una explicación.", "Demostración end to end y pruebas de aceptación."],
                  ["F2-05", "E", "La interfaz puede ser sencilla; el valor está en que la función principal opere correctamente.", "Interfaz mínima, comprensible y sin bloqueos críticos."],
                  ["F2-06", "E", "Documentar la solución en Word o Markdown, incluyendo cómo acceder, usar y comprobar el resultado.", "Manual de usuario, arquitectura, despliegue, evidencia y limitaciones."],
                  ["F2-07", "E", "Aplicar principios de IA responsable y no presentar una simulación como operación regulada real.", "Avisos, aprobación humana, límites y registro de decisiones."],
                  ["F2-08", "E", "El trabajo puede realizarse de manera individual o en equipo de hasta cuatro personas, con el mismo nivel de exigencia.", "Lista de participantes, roles y contribuciones."],
                  ["F2-09", "E", "Administrar los créditos de Azure y detener o eliminar recursos con cobro continuo cuando no se utilicen.", "Presupuesto, alertas y guía de apagado o eliminación."],
                  ["F2-10", "E", "La entrega vence el viernes 6 de noviembre a las 23:45, hora del centro de México, mediante el canal de Teams Entrega tu proyecto fase 2.", "Enlace o paquete colocado antes del cierre."],
                  ["F2-13", "E", "La documentación de entrega debe ser Markdown e incluir imágenes, capturas, explicación de la solución y problema resuelto.", "Archivo Markdown completo; otro formato no sustituye este entregable."],
                  ["F2-14", "E", "No cuentan como prototipo un video, capturas aisladas, una demo dentro del portal de Azure o código que deba ejecutarse en la computadora del estudiante.", "Prueba desde un dispositivo externo como usuario normal."],
                  ["F2-11", "D", "Incluir pruebas, observabilidad y evidencia reproducible para demostrar que el agente funciona fuera del entorno de diseño.", "Resultados de evaluación, trazas y tablero de operación."],
                  ["F2-12", "D", "Versionar código, prompts, configuración y despliegue aunque el repositorio no sea el entregable principal.", "Repositorio privado o controlado con historial y pipeline."],
              ], widths=[0.72, 0.55, 3.65, 1.9], font_size=7.45)

    doc.add_heading("5 Alcance funcional recomendado del MVP", level=1)
    add_para(doc, "Para la opción Río Claro, el prototipo debe atender los objetivos de cuentas por pagar, servicio al cliente, bodega, dirección y soporte. La construcción puede organizarse por épicas, pero la demostración final debe integrar los recorridos en una experiencia accesible para un usuario normal.")
    doc.add_heading("5.1 Flujo principal", level=2)
    add_table(doc,
              ["Paso", "Interacción", "Resultado"],
              [
                  ["1", "El usuario inicia sesión y carga una imagen o PDF de ticket, recibo o factura.", "Archivo almacenado con identificador y metadatos."],
                  ["2", "El agente orquestador clasifica la intención y delega el análisis documental.", "Tipo de documento y plan de ejecución."],
                  ["3", "Document Intelligence extrae campos, líneas, importes y fechas.", "JSON estructurado con confianza por campo."],
                  ["4", "El agente validador aplica reglas, detecta faltantes, duplicados y discrepancias.", "Resultado válido, observado o rechazado con explicación."],
                  ["5", "El agente de conocimiento consulta políticas, catálogo, pedidos e inventario mediante RAG y fuentes estructuradas.", "Respuesta fundamentada y citas a fuentes autorizadas."],
                  ["6", "El agente de facturación genera un borrador simulado o registro de gasto.", "Vista previa claramente marcada como no fiscal."],
                  ["7", "Una persona aprueba, corrige o rechaza la acción.", "Decisión, responsable, fecha y comentarios."],
                  ["8", "El sistema conserva trazas, métricas y resultado final; consolida indicadores para dirección.", "Auditoría, evidencia y reporte coherente entre sucursales."],
              ], widths=[0.55, 3.65, 2.6], font_size=8.0)

    doc.add_heading("5.2 Fuera del MVP", level=2)
    add_bullets(doc, [
        "Timbrado fiscal real ante el SAT, emisión de CFDI o manejo de certificados fiscales de producción.",
        "Procesamiento de pagos, transferencias bancarias o decisiones financieras autónomas.",
        "Integración pagada con WhatsApp; el prototipo ofrece web móvil, voz y notificación en Teams con herramientas de Azure.",
        "Alta disponibilidad multirregión, soporte para diez mil usuarios o certificación formal de ciberseguridad.",
        "Sustitución completa de ERP, CRM, nómina o inventario existente.",
        "Uso de datos personales reales no anonimizados durante demostraciones o pruebas.",
    ])

    doc.add_heading("6 Usuarios y recorridos", level=1)
    add_table(doc,
              ["Actor", "Necesidad", "Permisos y límites"],
              [
                  ["Capturista o empleado", "Cargar documentos, consultar estado y corregir campos permitidos.", "Ve únicamente documentos propios o de su sucursal."],
                  ["Cliente o vendedor", "Consultar pedido, política o producto y registrar una queja.", "Acceso solo a información del cliente y fuentes públicas autorizadas."],
                  ["Jefe de bodega", "Preguntar por voz desde el celular por existencia de productos.", "Solo inventario y operaciones de su ámbito."],
                  ["Dirección", "Consultar reporte uniforme de ventas y costo del piloto.", "Datos agregados de las cinco sucursales."],
                  ["Supervisor", "Revisar validaciones y aprobar o rechazar borradores.", "No modifica configuración de agentes ni secretos."],
                  ["Analista administrativo", "Consultar gastos, exportar registros y revisar excepciones.", "Acceso a datos asignados; exportación auditada."],
                  ["Administrador funcional", "Gestionar reglas, catálogos y fuentes de conocimiento.", "Cambios versionados y sujetos a aprobación."],
                  ["Administrador técnico", "Operar recursos, despliegues, monitoreo y acceso.", "Privilegio mínimo y separación de funciones."],
                  ["Auditor o evaluador", "Reproducir escenarios y revisar trazas, métricas y decisiones.", "Solo lectura; datos de prueba anonimizados."],
              ], widths=[1.5, 3.0, 2.3], font_size=8.2)
    doc.add_heading("6.1 Indicadores de éxito por personaje", level=2)
    add_table(doc,
              ["Personaje", "Éxito esperado"],
              [
                  ["Don Ernesto dirección", "Reporte de ventas coherente para las cinco sucursales y costo del piloto dentro de lo previsto."],
                  ["Laura cuentas por pagar", "Reducir captura de unas 12 horas semanales a menos de dos, revisar solo casos dudosos y lograr cero pagos duplicados."],
                  ["Mariana sucursal León", "Responder a clientes en menos de 15 minutos sin depender de la sucursal que surtió el pedido."],
                  ["Toño bodega", "Preguntar por voz desde el celular por existencias y recibir una respuesta correcta y fechada."],
                  ["Carlos soporte", "Accesos individuales, secretos protegidos y capacidad documentada de apagar el sistema si falla."],
              ], widths=[1.9, 4.9], font_size=8.1)

    doc.add_heading("7 Requerimientos funcionales", level=1)
    functional_rows = [
        ["RF-01", "Alta", "Autenticación", "Autenticar usuarios con Microsoft Entra ID y asociar rol, sucursal y ámbito de datos."],
        ["RF-02", "Alta", "Ingreso", "Aceptar PDF, JPG y PNG; validar tamaño, extensión, legibilidad y malware antes del procesamiento."],
        ["RF-03", "Alta", "Clasificación", "Distinguir ticket, recibo, factura u otro documento y permitir corrección humana."],
        ["RF-04", "Alta", "Extracción", "Extraer emisor, receptor, fecha, subtotal, impuestos, total, moneda y conceptos cuando estén disponibles."],
        ["RF-05", "Alta", "Confianza", "Mostrar confianza por campo y enviar a revisión aquellos por debajo del umbral configurable."],
        ["RF-06", "Alta", "Validación", "Validar campos obligatorios, coherencia aritmética, duplicados y reglas del negocio."],
        ["RF-07", "Alta", "Orquestación", "Delegar cada tarea al agente o función adecuada, conservar estado y controlar reintentos."],
        ["RF-08", "Alta", "Conocimiento", "Responder preguntas sobre reglas, productos y procedimientos con citas a documentos autorizados."],
        ["RF-09", "Alta", "Borrador", "Generar un borrador de factura simulada o registro de gasto y marcarlo como no fiscal."],
        ["RF-10", "Alta", "Aprobación", "Impedir acciones sensibles hasta recibir aprobación explícita de una persona autorizada."],
        ["RF-11", "Alta", "Corrección", "Permitir corregir campos extraídos sin alterar el archivo original y guardar ambas versiones."],
        ["RF-12", "Media", "Seguimiento", "Mostrar estado, pasos ejecutados, errores y resultado de cada solicitud."],
        ["RF-13", "Media", "Búsqueda", "Buscar por fecha, proveedor, sucursal, estado, importe e identificador."],
        ["RF-14", "Media", "Exportación", "Exportar registros autorizados en CSV y descargar un reporte PDF o Word de evidencia."],
        ["RF-15", "Media", "Administración", "Cargar y versionar fuentes de conocimiento, reglas y prompts sin exponer secretos."],
        ["RF-16", "Alta", "Auditoría", "Registrar usuario, agente, herramienta, versión, entrada, salida, aprobación, latencia y costo estimado."],
        ["RF-17", "Media", "Retroalimentación", "Capturar evaluación del usuario y motivos de corrección para mejorar pruebas y prompts."],
        ["RF-18", "Media", "Notificación", "Notificar en Teams o correo cuando un documento, queja o flujo requiera revisión o falle definitivamente."],
        ["RF-19", "Alta", "Atención", "Responder consultas de clientes y empleados, registrar la conversación y crear un caso cuando no pueda resolverla."],
        ["RF-20", "Alta", "Voz móvil", "Aceptar preguntas por voz desde un teléfono y devolver respuesta textual y opcionalmente hablada."],
        ["RF-21", "Alta", "Catálogo", "Normalizar claves y nombres equivalentes de productos y conservar la correspondencia con cada sucursal."],
        ["RF-22", "Alta", "Inventario", "Responder existencias desde una fuente estructurada y mostrar sucursal, fecha de actualización y unidad."],
        ["RF-23", "Alta", "Quejas", "Centralizar quejas, detectar recurrencia y sentimiento, y permitir seguimiento entre sucursales."],
        ["RF-24", "Media", "Ventas", "Generar un reporte por producto y sucursal basado en definiciones y claves normalizadas."],
    ]
    add_table(doc, ["ID", "Prioridad", "Capacidad", "Requerimiento"], functional_rows,
              widths=[0.7, 0.7, 1.2, 4.2], font_size=7.55)

    doc.add_heading("8 Arquitectura de agentes", level=1)
    add_para(doc, "La solución debe usar agentes solo donde el razonamiento, el lenguaje o la selección dinámica de herramientas aporten valor. Las validaciones aritméticas, permisos, persistencia, políticas y transiciones de estado deben implementarse como lógica determinista. Microsoft Agent Framework recomienda esta combinación para conservar control sobre los pasos críticos.")
    add_table(doc,
              ["Agente", "Responsabilidad", "Herramientas", "Límite"],
              [
                  ["Orquestador", "Comprender intención, crear plan, delegar y consolidar resultados.", "Workflows, estado y catálogo de herramientas.", "No aprueba ni modifica datos por sí mismo."],
                  ["Analista documental", "Elegir modelo y convertir documento a estructura normalizada.", "Document Intelligence, Blob Storage.", "No inventa campos ausentes."],
                  ["Validador", "Interpretar excepciones y explicar reglas incumplidas.", "Motor de reglas, SQL y conocimiento.", "La decisión aritmética final es determinista."],
                  ["Conocimiento", "Responder consultas y recuperar políticas, catálogos y procedimientos.", "Azure AI Search o Foundry IQ.", "Debe citar fuente y reconocer falta de evidencia."],
                  ["Atención", "Resolver preguntas, detectar sentimiento y registrar o escalar quejas.", "Speech, Search, SQL y notificaciones.", "No promete acciones que no estén confirmadas."],
                  ["Facturación simulada", "Preparar borrador no fiscal a partir de datos validados.", "Plantillas y función de negocio.", "Nunca timbra ni envía sin aprobación."],
                  ["Revisor", "Contrastar consistencia, seguridad y cumplimiento antes de presentar resultado.", "Evaluadores, políticas y trazas.", "Escala dudas a una persona."],
              ], widths=[1.25, 2.2, 1.8, 1.55], font_size=7.7)

    doc.add_heading("8.1 Patrón de orquestación", level=2)
    add_para(doc, "El patrón base será secuencial con bifurcaciones y aprobación humana: ingreso, extracción, validación, recuperación de conocimiento, generación de borrador y aprobación. Para preguntas generales puede aplicarse handoff hacia el agente de conocimiento. Las evaluaciones de seguridad y calidad pueden ejecutarse en paralelo. No se recomienda una orquestación Magentic para el camino crítico del MVP porque la ruta de negocio es conocida y debe ser predecible.")
    add_para(doc, "La implementación debe soportar checkpoints, reanudación, idempotencia y reintentos limitados. Cada herramienta sensible se declarará como sujeta a aprobación. El orquestador debe detener el flujo cuando falten datos, no exista evidencia suficiente o se alcance el límite de costo, tiempo o iteraciones.")

    doc.add_heading("9 Arquitectura tecnológica Microsoft", level=1)
    add_table(doc,
              ["Capa", "Servicio propuesto", "Uso"],
              [
                  ["Experiencia", "React TypeScript en Azure App Service", "Portal web responsivo y acceso mediante URL de Azure."],
                  ["API", "ASP.NET Core en Azure App Service", "Autorización, contratos, reglas, persistencia y fachada para agentes."],
                  ["Agentes", "Microsoft Foundry Agent Service", "Alojamiento, endpoints, identidad, sesiones, herramientas y observabilidad."],
                  ["Orquestación", "Microsoft Agent Framework", "Workflows secuenciales, handoff, concurrencia controlada y human in the loop."],
                  ["Modelos", "Catálogo de modelos de Microsoft Foundry", "Modelo principal y modelo juez seleccionados por evaluación y costo."],
                  ["Documentos", "Azure AI Document Intelligence", "OCR, layout y modelos preconstruidos para facturas y recibos."],
                  ["Voz", "Azure AI Speech", "Entrada y salida de voz para personal que trabaja desde el celular."],
                  ["Conocimiento", "Azure AI Search o Foundry IQ", "Índice híbrido, recuperación, citas y filtros por permisos."],
                  ["Archivos", "Azure Blob Storage", "Originales inmutables, resultados y evidencia con políticas de ciclo de vida."],
                  ["Transacciones", "Azure SQL Database", "Solicitudes, campos, estados, reglas, decisiones y auditoría de negocio."],
                  ["Identidad", "Microsoft Entra ID y Managed Identities", "Inicio de sesión, RBAC y acceso sin claves embebidas."],
                  ["Secretos", "Azure Key Vault", "Secretos residuales, certificados y rotación."],
                  ["Seguridad de contenido", "Azure AI Content Safety", "Moderación y Prompt Shields según el riesgo del canal."],
                  ["Observabilidad", "Azure Monitor Application Insights y Log Analytics", "Trazas OpenTelemetry, latencia, errores, tokens y costos."],
                  ["Entrega", "GitHub y GitHub Actions", "Versionado, revisión, pruebas, IaC y despliegue continuo."],
                  ["Infraestructura", "Bicep", "Recursos reproducibles y separación de ambientes."],
                  ["Colaboración", "Microsoft Teams y Power Automate opcional", "Avisos de revisión y tareas operativas."],
              ], widths=[1.15, 2.35, 3.3], font_size=7.55)

    doc.add_heading("9.1 Vista lógica", level=2)
    add_table(doc,
              ["Entrada", "Coordinación", "Servicios especializados", "Resultado"],
              [["Usuario web y documentos", "API y workflow de agentes", "Document Intelligence, AI Search, reglas, SQL y Storage", "Respuesta con citas, borrador, aprobación y auditoría"]],
              widths=[1.45, 1.7, 2.45, 1.2], font_size=8.0, header_fill=BLUE)
    add_para(doc, "El Foundry resource concentra gobierno y acceso a modelos; los proyectos separan desarrollo, pruebas y producción. Los servicios conectados deben autenticarse mediante identidad administrada y RBAC. Las trazas de agentes se enviarán a Application Insights y los registros de plataforma a Log Analytics.")

    doc.add_heading("10 Datos integraciones y contratos", level=1)
    doc.add_heading("10.1 Entidades mínimas", level=2)
    add_table(doc,
              ["Entidad", "Campos principales", "Retención inicial"],
              [
                  ["Solicitud", "Id, usuario, sucursal, intención, estado, fechas y correlación.", "24 meses para piloto, sujeto a política."],
                  ["Documento", "Id, tipo, hash, URI, versión, clasificación y propietario.", "Original según política fiscal o de negocio; pruebas 90 días."],
                  ["Campo extraído", "Nombre, valor, confianza, fuente, versión y corrección.", "Igual a la solicitud asociada."],
                  ["Ejecución de agente", "Agente, versión, modelo, herramienta, tokens, latencia y resultado.", "90 días en trazas; agregados 13 meses."],
                  ["Aprobación", "Decisión, actor, fecha, motivo, antes y después.", "24 meses o exigencia aplicable."],
                  ["Fuente de conocimiento", "Documento, versión, permisos, fragmentos, índice y estado.", "Mientras sea vigente más historial aprobado."],
              ], widths=[1.4, 3.8, 1.6], font_size=7.8)

    doc.add_heading("10.2 Contratos y reglas de datos", level=2)
    add_table(doc,
              ["ID", "Requerimiento"],
              [
                  ["DAT-01", "El archivo original será inmutable; toda corrección se guardará como versión lógica separada."],
                  ["DAT-02", "Cada salida generada incluirá identificador de solicitud, versión de agente y referencias de fuente."],
                  ["DAT-03", "Los importes usarán decimal y moneda explícita; nunca punto flotante binario para cálculos financieros."],
                  ["DAT-04", "Los documentos se deduplicarán por hash y reglas de negocio antes de crear una nueva operación."],
                  ["DAT-05", "El índice de conocimiento conservará ACL o filtros equivalentes para no recuperar contenido no autorizado."],
                  ["DAT-06", "Los conjuntos de prueba utilizarán datos sintéticos o anonimizados y contarán con resultado esperado."],
                  ["DAT-07", "Todo intercambio entre componentes se validará contra esquemas JSON versionados."],
              ], widths=[0.85, 5.95], font_size=8.2)

    doc.add_heading("11 Requerimientos no funcionales", level=1)
    nfr_rows = [
        ["RNF-01", "Rendimiento", "P95 menor a 8 segundos para preguntas de conocimiento y menor a 30 segundos para un documento de hasta 10 páginas, excluyendo cola extraordinaria."],
        ["RNF-02", "Disponibilidad", "Objetivo de 99.5 por ciento mensual para el MVP productivo y degradación controlada si un servicio de IA no está disponible."],
        ["RNF-03", "Escalabilidad", "Procesar al menos 10 documentos concurrentes y permitir escalamiento horizontal sin cambiar contratos."],
        ["RNF-04", "Usabilidad", "Un usuario nuevo completa el flujo principal con una guía de una página y sin asistencia técnica."],
        ["RNF-05", "Accesibilidad", "Interfaz conforme a WCAG 2.1 nivel AA en navegación, contraste, etiquetas y teclado."],
        ["RNF-06", "Compatibilidad", "Últimas dos versiones estables de Edge y Chrome; diseño responsivo para escritorio y tableta."],
        ["RNF-07", "Mantenibilidad", "Cobertura de pruebas sobre reglas críticas, análisis estático y documentación de decisiones de arquitectura."],
        ["RNF-08", "Portabilidad", "Infraestructura reproducible con Bicep y configuración externa por ambiente."],
        ["RNF-09", "Costo", "Presupuesto y alertas por ambiente; límites de tokens, tamaño, reintentos y concurrencia."],
        ["RNF-10", "Recuperación", "RPO de 24 horas y RTO de 8 horas para MVP; procedimientos de restauración probados."],
        ["RNF-11", "Idioma", "Interfaz, prompts, documentos y evaluación principal en español; pruebas explícitas de calidad en español."],
        ["RNF-12", "Explicabilidad", "Toda decisión asistida debe mostrar datos usados, reglas aplicadas y agente responsable."],
    ]
    add_table(doc, ["ID", "Atributo", "Requerimiento"], nfr_rows, widths=[0.75, 1.15, 4.9], font_size=7.7)

    doc.add_heading("12 Seguridad privacidad e IA responsable", level=1)
    add_table(doc,
              ["ID", "Control"],
              [
                  ["SEG-01", "Usar Entra ID, RBAC y privilegio mínimo para usuarios, aplicaciones, proyectos y agentes."],
                  ["SEG-02", "Usar Managed Identities para acceso entre Azure App Service, Foundry, Search, Storage, SQL y Key Vault."],
                  ["SEG-03", "No almacenar claves, cadenas de conexión, tokens o datos personales en prompts, repositorios o trazas."],
                  ["SEG-04", "Cifrar tránsito con TLS y datos en reposo con capacidades administradas de Azure; evaluar claves administradas por cliente si el riesgo lo exige."],
                  ["SEG-05", "Analizar archivos y entradas; limitar extensión, tamaño, tipo y frecuencia; aplicar protección contra prompt injection."],
                  ["SEG-06", "Aplicar filtros de contenido y probar lenguaje dañino, fuga de datos, jailbreak y abuso de herramientas."],
                  ["SEG-07", "Exigir aprobación humana para borradores de facturación, exportaciones masivas y cambios de reglas o fuentes."],
                  ["SEG-08", "Separar desarrollo, prueba y producción; usar datos sintéticos fuera de producción."],
                  ["SEG-09", "Mostrar aviso de que el resultado es asistido por IA y que la factura del MVP es una simulación no fiscal."],
                  ["SEG-10", "Permitir corrección, impugnación y trazabilidad de las salidas; no tomar decisiones laborales o financieras automáticas."],
                  ["SEG-11", "Evaluar sesgo, precisión y desempeño por tipo de documento, calidad de imagen, sucursal e idioma."],
                  ["SEG-12", "Definir retención, eliminación y anonimización; no usar entradas del usuario para reentrenamiento sin autorización."],
              ], widths=[0.85, 5.95], font_size=7.95)
    doc.add_heading("12.1 Evidencia obligatoria de IA responsable", level=2)
    add_table(doc,
              ["Principio", "Pregunta que debe responder el prototipo"],
              [
                  ["Equidad", "¿El agente funciona de manera comparable para las cinco sucursales aunque la calidad y cantidad de datos difieran?"],
                  ["Confiabilidad y seguridad", "¿Una factura borrosa se envía a revisión en lugar de completar importes sin evidencia?"],
                  ["Privacidad y seguridad", "¿Nómina, precios y datos de clientes están protegidos con Entra ID, Key Vault y minimización de datos?"],
                  ["Inclusión", "¿El asistente funciona por voz y desde el celular para personal de bodega?"],
                  ["Transparencia", "¿El usuario sabe que interactúa con IA y puede identificar la fuente de cada respuesta?"],
                  ["Rendición de cuentas", "¿Existe un responsable que revisa y aprueba antes de pagar o cerrar una operación?"],
              ], widths=[1.65, 5.15], font_size=8.0)

    doc.add_heading("13 Evaluación pruebas y observabilidad", level=1)
    doc.add_heading("13.1 Estrategia de prueba", level=2)
    add_table(doc,
              ["Nivel", "Cobertura", "Puerta de salida"],
              [
                  ["Unidad", "Reglas, cálculos, esquemas, autorización y funciones de herramientas.", "Sin fallos críticos; cobertura acordada en componentes de riesgo."],
                  ["Integración", "Foundry, Document Intelligence, Search, Storage, SQL, identidad y colas.", "Contratos y errores controlados en ambiente de prueba."],
                  ["Agente", "Selección de herramientas, seguimiento de instrucciones, citas, límites y rechazo seguro.", "Conjunto dorado aprobado y regresión estable."],
                  ["Seguridad", "Prompt injection, fuga, escalamiento de privilegios, archivos maliciosos y abuso.", "Cero hallazgos críticos o altos sin mitigar."],
                  ["Usuario", "Carga, revisión, aprobación, búsqueda, exportación y recuperación de error.", "Escenarios críticos aceptados por representante del negocio."],
                  ["Operación", "Latencia, costo, trazas, alertas, apagado y restauración.", "Runbook ejecutado y evidencia disponible."],
              ], widths=[1.0, 3.55, 2.25], font_size=7.8)

    doc.add_heading("13.2 Métricas de agentes", level=2)
    add_bullets(doc, [
        "Tasa de finalización del flujo, fallos por herramienta y reintentos.",
        "Precisión, relevancia de recuperación, fundamentación, coherencia y cumplimiento de instrucciones.",
        "Tasa de citas válidas y de respuestas que reconocen falta de información.",
        "Latencia total y por agente, tokens de entrada y salida, costo estimado y caché.",
        "Porcentaje de documentos enviados a revisión y motivos de corrección.",
        "Incidentes de seguridad, bloqueos por Content Safety y solicitudes de herramienta rechazadas.",
    ])
    add_para(doc, "Las evaluaciones programadas deben ejecutarse antes de promover una nueva versión de prompt, modelo, herramienta, índice o workflow. Application Insights almacenará trazas distribuidas y Foundry mostrará resultados de evaluación y métricas de agentes. Las funciones en vista previa deben aislarse detrás de una decisión explícita y no constituir una dependencia crítica sin plan alterno.")

    doc.add_heading("14 Criterios de aceptación", level=1)
    acceptance_rows = [
        ["ACE-01", "Un evaluador abre la URL publicada, inicia sesión y carga un documento de prueba sin acceder al repositorio."],
        ["ACE-02", "El sistema conserva el original, extrae los campos prioritarios y muestra confianza y fuente."],
        ["ACE-03", "Las reglas detectan un total inconsistente, un campo obligatorio ausente y un documento duplicado."],
        ["ACE-04", "Una pregunta sobre una política devuelve respuesta en español con cita válida o declara que no hay evidencia."],
        ["ACE-05", "La solución genera un borrador claramente identificado como simulación no fiscal."],
        ["ACE-06", "El flujo se detiene antes de la acción sensible y solo continúa con aprobación autorizada."],
        ["ACE-07", "El historial muestra agentes, herramientas, versiones, tiempos, decisión humana y resultado final."],
        ["ACE-08", "Un usuario sin permiso no puede consultar documentos de otra sucursal ni fuentes restringidas."],
        ["ACE-09", "La suite de evaluación alcanza las metas acordadas y no presenta vulnerabilidades críticas abiertas."],
        ["ACE-10", "El manual permite desplegar, operar, detener y eliminar recursos sin depender del autor."],
        ["ACE-11", "La documentación explica arquitectura, costos, límites, datos, prompts, riesgos y evidencia de prueba."],
        ["ACE-12", "La demostración incluye al menos un error controlado y su recuperación, no solo el camino feliz."],
    ]
    add_table(doc, ["ID", "Criterio"], acceptance_rows, widths=[0.85, 5.95], font_size=8.0)

    doc.add_heading("15 Plan de construcción asistido por agentes", level=1)
    add_para(doc, "Además de los agentes que operan el producto, la construcción puede acelerarse con agentes de ingeniería. Deben trabajar sobre un backlog controlado, producir artefactos revisables y pasar por puertas humanas antes de fusionar código, desplegar infraestructura o modificar seguridad.")
    add_table(doc,
              ["Agente de construcción", "Responsabilidad", "Salida revisable"],
              [
                  ["Analista de requerimientos", "Convertir fuentes, decisiones y preguntas en historias, criterios y trazabilidad.", "Backlog versionado y matriz de cobertura."],
                  ["Arquitecto Microsoft", "Diseñar servicios, límites, identidades, red, datos y costos.", "ADRs, diagramas y Bicep inicial."],
                  ["Ingeniero de agentes", "Definir prompts, herramientas, workflows, checkpoints y aprobaciones.", "Configuración, contratos y pruebas de agentes."],
                  ["Ingeniero de datos", "Modelar SQL, Storage, índices, calidad y datos sintéticos.", "Esquemas, cargas y conjunto dorado."],
                  ["Desarrollador API", "Implementar reglas deterministas, autorización y fachada de servicios.", "API probada y documentada."],
                  ["Desarrollador web", "Construir carga, revisión, chat, estados y administración.", "Interfaz accesible y pruebas end to end."],
                  ["Ingeniero DevSecOps", "Automatizar infraestructura, CI CD, secretos, escaneo y ambientes.", "Pipelines, políticas y runbooks."],
                  ["Agente QA y evaluación", "Generar casos, ejecutar regresión y comparar versiones de modelos y prompts.", "Reporte de calidad y recomendación de promoción."],
                  ["Revisor de seguridad", "Analizar amenazas, permisos, privacidad, inyección y abuso de herramientas.", "Hallazgos priorizados y aprobación de control."],
                  ["Agente de documentación", "Mantener manuales, arquitectura, evidencia y registro de cambios.", "Documentación coherente con la versión desplegada."],
              ], widths=[1.65, 3.2, 1.95], font_size=7.65)

    doc.add_heading("15.1 Reglas de colaboración entre agentes", level=2)
    add_bullets(doc, [
        "Cada tarea debe tener entrada, salida, definición de terminado y archivos permitidos.",
        "Ningún agente fusiona cambios, concede roles, rota secretos o despliega a producción sin aprobación humana.",
        "Los agentes deben citar el requisito y la decisión de arquitectura que implementan.",
        "Los resultados se revisan mediante pruebas automatizadas y revisión de pares; no se aceptan por apariencia.",
        "Los prompts, skills, herramientas y evaluadores se versionan junto con el código.",
        "Una regresión de calidad, seguridad o costo bloquea la promoción incluso si la funcionalidad principal opera.",
    ])

    doc.add_heading("16 Backlog hitos y entregables", level=1)
    add_table(doc,
              ["Hito", "Duración sugerida", "Resultado"],
              [
                  ["M0 Alineación", "2 a 3 días", "Decisiones abiertas resueltas, propietario, presupuesto y datos autorizados."],
                  ["M1 Fase 1", "1 a 2 semanas", "Diagnóstico, priorización, arquitectura, riesgos, métricas y backlog aprobado."],
                  ["M2 Fundación", "1 semana", "Repositorios, IaC, ambientes, identidad, observabilidad y datos sintéticos."],
                  ["M3 Flujo documental", "2 semanas", "Carga, almacenamiento, extracción, normalización y revisión de campos."],
                  ["M4 Agentes y RAG", "2 semanas", "Orquestador, conocimiento, validación, citas y workflows con aprobación."],
                  ["M5 Producto web", "1 a 2 semanas", "Experiencia completa, estados, búsqueda, corrección y borrador simulado."],
                  ["M6 Calidad y seguridad", "1 semana", "Evaluación, red teaming, rendimiento, accesibilidad y remediación."],
                  ["M7 Piloto", "1 semana", "Despliegue, manuales, demostración, métricas y cierre de aceptación."],
              ], widths=[1.4, 1.45, 3.95], font_size=8.0)

    doc.add_heading("16.1 Paquete de entrega", level=2)
    add_bullets(doc, [
        "URL funcional de Azure y cuentas o instrucciones de acceso para evaluación.",
        "Documento de requerimientos y arquitectura actualizado.",
        "Código fuente, prompts, workflows, evaluadores e infraestructura como código.",
        "Manual de usuario, guía de despliegue, runbook operativo y procedimiento de apagado.",
        "Datos de prueba sintéticos, conjunto dorado y reporte de evaluación.",
        "Evidencias de Fase 1 y Fase 2, incluyendo capturas, trazas y decisiones humanas.",
        "Inventario de recursos, configuración, costos estimados y lista de limitaciones conocidas.",
    ])

    doc.add_heading("17 Riesgos dependencias y mitigaciones", level=1)
    add_table(doc,
              ["ID", "Riesgo", "Impacto", "Mitigación"],
              [
                  ["R-01", "Existen diferencias entre comentarios verbales y reglas finales del PDF.", "Interpretación inconsistente del alcance.", "Tratar el PDF como fuente prioritaria y registrar excepciones mediante control de cambios."],
                  ["R-02", "Calidad variable de fotos y documentos.", "Extracción errónea.", "Guía de captura, umbrales, revisión humana y conjunto de prueba diverso."],
                  ["R-03", "Alucinación o cita incorrecta.", "Decisión equivocada.", "RAG con fuentes autorizadas, citas obligatorias y evaluación de fundamentación."],
                  ["R-04", "Prompt injection en documentos.", "Fuga o uso indebido de herramientas.", "Separar datos de instrucciones, Prompt Shields, allowlist y aprobación."],
                  ["R-05", "Permisos excesivos.", "Acceso no autorizado.", "Managed Identity, RBAC mínimo, pruebas negativas y revisión periódica."],
                  ["R-06", "Consumo imprevisto de Azure.", "Agotamiento de créditos.", "Presupuesto, alertas, cuotas, apagado y límites de tokens o reintentos."],
                  ["R-07", "Dependencia de características preview.", "Cambios o falta de SLA.", "Aislar preview, documentar alternativa GA y aprobar su uso."],
                  ["R-08", "Confusión entre simulación y factura real.", "Riesgo legal y reputacional.", "Marcado visible, bloqueo de envío y revisión humana."],
                  ["R-09", "Datos personales en trazas.", "Incumplimiento de privacidad.", "Redacción, minimización, retención corta y acceso restringido."],
                  ["R-10", "El enlace deja de funcionar al terminar créditos.", "Evaluación o portafolio inaccesible.", "Capturas, video, exportación de evidencia y plan de migración."],
              ], widths=[0.6, 2.25, 1.55, 2.4], font_size=7.35)

    doc.add_heading("18 Decisiones abiertas", level=1)
    add_para(doc, "Estas decisiones deben cerrarse en M0. Hasta entonces, la estimación y la arquitectura son una línea base.")
    add_table(doc,
              ["Decisión", "Opción recomendada", "Alternativas"],
              [
                  ["Opción definitiva", "Distribuidora Río Claro con facturas y asistente empresarial.", "Proyecto trabajado y documentado en la Fase 1."],
                  ["Datos de negocio", "Sintéticos más muestra anonimizada autorizada.", "Solo sintéticos durante todo el piloto."],
                  ["Canales", "Portal web y notificación en Teams.", "WhatsApp con presupuesto y proveedor aprobados."],
                  ["Alojamiento web", "Azure App Service para mantener coherencia con el curso.", "Static Web Apps más Functions o Container Apps."],
                  ["Persistencia", "Azure SQL más Blob Storage.", "Cosmos DB cuando el esquema o escala lo justifiquen."],
                  ["Recuperación", "Azure AI Search con índice híbrido y citas.", "Foundry IQ si región, disponibilidad y gobernanza lo permiten."],
                  ["Modelo", "Seleccionar mediante evaluación de español, costo y latencia.", "Modelo único o combinación por tarea."],
                  ["Entornos", "Desarrollo, prueba y producción separados.", "Desarrollo y demostración para un prototipo académico."],
                  ["SLA y volumen", "Metas RNF del presente documento.", "Ajustar a datos reales de usuarios y documentos."],
                  ["Retención", "Política inicial definida en sección 10.", "Alinear con obligaciones fiscales y política institucional."],
              ], widths=[1.55, 2.85, 2.4], font_size=7.8)

    doc.add_heading("19 Matriz de trazabilidad", level=1)
    add_table(doc,
              ["Fuente", "Instrucción observada", "Requerimientos relacionados"],
              [
                  ["T02 00 08 43", "Proyecto individual, empresa ficticia, evidencia de prompts.", "F1-01, F1-04, F1-05, F1-08"],
                  ["T03 00 21 44", "Plan de implementación de IA desde cero para una empresa sin IA.", "F1-02, F1-03"],
                  ["T05 00 08 24", "Entrega de Word o PDF por OneDrive y formulario; uso de Copilot.", "F1-04, F1-08"],
                  ["T06 00 14 08", "Fase 2 individual o en equipo; caso estructurado de empresa familiar.", "F2-01, F2-08"],
                  ["T06 00 15 03", "140 empleados, cinco sucursales, limpieza y operación en WhatsApp Word USB.", "Contexto, F2-01"],
                  ["T06 00 16 07", "Página o chatbot funcionando como producto para un usuario real.", "F2-03, F2-04, F2-05"],
                  ["T06 00 17 33", "No basta el repositorio; se requiere sitio web desplegado en Azure.", "F2-03, F2-04"],
                  ["T06 00 18 10", "Implementar una o varias problemáticas y documentar.", "F2-01, F2-06"],
                  ["T06 00 18 20", "Escanear tickets y simular facturación; no se exige timbrado.", "Alcance recomendado, F2-07"],
                  ["T06 00 21 41", "No se exige gran escala o seguridad empresarial; debe funcionar.", "F2-05 y límites del MVP"],
                  ["T06 00 25 34", "La solución puede ser chatbot, página o app; requiere documento sencillo.", "F2-03, F2-06"],
                  ["T06 00 26 14", "Uso obligatorio de agente de IA Azure.", "F2-02"],
                  ["T06 00 28 55", "Entregar página utilizable o instalable, no solo carpeta.", "F2-03, F2-04"],
                  ["T10 00 27 31", "Ejemplo de constructor, arquitecto y desplegador bajo orquestación.", "Sección 15"],
                  ["T11 01 31 07", "Evaluaciones y Application Insights para probar agentes.", "F2-11, sección 13"],
                  ["T16 00 54 28", "El reporte de Fase 2 puede entregarse en Word o Markdown.", "F2-06"],
                  ["T17 00 04 41", "Resumen final: solución de IA desplegada en Azure.", "F2-02, F2-03"],
                  ["T17 01 21 54", "Entrega en canal de Teams Entrega tu proyecto fase 2.", "F2-10"],
                  ["PDF página 1", "Caso completo de Río Claro, fuentes desordenadas, restricciones y motivación.", "Contexto, objetivos, datos y restricciones"],
                  ["PDF página 2", "Dos opciones, equipo máximo de cuatro, prototipo Azure accesible, IA responsable, personajes y entrega Markdown.", "F2-01, F2-03, F2-08, F2-10, F2-13, F2-14"],
              ], widths=[1.05, 4.0, 1.75], font_size=7.35)

    doc.add_heading("Anexo A Inventario de transcripciones", level=1)
    transcript_files = [
        "Curso-Fundamentos de IA con Tecnologías  MICROSOFT.vtt",
        "Curso-Fundamentos de IA con Tecnologías  MICROSOFT 2.vtt",
        "Curso-Fundamentos de IA con Tecnologías  MICROSOFT 3.vtt",
        "Curso-Fundamentos de IA con Tecnologías  MICROSOFT 5.vtt",
        "Curso-Fundamentos de IA con Tecnologías  MICROSOFT 6.vtt",
        "Curso-Fundamentos de IA con Tecnologías  MICROSOFT 7.vtt",
        "Curso-Fundamentos de IA con Tecnologías  MICROSOFT 8.vtt",
        "Curso-Fundamentos de IA con Tecnologías  MICROSOFT 9.vtt",
        "Curso-Fundamentos de IA con Tecnologías  MICROSOFT 10.vtt",
        "Curso-Fundamentos de IA con Tecnologías  MICROSOFT 11.vtt",
        "Curso-Fundamentos de IA con Tecnologías  MICROSOFT 12.vtt",
        "Curso-Fundamentos de IA con Tecnologías  MICROSOFT 13.vtt",
        "Curso-Fundamentos de IA con Tecnologías  MICROSOFT 14.vtt",
        "Curso-Fundamentos de IA con Tecnologías  MICROSOFT 15.vtt",
        "Curso-Fundamentos de IA con Tecnologías  MICROSOFT 16.vtt",
        "Curso-Fundamentos de IA con Tecnologías  MICROSOFT 17.vtt",
    ]
    add_bullets(doc, transcript_files)
    add_para(doc, "No se encontró un archivo de transcripción con el número 4. Se incorporó el PDF final de Río Claro; cualquier otro material mencionado en Teams que no esté en la carpeta queda fuera de la evidencia disponible.")

    doc.add_heading("Anexo B Fuente PDF del caso", level=1)
    add_bullets(doc, [
        "Proyecto AI 901 Río Claro Final PDF, dos páginas, incorporado como fuente prioritaria del caso empresarial y las reglas de entrega.",
        "El PDF contenía texto incrustado ajeno al requerimiento del proyecto. Ese contenido fue clasificado como prompt injection y excluido por completo de requisitos, instrucciones, código y entregables.",
    ])

    doc.add_heading("Anexo C Referencias técnicas oficiales", level=1)
    refs = [
        ("Arquitectura de Microsoft Foundry", "https://learn.microsoft.com/en-us/azure/foundry/concepts/architecture"),
        ("Agentes en Microsoft Foundry", "https://learn.microsoft.com/en-us/azure/ai-foundry/agents/overview?view=foundry-classic"),
        ("Microsoft Agent Framework", "https://learn.microsoft.com/agent-framework/overview"),
        ("Capacidades de workflows", "https://learn.microsoft.com/en-us/agent-framework/workflows/"),
        ("Orquestaciones de workflows", "https://learn.microsoft.com/en-us/agent-framework/workflows/orchestrations/"),
        ("Human in the loop", "https://learn.microsoft.com/en-us/agent-framework/workflows/human-in-the-loop"),
        ("RAG e índices en Microsoft Foundry", "https://learn.microsoft.com/en-us/azure/foundry/concepts/retrieval-augmented-generation"),
        ("RAG en Azure AI Search", "https://learn.microsoft.com/en-us/azure/search/retrieval-augmented-generation-overview"),
        ("Azure AI Search como herramienta de agentes", "https://learn.microsoft.com/en-us/azure/foundry/agents/how-to/tools/ai-search"),
        ("Document Intelligence para facturas", "https://learn.microsoft.com/en-us/azure/ai-services/document-intelligence/prebuilt/invoice?view=doc-intel-4.0.0"),
        ("Azure AI Content Safety", "https://learn.microsoft.com/en-us/azure/ai-services/content-safety/overview/"),
        ("Monitoreo de agentes", "https://learn.microsoft.com/en-us/azure/foundry/observability/how-to/how-to-monitor-agents-dashboard?view=foundry"),
    ]
    for title, url in refs:
        p = doc.add_paragraph(style="List Bullet")
        add_hyperlink(p, title, url)

    doc.add_heading("Anexo D Definición de terminado", level=1)
    add_bullets(doc, [
        "Cada requisito implementado tiene prueba, evidencia y trazabilidad al backlog.",
        "No hay secretos, datos personales reales ni permisos excesivos en código o trazas.",
        "La versión de agentes, prompts, herramientas y modelo está fijada y documentada.",
        "El conjunto dorado y las pruebas de seguridad se ejecutaron contra la versión desplegada.",
        "El enlace funciona desde una sesión de evaluación y el flujo completo puede repetirse.",
        "Los costos, recursos y procedimiento de apagado están documentados y probados.",
        "La documentación coincide con la aplicación y permite operación por una persona distinta del autor.",
        "Las limitaciones y decisiones pendientes están visibles y tienen propietario.",
    ])

    add_footer(doc)
    doc.save(OUT)
    print(str(OUT))


if __name__ == "__main__":
    build()
