from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.pagesizes import A4
from reportlab.graphics import renderPDF

import svglib.svglib as svglib

from graphs import barchart_horizontal, barchart_vertical, piechart, linechart

from PyPDF2 import PdfReader, PdfWriter

import os

dir_path = os.path.dirname(os.path.realpath(__file__))
graph_path = os.path.join(dir_path, 'utils', 'graphs', 'SVG_')

# Register a new font for the PDF
pdfmetrics.registerFont(TTFont('Poppins', os.path.join(dir_path, 'utils', 'fonts', 'Poppins-Regular.ttf')))
pdfmetrics.registerFont(TTFont('Poppins-Bold', os.path.join(dir_path, 'utils', 'fonts', 'Poppins-Bold.ttf')))
pdfmetrics.registerFont(TTFont('Poppins-SemiBold', os.path.join(dir_path, 'utils', 'fonts', 'Poppins-SemiBold.ttf')))
pdfmetrics.registerFont(TTFont('Poppins-ExtraBold', os.path.join(dir_path, 'utils', 'fonts', 'Poppins-ExtraBold.ttf')))


def create_overlay(data):
    # Destination path for the overlay PDF
    overlay_path = os.path.join(dir_path, 'utils', 'overlay.pdf')
    
    c = canvas.Canvas(overlay_path, pagesize=A4)
    
    # Municipality
    c.setFont("Poppins", 28)
    c.setFillColorRGB(0.8627, 0.9333, 0.9843)
    c.drawString(320, 783, f"{data['municipality']}")
    
    # Time period
    c.setFont("Poppins", 13)
    c.drawString(178, 748, f"{data['time_period']}")

    # Date
    c.drawString(395, 747.5, f"{data['date']}")

    # Topics
    c.setFont("Poppins-SemiBold", 8)
    c.setFillColorRGB(0.0392, 0.1019, 0.1608)
    for i, topic in enumerate(data['topics']):
        c.drawString(60, 659 - (i * 13.6), f"{topic}")

    # Amount of hubs
    c.setFont("Poppins-ExtraBold", 36)
    c.setFillColorRGB(0.0392, 0.1019, 0.1608)
    if data['amount_hubs'] <= 99:
        c.drawString(262, 602, f"{data['amount_hubs']}")
    else:
        c.setFont("Poppins-ExtraBold", 30)
        c.drawString(260, 603, f"{data['amount_hubs']}")

    # Service providers
    c.setFont("Poppins", 8)
    columns = 7
    column_width = 100
    start_x = 330
    start_y = 675
    line_height = 16

    for i, provider in enumerate(data['service_providers']):
        column = i // columns
        row = i % columns
        x = start_x + column * column_width
        y = start_y - row * line_height
        c.drawString(x, y, f"- {provider}")
    
    # avg distance travelled in meters
    distance_data = data["avg_distance_travelled"]
    barchart_vertical(list(distance_data.keys()), list(distance_data.values()) , 270, 190, "avg_distance", "Voertuig types", "Afstand (m)")
    distance_svg = svglib.svg2rlg(graph_path + "avg_distance" + ".svg")
    renderPDF.draw(distance_svg, c, 20, 312)

    # avg parking time in minutes
    parking_data = data["avg_parking_time"]
    barchart_vertical(list(parking_data.keys()), list(parking_data.values()), 270, 190, "avg_parking_time", "Voertuig types", "Tijd (h)")
    parking_svg = svglib.svg2rlg(graph_path + "avg_parking_time" + ".svg")
    renderPDF.draw(parking_svg, c, 20, 28)

    # top 5 hubs
    hubs_data = data["top_5_hubs"]["top5"]
    barchart_horizontal(list(hubs_data.keys()), list(hubs_data.values()), 450, 200, "top_5_hubs")
    hubs_svg = svglib.svg2rlg(graph_path + "top_5_hubs" + ".svg")

    # Scale down the SVG
    scale_factor = 0.55
    hubs_svg.width = hubs_svg.width * scale_factor
    hubs_svg.height = hubs_svg.height * scale_factor
    hubs_svg.scale(scale_factor, scale_factor)

    renderPDF.draw(hubs_svg, c, 330, 410)

    # top 5 zones rented
    zones_data = data["top_5_zones_rented"]["top5"]
    barchart_horizontal(list(zones_data.keys()), list(zones_data.values()), 450, 200, "top_5_zones")
    zones_svg = svglib.svg2rlg(graph_path + "top_5_zones" + ".svg")

    # Scale down the SVG
    scale_factor = 0.55
    zones_svg.width = zones_svg.width * scale_factor
    zones_svg.height = zones_svg.height * scale_factor
    zones_svg.scale(scale_factor, scale_factor)

    renderPDF.draw(zones_svg, c, 330, 200)

    # total amount of vehicles
    vehicle_data = data["total_amount_vehicles"]
    piechart(vehicle_data, 500, 500, "total_vehicles")
    vehicle_svg = svglib.svg2rlg(graph_path + "total_vehicles" + ".svg")

    scale_factor = 0.43
    vehicle_svg.width = vehicle_svg.width * scale_factor
    vehicle_svg.height = vehicle_svg.height * scale_factor
    vehicle_svg.scale(scale_factor, scale_factor)

    renderPDF.draw(vehicle_svg, c, 313, -42)

    # total amount of rentals
    rental_data = data["total_vehicles_rented"]

    c.setFont("Poppins-ExtraBold", 12)
    total_rentals_str = ', '.join(f'{v}' for k, v in rental_data.items())
    c.drawString(518, 108, total_rentals_str)

    c.showPage()
    c.save()
    
    return overlay_path

def create_pdf(data):
    # Maak een PDF met nieuwe inhoud
    overlay_pdf_path = create_overlay(data)

    # Lees de bestaande template en de overlay
    template_path = os.path.join(dir_path, 'utils', 'Infographic_Template.pdf')
    template = PdfReader(template_path)
    overlay = PdfReader(overlay_pdf_path)

    # Maak een nieuwe PdfWriter om de samengestelde PDF te maken
    writer = PdfWriter()

    # Voeg inhoud van de overlay toe aan de eerste pagina van de template
    first_page = template.pages[0]
    overlay_page = overlay.pages[0]

    # Voeg de overlay-inhoud toe aan de eerste pagina van de template
    first_page.merge_page(overlay_page)

    # Voeg de samengestelde pagina toe aan de PdfWriter
    writer.add_page(first_page)

    # Schrijf de nieuwe samengestelde PDF
    new_pdf_path = os.path.join(dir_path, 'utils', 'filled_infographic.pdf')
    writer.write(new_pdf_path)
    
    return new_pdf_path