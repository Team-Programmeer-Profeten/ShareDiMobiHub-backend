from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.pagesizes import A4
from reportlab.graphics import renderPDF

import svglib.svglib as svglib

from app.graphs import barchart_horizontal, barchart_vertical, piechart, multi_barchart, linechart, multi_linechart
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
    barchart_horizontal(list(hubs_data.keys()), list(hubs_data.values()), 450, 200, "top_5_hubs", "Aantal verhuringen")
    hubs_svg = svglib.svg2rlg(graph_path + "top_5_hubs" + ".svg")

    # Scale down the SVG
    scale_factor = 0.55
    hubs_svg.width = hubs_svg.width * scale_factor
    hubs_svg.height = hubs_svg.height * scale_factor
    hubs_svg.scale(scale_factor, scale_factor)

    renderPDF.draw(hubs_svg, c, 330, 410)

    # top 5 zones rented
    zones_data = data["top_5_zones_rented"]["top5"]
    barchart_horizontal(list(zones_data.keys()), list(zones_data.values()), 450, 200, "top_5_zones", "Aantal verhuringen")
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

def add_page(data, writer):
    if 'topics' in data:
        for topic in data['topics']:
            if topic == 'Hoeveelheid Voertuigen':
                amount_vehicles = os.path.join(dir_path, 'utils', 'topics', 'amount_vehicles_overlay.pdf')
                c = canvas.Canvas(amount_vehicles, pagesize=A4)
                c.setFont("Poppins", 28)
                c.setFillColorRGB(0.8627, 0.9333, 0.9843)
                c.drawString(130, 783, f"{topic}")

                c.setFont("Poppins-SemiBold", 16)
                c.setFillColorRGB(0.0392, 0.1019, 0.1608)
                c.drawString(100, 660, "Aantal voertuigen per tijdslot")

                # Amount vehicles
                vehicle_data = data["amount_vehicles"]
                linechart(vehicle_data["x"], vehicle_data["y"], 450, 250, "amount_vehicles", "Tijdslot", "Aantal voertuigen")
                vehicle_svg = svglib.svg2rlg(graph_path + "amount_vehicles" + ".svg")
                renderPDF.draw(vehicle_svg, c, 20, 395)

                c.setFont("Poppins-SemiBold", 16)
                c.setFillColorRGB(0.0392, 0.1019, 0.1608)
                c.drawString(90, 330, "Aantal voertuigen per service provider")

                # Amount vehicles per provider
                vehicle_data_provider = data["amount_vehicles_provider"]
                multi_linechart(vehicle_data_provider, 550, 250, "amount_vehicles_provider")
                vehicle_provider_svg = svglib.svg2rlg(graph_path + "amount_vehicles_provider" + ".svg")
                renderPDF.draw(vehicle_provider_svg, c, 20, 70)

                c.showPage()
                c.save()
    
                overlay = PdfReader(amount_vehicles)
                template = PdfReader(os.path.join(dir_path, 'utils', 'Topic_Template.pdf'))
                
                newWriter = PdfWriter()
                template_page = template.pages[0]
                overlay_page = overlay.pages[0]

                template_page.merge_page(overlay_page)

                newWriter.add_page(template_page)

                writer.add_page(template_page)

            if topic == 'Afstand Afgelegd':
                distance_travelled = os.path.join(dir_path, 'utils', 'topics', 'distance_travelled_overlay.pdf')
                c = canvas.Canvas(distance_travelled, pagesize=A4)
                c.setFont("Poppins", 28)
                c.setFillColorRGB(0.8627, 0.9333, 0.9843)
                c.drawString(170, 783, f"{topic}")

                c.setFont("Poppins-SemiBold", 16)
                c.setFillColorRGB(0.0392, 0.1019, 0.1608)
                c.drawString(80, 660, "Afstand afgelegd per half jaar")

                # Distance travelled per half year
                distance_travelled_halfyears = data["distance_travelled_halfyears"]
                barchart_vertical(list(distance_travelled_halfyears.keys()), list(distance_travelled_halfyears.values()), 350, 250, "distance_travelled_halfyears", "Tijdslot", "Afstand (km)")
                distance_travelled_svg = svglib.svg2rlg(graph_path + "distance_travelled_halfyears" + ".svg")
                renderPDF.draw(distance_travelled_svg, c, 20, 395)

                c.setFont("Poppins-SemiBold", 16)
                c.setFillColorRGB(0.0392, 0.1019, 0.1608)
                c.drawString(80, 330, "Gemiddelde afstand per service provider")
                
                # Average distance by provider
                average_distance_by_provider = data["average_distance_by_provider"]
                barchart_horizontal(list(average_distance_by_provider.keys()), list(average_distance_by_provider.values()), 450, 200, "average_distance_by_provider", "Afstand (m)")
                average_distance_by_provider_svg = svglib.svg2rlg(graph_path + "average_distance_by_provider" + ".svg")
                renderPDF.draw(average_distance_by_provider_svg, c, 18, 120)

                c.showPage()
                c.save()
    
                overlay = PdfReader(distance_travelled)
                template = PdfReader(os.path.join(dir_path, 'utils', 'Topic_Template.pdf'))
                
                newWriter = PdfWriter()
                template_page = template.pages[0]
                overlay_page = overlay.pages[0]

                template_page.merge_page(overlay_page)

                newWriter.add_page(template_page)

                writer.add_page(template_page)

            if topic == 'Verhuringen':
                rentals = os.path.join(dir_path, 'utils', 'topics', 'rentals_overlay.pdf')
                c = canvas.Canvas(rentals, pagesize=A4)
                c.setFont("Poppins", 28)
                c.setFillColorRGB(0.8627, 0.9333, 0.9843)
                c.drawString(200, 783, f"{topic}")

                c.setFont("Poppins-SemiBold", 16)
                c.setFillColorRGB(0.0392, 0.1019, 0.1608)
                c.drawString(100, 660, "Verhuringen per dag")

                # Rentals per day
                rented_neighbourhoods_data = data["rentals_neighbourhoods"]
                barchart_vertical(list(rented_neighbourhoods_data.keys()), list(rented_neighbourhoods_data.values()), 300, 250, "rentals_neighbourhoods", "Dag", "Aantal")
                rentals_svg = svglib.svg2rlg(graph_path + "rentals_neighbourhoods" + ".svg")
                renderPDF.draw(rentals_svg, c, 20, 395)

                c.setFont("Poppins-SemiBold", 16)
                c.setFillColorRGB(0.0392, 0.1019, 0.1608)
                c.drawString(50, 350, "Verhuringen per service provider per dag")

                # Rentals per day per provider
                rentals_per_provider = data["rentals_per_provider"]
                multi_barchart(rentals_per_provider, 550, 400, "rentals_per_provider", "Dag", "Aantal")
                rentals_per_provider_svg = svglib.svg2rlg(graph_path + "rentals_per_provider" + ".svg")

                # Scale down the SVG
                scale_factor = 0.70
                rentals_per_provider_svg.width = rentals_per_provider_svg.width * scale_factor
                rentals_per_provider_svg.height = rentals_per_provider_svg.height * scale_factor
                rentals_per_provider_svg.scale(scale_factor, scale_factor)

                renderPDF.draw(rentals_per_provider_svg, c, 20, 60)

                c.showPage()
                c.save()
    
                overlay = PdfReader(rentals)
                template = PdfReader(os.path.join(dir_path, 'utils', 'Topic_Template.pdf'))
                
                newWriter = PdfWriter()
                template_page = template.pages[0]
                overlay_page = overlay.pages[0]

                template_page.merge_page(overlay_page)

                newWriter.add_page(template_page)

                writer.add_page(template_page)

            if topic == 'Zone Bezetting':
                zone_occupation = os.path.join(dir_path, 'utils', 'topics', 'zone_occupation_overlay.pdf')
                c = canvas.Canvas(zone_occupation, pagesize=A4)
                c.setFont("Poppins", 28)
                c.setFillColorRGB(0.8627, 0.9333, 0.9843)
                c.drawString(190, 783, f"{topic}")

                c.setFont("Poppins-SemiBold", 16)
                c.setFillColorRGB(0.0392, 0.1019, 0.1608)
                c.drawString(80, 660, "Gemiddelde parkeertijd per service provider")

                # Average parking time by provider
                avg_parkingtime_per_provider = data["avg_parkingtime_per_provider"]
                barchart_horizontal(list(avg_parkingtime_per_provider.keys()), list(avg_parkingtime_per_provider.values()), 450, 200, "avg_parkingtime_per_provider", "Parkeertijd (h)")
                avg_parkingtime_per_provider_svg = svglib.svg2rlg(graph_path + "avg_parkingtime_per_provider" + ".svg")
                renderPDF.draw(avg_parkingtime_per_provider_svg, c, 20, 450)

                c.setFont("Poppins-SemiBold", 16)
                c.setFillColorRGB(0.0392, 0.1019, 0.1608)
                c.drawString(50, 365, "Gemiddelde parkeertijd in minuten per half jaar")

                # Average parking time half years
                avg_parkingtime_halfyears = data["avg_parking_time_half_years"]
                barchart_vertical(list(avg_parkingtime_halfyears.keys()), list(avg_parkingtime_halfyears.values()), 350, 250, "avg_parking_time_half_years", "Tijdslot", "Tijd (min)")
                avg_parkingtime_halfyears_svg = svglib.svg2rlg(graph_path + "avg_parking_time_half_years" + ".svg")
                renderPDF.draw(avg_parkingtime_halfyears_svg, c, 30, 100)

                c.showPage()
                c.save()
    
                overlay = PdfReader(zone_occupation)
                template = PdfReader(os.path.join(dir_path, 'utils', 'Topic_Template.pdf'))
                
                newWriter = PdfWriter()
                template_page = template.pages[0]
                overlay_page = overlay.pages[0]

                template_page.merge_page(overlay_page)

                newWriter.add_page(template_page)

                writer.add_page(template_page)

            if topic == 'Hubs':
                hubs = os.path.join(dir_path, 'utils', 'topics', 'hubs_overlay.pdf')
                c = canvas.Canvas(hubs, pagesize=A4)
                c.setFont("Poppins", 28)
                c.setFillColorRGB(0.8627, 0.9333, 0.9843)
                c.drawString(250, 783, f"{topic}")

                c.setFont("Poppins-SemiBold", 16)
                c.setFillColorRGB(0.0392, 0.1019, 0.1608)
                c.drawString(50, 660, "Gemiddelde bezetting alle hubs per voertuigtype")

                # Avg occupation hubs
                avg_occupation_hubs = data["avg_occupation_hubs"]
                barchart_vertical(list(avg_occupation_hubs.keys()), list(avg_occupation_hubs.values()), 450, 250, "avg_occupation_hubs", "Voertuigtypes", "Gemiddelde bezetting")
                avg_occupation_hubs_svg = svglib.svg2rlg(graph_path + "avg_occupation_hubs" + ".svg")
                renderPDF.draw(avg_occupation_hubs_svg, c, 20, 400)

                c.setFont("Poppins-SemiBold", 16)
                c.setFillColorRGB(0.0392, 0.1019, 0.1608)
                c.drawString(50, 330, "Bezetting totale capaciteit hubs per voertuigtype")

                # Available vehicle percentage of capacity of all hubs
                available_vehicle_percentage = data["vehicle_available_percentage_of_capacity"]
                barchart_vertical(list(available_vehicle_percentage.keys()), list(available_vehicle_percentage.values()), 450, 250, "vehicle_available_percentage_of_capacity", "Voertuigtypes", "Bezetting (%)")
                available_vehicle_percentage_svg = svglib.svg2rlg(graph_path + "vehicle_available_percentage_of_capacity" + ".svg")
                renderPDF.draw(available_vehicle_percentage_svg, c, 20, 75)

                c.showPage()
                c.save()
    
                overlay = PdfReader(hubs)
                template = PdfReader(os.path.join(dir_path, 'utils', 'Topic_Template.pdf'))
                
                newWriter = PdfWriter()
                template_page = template.pages[0]
                overlay_page = overlay.pages[0]

                template_page.merge_page(overlay_page)

                newWriter.add_page(template_page)

                writer.add_page(template_page)
    

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

    add_page(data, writer)

    # Schrijf de nieuwe samengestelde PDF
    new_pdf_path = os.path.join(dir_path, 'utils', 'filled_infographic.pdf')
    writer.write(new_pdf_path)
    
    return new_pdf_path
