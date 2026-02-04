"""
PDF_GENERATOR.PY - VERSIÓN MEJORADA VISUAL
Generador de PDFs profesionales para KAZO con gráficos y diseño moderno
"""

from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    PageBreak, Image, KeepTogether
)
from reportlab.lib.enums import TA_CENTER, TA_RIGHT, TA_LEFT, TA_JUSTIFY
from reportlab.pdfgen import canvas as pdf_canvas
from datetime import datetime
import pandas as pd

# Para gráficos de barras
from reportlab.graphics.shapes import Drawing
from reportlab.graphics.charts.barcharts import HorizontalBarChart
from reportlab.graphics import renderPDF

# ============================================================================
# ESTILOS PERSONALIZADOS
# ============================================================================

def get_custom_styles():
    """Retorna estilos personalizados para KAZO"""
    styles = getSampleStyleSheet()
    
    styles.add(ParagraphStyle(
        name='KazoTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=colors.HexColor('#366092'),
        spaceAfter=30,
        alignment=TA_CENTER,
        fontName='Helvetica-Bold'
    ))
    
    styles.add(ParagraphStyle(
        name='KazoSection',
        parent=styles['Heading3'],
        fontSize=14,
        textColor=colors.HexColor('#366092'),
        spaceAfter=10,
        spaceBefore=10,
        fontName='Helvetica-Bold'
    ))
    
    styles.add(ParagraphStyle(
        name='KazoNormal',
        parent=styles['Normal'],
        fontSize=10,
        leading=14,
        alignment=TA_JUSTIFY,
        fontName='Helvetica'
    ))
    
    return styles

# ============================================================================
# CLASE BASE PARA PDFs
# ============================================================================

