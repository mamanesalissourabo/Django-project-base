from openpyxl import Workbook
from openpyxl.styles import Font
from django.http import HttpResponse
from django.utils.translation import gettext as _

def export_incidents_to_excel(queryset):
    response = HttpResponse(content_type='application/ms-excel')
    response['Content-Disposition'] = 'attachment; filename="incidents.xlsx"'
    
    wb = Workbook()
    ws = wb.active
    ws.title = "Incidents"
    
    # En-têtes communs
    headers = [
        "Référence", "Nom", "Date", "Description", 
        "Type d'incident", "Statut", "Site", "Emplacement"
    ]
    
    # En-têtes conditionnels pour PA et OSE
    pa_headers = [
        "Blessure potentielle", "Cause principale", 
        "Conséquence PA", "Solution PA"
    ]
    
    ose_headers = [
        "Conséquence OSE", "Solution OSE", 
        "Action correction", "Commentaire correction"
    ]
    
    # Ajouter tous les en-têtes
    headers.extend(pa_headers)
    headers.extend(ose_headers)
    
    ws.append(headers)
    
    # Style des en-têtes
    for cell in ws[1]:
        cell.font = Font(bold=True)
    
    # Données
    for incident in queryset:
        # Données de base
        row_data = [
            incident.reference,
            incident.name,
            incident.report_date.strftime("%d/%m/%Y %H:%M") if incident.report_date else "",
            incident.description,
            incident.get_type_incident_display(),
            incident.get_status_display(),
            str(incident.site) if incident.site else "",
            str(incident.emplacement) if incident.emplacement else "",
        ]
        
        # Données spécifiques PA
        if incident.type_incident == 'PA':
            row_data.extend([
                "Oui" if incident.blessure_potentielle else "Non",
                incident.cause_principale or "",
                incident.consequence_pa or "",
                incident.solution_pa or "",
            ])
        else:
            row_data.extend(["", "", "", ""])  # Colonnes vides pour PA
            
        # Données spécifiques OSE
        if incident.type_incident == 'OSE':
            row_data.extend([
                incident.consequence_ose or "",
                incident.solution_ose or "",
                "Oui" if incident.action_correction else "Non",
                incident.commentaire_correction or "",
            ])
        else:
            row_data.extend(["", "", "", ""])  # Colonnes vides pour OSE
        
        ws.append(row_data)
    
    wb.save(response)
    return response