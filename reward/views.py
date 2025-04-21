from django.shortcuts import render
from reward.models import UserProfile

def leaderboard(request):
    # Récupérer les 10 meilleurs utilisateurs triés par total_points (du plus élevé au plus bas)
    top_users = UserProfile.objects.order_by('-total_points')[:10]
    
    # Ajouter le rang (position) à chaque utilisateur
    ranked_users = []
    for rank, profile in enumerate(top_users, start=1):
        ranked_users.append({
            'rank': rank,
            'first_name': profile.user.first_name or "Utilisateur", 
            'last_name': profile.user.last_name or "",  
            'incident_count': profile.get_incident_count(),  # Nombre d'incidents
            'total_bonus': profile.get_total_bonus(),        # Total des bonus
            'total_points': profile.total_points,            # Total des points
        })
    # Passer les utilisateurs classés au template
    return render(request, 'reward/leaderboard.html', {'ranked_users': ranked_users})