class KazoPDFGenerator:
    """Clase base para generar PDFs profesionales de KAZO"""
    
    def __init__(self, filename, cliente_nombre, title="Informe KAZO"):
        self.filename = filename
        self.cliente_nombre = cliente_nombre
        self.title = title
        self.styles = get_custom_styles()
        
        self.doc = SimpleDocTemplate(
            filename,
            pagesize=A4,
            rightMargin=2*cm,
            leftMargin=2*cm,
            topMargin=2.5*cm,
            bottomMargin=2.5*cm
        )
        
        self.story = []
        self.width, self.height = A4
    
    def add_header(self):
        """Añade header"""
        title = Paragraph(self.title, self.styles['KazoTitle'])
        self.story.append(title)
        
        cliente_info = f"""
        <para align=center>
        <b>Cliente:</b> {self.cliente_nombre}<br/>
        <b>Fecha:</b> {datetime.now().strftime('%d/%m/%Y')}<br/>
        </para>
        """
        self.story.append(Paragraph(cliente_info, self.styles['KazoNormal']))
        self.story.append(Spacer(1, 0.5*cm))
        
        line_table = Table([['']], colWidths=[self.width - 4*cm])
        line_table.setStyle(TableStyle([
            ('LINEBELOW', (0, 0), (-1, -1), 2, colors.HexColor('#70AD47')),
        ]))
        self.story.append(line_table)
        self.story.append(Spacer(1, 0.3*cm))
    
    def add_section_title(self, title):
        """Añade título de sección"""
        self.story.append(Paragraph(title, self.styles['KazoSection']))
        self.story.append(Spacer(1, 0.2*cm))
    
    def add_paragraph(self, text, style='KazoNormal'):
        """Añade párrafo de texto"""
        self.story.append(Paragraph(text, self.styles[style]))
        self.story.append(Spacer(1, 0.2*cm))
    
    def add_metric_cards(self, metrics_list):
        """Añade tarjetas de métricas grandes"""
        rows = []
        
        for i in range(0, len(metrics_list), 2):
            row_cells = []
            for j in range(2):
                if i + j < len(metrics_list):
                    metric = metrics_list[i + j]
                    cell_content = f"""
                    <para alignment="center">
                    <font size="10" color="grey">{metric['label']}</font><br/>
                    <font size="20" color="{metric.get('color', '#366092')}"><b>{metric['value']}</b></font>
                    </para>
                    """
                    row_cells.append(Paragraph(cell_content, self.styles['KazoNormal']))
                else:
                    row_cells.append("")
            rows.append(row_cells)
        
        col_width = (self.width - 5*cm) / 2
        table = Table(rows, colWidths=[col_width, col_width])
        
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#F8F9FA')),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('TOPPADDING', (0, 0), (-1, -1), 20),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 20),
            ('BOX', (0, 0), (-1, -1), 2, colors.HexColor('#E0E0E0')),
            ('GRID', (0, 0), (-1, -1), 1, colors.white),
        ]))
        
        self.story.append(table)
        self.story.append(Spacer(1, 0.5*cm))
    
    def add_bar_chart(self, data_dict, title="", max_items=10):
        """Añade gráfico de barras horizontales"""
        if not data_dict:
            return
        
        if len(data_dict) > max_items:
            sorted_items = sorted(data_dict.items(), key=lambda x: x[1], reverse=True)
            data_dict = dict(sorted_items[:max_items])
        
        sorted_items = sorted(data_dict.items(), key=lambda x: x[1])
        labels = [item[0][:25] for item in sorted_items]
        values = [item[1] for item in sorted_items]
        
        drawing = Drawing(self.width - 4*cm, 10*cm)
        
        chart = HorizontalBarChart()
        chart.x = 5*cm
        chart.y = 0.5*cm
        chart.width = self.width - 11*cm
        chart.height = 9*cm
        
        chart.data = [values]
        chart.categoryAxis.categoryNames = labels
        chart.bars[0].fillColor = colors.HexColor('#70AD47')
        chart.valueAxis.valueMin = 0
        chart.valueAxis.valueMax = max(values) * 1.1 if values else 100
        chart.categoryAxis.labels.fontSize = 9
        chart.valueAxis.labels.fontSize = 9
        
        drawing.add(chart)
        
        if title:
            self.add_section_title(title)
        
        self.story.append(drawing)
        self.story.append(Spacer(1, 0.5*cm))
    
    def add_cuadrante_visual(self, cuad_data):
        """Añade caja visual de cuadrante BCG"""
        header_text = f"""
        <para alignment="left">
        <font size="14"><b>{cuad_data['emoji']} {cuad_data['nombre']}</b></font>
        <font size="10" color="grey"> ({cuad_data['count']} platos)</font>
        </para>
        """
        
        accion_text = f"""
        <para alignment="left">
        <font size="11" color="{cuad_data['color']}"><b>→ {cuad_data['accion']}</b></font>
        </para>
        """
        
        platos_text = ""
        if cuad_data.get('top_platos'):
            platos_text = "<para alignment='left'><b>Principales:</b><br/>"
            for plato in cuad_data['top_platos'][:5]:
                platos_text += f"• {plato[:40]}<br/>"
            platos_text += "</para>"
        
        beneficio_text = f"""
        <para alignment="right">
        <font size="14" color="{cuad_data['color']}"><b>{cuad_data.get('beneficio_total', 0):,.2f}€</b></font><br/>
        <font size="8" color="grey">Beneficio/mes</font>
        </para>
        """
        
        data = [
            [Paragraph(header_text, self.styles['KazoNormal']), ''],
            [Paragraph(accion_text, self.styles['KazoNormal']), ''],
            [Paragraph(platos_text, self.styles['KazoNormal']), Paragraph(beneficio_text, self.styles['KazoNormal'])]
        ]
        
        table = Table(data, colWidths=[10*cm, 5*cm])
        
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor(cuad_data['color'])),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#F8F9FA')),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('TOPPADDING', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
            ('LEFTPADDING', (0, 0), (-1, -1), 15),
            ('BOX', (0, 0), (-1, -1), 2, colors.HexColor(cuad_data['color'])),
            ('SPAN', (0, 0), (1, 0)),
            ('SPAN', (0, 1), (1, 1)),
        ]))
        
        self.story.append(table)
        self.story.append(Spacer(1, 0.3*cm))
    
    def add_footer_page(self, canvas, doc):
        """Añade footer a cada página"""
        canvas.saveState()
        
        canvas.setStrokeColor(colors.HexColor('#70AD47'))
        canvas.setLineWidth(1)
        canvas.line(2*cm, 2*cm, self.width - 2*cm, 2*cm)
        
        footer_text = f"KAZO Consultoría HORECA | {self.cliente_nombre} | Página {doc.page}"
        canvas.setFont('Helvetica', 8)
        canvas.setFillColor(colors.grey)
        canvas.drawCentredString(self.width / 2, 1.5*cm, footer_text)
        
        contact = "info@kazo.es | www.kazo.es | +34 XXX XXX XXX"
        canvas.setFont('Helvetica', 7)
        canvas.drawCentredString(self.width / 2, 1*cm, contact)
        
        canvas.restoreState()
    
    def build(self):
        """Construye el PDF"""
        self.doc.build(self.story, onFirstPage=self.add_footer_page, 
                      onLaterPages=self.add_footer_page)

