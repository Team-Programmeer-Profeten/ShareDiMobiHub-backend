from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.pagesizes import A4
from reportlab.graphics import renderPDF

import svglib.svglib as svglib

from graphs import barchart_horizontal, barchart_vertical

from PyPDF2 import PdfReader, PdfWriter

import os

from datetime import datetime

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
    # Hexcode: DCEEFB
    c.setFillColorRGB(0.8627, 0.9333, 0.9843)
    c.drawString(320, 783, f"{data['municipality']}")
    
    # Time period
    c.setFont("Poppins", 13)
    c.drawString(178, 748, f"{data['time_period']}")

    # Date
    c.drawString(395, 747.5, f"{data['date']}")

    # Topics
    c.setFont("Poppins-SemiBold", 8)
    # Hexcode: 0A1A29
    c.setFillColorRGB(0.0392, 0.1019, 0.1608)
    for i, topic in enumerate(data['topics']):
        c.drawString(60, 659 - (i * 13.6), f"{topic}")

    # Amount of hubs
    c.setFont("Poppins-ExtraBold", 36)
    # Hexcode: 0A1A29
    c.setFillColorRGB(0.0392, 0.1019, 0.1608)
    if data['amount_hubs'] <= 99:
        c.drawString(262, 602, f"{data['amount_hubs']}")
    else:
        c.setFont("Poppins-ExtraBold", 30)
        c.drawString(260, 603, f"{data['amount_hubs']}")

    # Service providers
    c.setFont("Poppins", 8)  # Set font size to 6
    columns = 7  # Number of items per column
    column_width = 100  # Width of each column
    start_x = 330  # Starting x-position
    start_y = 675  # Starting y-position
    line_height = 16  # Height of each line

    for i, provider in enumerate(data['service_providers']):
        column = i // columns
        row = i % columns
        x = start_x + column * column_width
        y = start_y - row * line_height
        c.drawString(x, y, f"- {provider}")
    
    # avg distance travelled in meters
    distance_data = data["avg_distance_travelled"]
    barchart_vertical(list(distance_data.keys()), list(distance_data.values()) , 200, 200, "avg_distance")
    distance_svg = svglib.svg2rlg(graph_path + "avg_distance" + ".svg")
    renderPDF.draw(distance_svg, c, 60, 450)
    
    c.setFont("Poppins", 10)
    avg_distance_str = ', '.join(f'{k}: {v}' for k, v in distance_data.items())
    c.drawString(60, 450, avg_distance_str)

    # avg parking time in minutes
    parking_data = data["avg_parking_time"]
    barchart_vertical(list(parking_data.keys()), list(parking_data.values()), 200, 200, "avg_parking_time")
    parking_svg = svglib.svg2rlg(graph_path + "avg_parking_time" + ".svg")
    renderPDF.draw(parking_svg, c, 60, 200)

    c.setFont("Poppins", 10)
    start_y = 200
    for i, (k, v) in enumerate(parking_data.items()):
        c.drawString(60, start_y - i*10, f'{k}: {v} minutes')

    # top 5 zones rented
    zones_data = data["top_5_zones_rented"]["top5"]
    barchart_horizontal(list(zones_data.keys()), list(zones_data.values()), 200, 200, "top_5_zones")
    zones_svg = svglib.svg2rlg(graph_path + "top_5_zones" + ".svg")
    renderPDF.draw(zones_svg, c, 350, 300)

    c.setFont("Poppins", 10)
    start_y = 300
    for i, (k, v) in enumerate(zones_data.items()):
        c.drawString(350, start_y - i*10, f'{k}: {v}')

    # total amount of vehicles
    vehicle_data = data["total_amount_vehicles"]
    barchart_horizontal(list(vehicle_data.keys()), list(vehicle_data.values()), 200, 200, "total_vehicles")
    vehicle_svg = svglib.svg2rlg(graph_path + "total_vehicles" + ".svg")
    renderPDF.draw(vehicle_svg, c, 340, 110)

    c.setFont("Poppins", 10)
    for i, (k, v) in enumerate(vehicle_data.items()):
        c.drawString(340, 110 - i*12, f'{k}: {v}')

    # total amount of rentals
    rental_data = data["total_vehicles_rented"]
    barchart_horizontal(list(rental_data.keys()), list(rental_data.values()), 200, 200, "total_rentals")
    rentals_svg = svglib.svg2rlg(graph_path + "total_rentals" + ".svg")
    renderPDF.draw(rentals_svg, c, 500, 70)

    c.setFont("Poppins", 10)
    total_rentals_str = ', '.join(f'{k}: {v}' for k, v in rental_data.items())
    c.drawString(500, 70, total_rentals_str)


    # Maak de pagina en sluit de canvas
    c.showPage()
    c.save()
    
    return overlay_path

# De gegevens die we willen toevoegen
# data = {
#     'municipality': 'Utrecht',
#     'time_period': 'Maart-April',
#     'date': datetime.now().strftime("%d-%m-%Y"),
#     'topics': ['Hoeveelheid voertuigen', 'Afstand afgelegd', 'Verhuringen', 'Zone bezetting', 'Hubs'],
#     'amount_hubs': '32',
#     'service_providers': [{ 'name': 'Cargoroo', 'type': 'Fiets' }, { 'name': 'Tier', 'type': 'Fiets'}, { 'name': 'Check', 'type': 'Scooter, Auto' }, { 'name': 'Donkey', 'type': 'Fiets' }, { 'name': 'Felyx', 'type': 'Scooter' }],
#     # Voeg meer data toe als dat nodig is
# }

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