# ============================================================================
# INFORME DE INGENIERÍA DE MENÚ MEJORADO
# ============================================================================

def generar_pdf_ingenieria_menu(filename, cliente_nombre, df_carta, grafico_path=None):
    """Genera PDF VISUAL de Ingeniería de Menú"""
    
    pdf = KazoPDFGenerator(filename, cliente_nombre, "Informe de Ingeniería de Menú")
    
    pdf.add_header()
    
    # PÁGINA 1: RESUMEN EJECUTIVO
    pdf.add_section_title("📊 Resumen Ejecutivo")
    
    total_facturacion = (df_carta['Precio Venta'] * df_carta['Ventas/Mes']).sum()
    total_beneficio = ((df_carta['Precio Venta'] - df_carta['Coste Total']) * df_carta['Ventas/Mes']).sum()
    margen_general = (total_beneficio / total_facturacion * 100) if total_facturacion > 0 else 0
    
    metrics_cards = [
        {'label': '💰 Facturación Mensual', 'value': f'{total_facturacion:,.0f}€', 'color': '#4472C4'},
        {'label': '💵 Beneficio Mensual', 'value': f'{total_beneficio:,.0f}€', 'color': '#70AD47'},
        {'label': '📊 Margen General', 'value': f'{margen_general:.1f}%', 'color': '#FFC000'},
        {'label': '🍽️ Platos', 'value': f'{len(df_carta)}', 'color': '#366092'},
    ]
    
    pdf.add_metric_cards(metrics_cards)
    
    if grafico_path:
        try:
            img = Image(grafico_path, width=15*cm, height=10*cm)
            pdf.story.append(img)
            pdf.story.append(Spacer(1, 0.5*cm))
        except:
            pass
    
    pdf.story.append(PageBreak())
    
    # PÁGINA 2: CLASIFICACIÓN BCG
    pdf.add_section_title("🎯 Clasificación BCG")
    
    ventas_media = df_carta['Ventas/Mes'].median()
    df_carta['Margen %'] = ((df_carta['Precio Venta'] - df_carta['Coste Total']) / df_carta['Precio Venta'] * 100)
    margen_medio = df_carta['Margen %'].median()
    
    def clasificar(row):
        if row['Ventas/Mes'] >= ventas_media and row['Margen %'] >= margen_medio:
            return '⭐ ESTRELLA'
        elif row['Ventas/Mes'] >= ventas_media and row['Margen %'] < margen_medio:
            return '🐴 CABALLO'
        elif row['Ventas/Mes'] < ventas_media and row['Margen %'] >= margen_medio:
            return '🧩 ROMPECABEZAS'
        else:
            return '🐕 PERRO'
    
    df_carta['Cuadrante'] = df_carta.apply(clasificar, axis=1)
    df_carta['Beneficio'] = (df_carta['Precio Venta'] - df_carta['Coste Total']) * df_carta['Ventas/Mes']
    
    df_estrellas = df_carta[df_carta['Cuadrante'] == '⭐ ESTRELLA']
    df_caballos = df_carta[df_carta['Cuadrante'] == '🐴 CABALLO']
    df_rompecabezas = df_carta[df_carta['Cuadrante'] == '🧩 ROMPECABEZAS']
    df_perros = df_carta[df_carta['Cuadrante'] == '🐕 PERRO']
    
    if not df_estrellas.empty:
        pdf.add_cuadrante_visual({
            'emoji': '⭐', 'nombre': 'ESTRELLAS', 'count': len(df_estrellas),
            'color': '#70AD47', 'accion': 'Mantener y destacar',
            'top_platos': df_estrellas.nlargest(5, 'Beneficio')['Nombre Plato'].tolist(),
            'beneficio_total': df_estrellas['Beneficio'].sum()
        })
    
    if not df_caballos.empty:
        pdf.add_cuadrante_visual({
            'emoji': '🐴', 'nombre': 'CABALLOS', 'count': len(df_caballos),
            'color': '#4472C4', 'accion': 'Subir precio +0.50€',
            'top_platos': df_caballos.nlargest(5, 'Ventas/Mes')['Nombre Plato'].tolist(),
            'beneficio_total': df_caballos['Beneficio'].sum()
        })
    
    if not df_rompecabezas.empty:
        pdf.add_cuadrante_visual({
            'emoji': '🧩', 'nombre': 'ROMPECABEZAS', 'count': len(df_rompecabezas),
            'color': '#FFC000', 'accion': 'Promocionar',
            'top_platos': df_rompecabezas.nlargest(5, 'Margen %')['Nombre Plato'].tolist(),
            'beneficio_total': df_rompecabezas['Beneficio'].sum()
        })
    
    if not df_perros.empty:
        pdf.add_cuadrante_visual({
            'emoji': '🐕', 'nombre': 'PERROS', 'count': len(df_perros),
            'color': '#C00000', 'accion': 'Eliminar',
            'top_platos': df_perros.nsmallest(5, 'Beneficio')['Nombre Plato'].tolist(),
            'beneficio_total': df_perros['Beneficio'].sum()
        })
    
    pdf.story.append(PageBreak())
    
    # PÁGINA 3: TOP 10 CON GRÁFICO DE BARRAS
    top_10 = df_carta.nlargest(10, 'Beneficio')
    if not top_10.empty:
        top_10_dict = dict(zip(top_10['Nombre Plato'], top_10['Beneficio']))
        pdf.add_bar_chart(top_10_dict, "🏆 Top 10 Más Rentables")
    
    pdf.story.append(Spacer(1, 0.5*cm))
    
    # PÁGINA 4: IMPACTO
    pdf.add_section_title("💡 Proyección de Impacto")
    
    impacto_caballos = (df_caballos['Ventas/Mes'].sum() * 0.50) if not df_caballos.empty else 0
    impacto_rompecabezas = (df_rompecabezas['Beneficio'].sum() * 0.20) if not df_rompecabezas.empty else 0
    ahorro_perros = ((df_perros['Coste Total'] * df_perros['Ventas/Mes']).sum() * 0.15) if not df_perros.empty else 0
    
    impacto_total_mes = impacto_caballos + impacto_rompecabezas + ahorro_perros
    impacto_total_año = impacto_total_mes * 12
    
    impact_text = f"""
    <b>Beneficio Adicional Estimado:</b><br/>
    <br/>
    • Subir Caballos: <font color="#70AD47"><b>+{impacto_caballos:,.0f}€/mes</b></font><br/>
    • Promocionar Rompecabezas: <font color="#FFC000"><b>+{impacto_rompecabezas:,.0f}€/mes</b></font><br/>
    • Optimizar Perros: <font color="#4472C4"><b>+{ahorro_perros:,.0f}€/mes</b></font><br/>
    <br/>
    <font size="14" color="#70AD47"><b>Total Mensual: +{impacto_total_mes:,.0f}€</b></font><br/>
    <font size="16" color="#366092"><b>Proyección Anual: +{impacto_total_año:,.0f}€</b></font>
    """
    
    pdf.add_paragraph(impact_text, 'KazoNormal')
    
    pdf.add_section_title("✅ Plan de Acción")
    
    plan = f"""
    <b>Esta Semana:</b> Subir {len(df_caballos)} platos (+0.50€), Eliminar {min(3, len(df_perros))} perros<br/>
    <b>Este Mes:</b> Promocionar {min(3, len(df_rompecabezas))} rompecabezas, Destacar {min(3, len(df_estrellas))} estrellas<br/>
    <b>3 Meses:</b> Revisar carta, ajustar precios, medir impacto
    """
    
    pdf.add_paragraph(plan, 'KazoNormal')
    
    pdf.build()
    return filename

# ============================================================================
# REPORTE MENSUAL
# ============================================================================

def generar_reporte_mensual(filename, cliente_nombre, mes, año, datos_mes):
    """Genera reporte mensual"""
    meses = ['Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio',
             'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre']
    
    pdf = KazoPDFGenerator(filename, cliente_nombre, f"Reporte - {meses[mes-1]} {año}")
    pdf.add_header()
    
    margen = (datos_mes['beneficio'] / datos_mes['facturacion'] * 100) if datos_mes['facturacion'] > 0 else 0
    
    kpis = [
        {'label': '💰 Facturación', 'value': f"{datos_mes['facturacion']:,.0f}€", 'color': '#4472C4'},
        {'label': '💵 Beneficio', 'value': f"{datos_mes['beneficio']:,.0f}€", 'color': '#70AD47'},
        {'label': '📊 Margen', 'value': f"{margen:.1f}%", 'color': '#FFC000'},
        {'label': '🍽️ Platos', 'value': f"{datos_mes['platos_vendidos']:,}", 'color': '#366092'}
    ]
    pdf.add_metric_cards(kpis)
    
    if 'alertas' in datos_mes:
        pdf.add_section_title("⚠️ Alertas")
        for alerta in datos_mes['alertas']:
            pdf.add_paragraph(f"• {alerta}")
    
    pdf.build()
    return filename
