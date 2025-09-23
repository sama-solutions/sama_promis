# -*- coding: utf-8 -*-
"""
SAMA PROMIS - Helper Functions
==============================

Fonctions utilitaires partagées entre tous les micromodules.
"""

import qrcode
import io
import base64
from datetime import datetime, timedelta
import re
import hashlib
import uuid


def generate_qr_code(data, size=10, border=4):
    """
    Génère un QR code à partir de données.
    
    Args:
        data (str): Données à encoder
        size (int): Taille des modules
        border (int): Taille de la bordure
        
    Returns:
        str: QR code en base64
    """
    try:
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=size,
            border=border,
        )
        qr.add_data(data)
        qr.make(fit=True)
        
        img = qr.make_image(fill_color="black", back_color="white")
        buffer = io.BytesIO()
        img.save(buffer, format='PNG')
        
        return base64.b64encode(buffer.getvalue()).decode()
    except Exception:
        return False


def generate_reference(prefix='SP', length=8):
    """
    Génère une référence unique.
    
    Args:
        prefix (str): Préfixe de la référence
        length (int): Longueur de la partie numérique
        
    Returns:
        str: Référence unique
    """
    timestamp = datetime.now().strftime('%Y%m%d')
    random_part = str(uuid.uuid4().int)[:length]
    return f"{prefix}-{timestamp}-{random_part}"


def format_currency(amount, currency='XOF'):
    """
    Formate un montant avec la devise.
    
    Args:
        amount (float): Montant
        currency (str): Code devise
        
    Returns:
        str: Montant formaté
    """
    if not amount:
        return f"0 {currency}"
    
    # Formatage avec séparateurs de milliers
    formatted_amount = "{:,.0f}".format(amount).replace(',', ' ')
    return f"{formatted_amount} {currency}"


def calculate_percentage(part, total):
    """
    Calcule un pourcentage.
    
    Args:
        part (float): Partie
        total (float): Total
        
    Returns:
        float: Pourcentage
    """
    if not total or total == 0:
        return 0
    return round((part / total) * 100, 2)


def validate_email(email):
    """
    Valide un email.
    
    Args:
        email (str): Email à valider
        
    Returns:
        bool: True si valide
    """
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None


def validate_phone(phone):
    """
    Valide un numéro de téléphone sénégalais.
    
    Args:
        phone (str): Numéro à valider
        
    Returns:
        bool: True si valide
    """
    # Format sénégalais: +221 XX XXX XX XX ou 77/78/70/76/75 XXX XX XX
    patterns = [
        r'^\+221\s?[0-9]{2}\s?[0-9]{3}\s?[0-9]{2}\s?[0-9]{2}$',
        r'^(77|78|70|76|75)\s?[0-9]{3}\s?[0-9]{2}\s?[0-9]{2}$'
    ]
    
    for pattern in patterns:
        if re.match(pattern, phone.replace(' ', '')):
            return True
    return False


def sanitize_filename(filename):
    """
    Nettoie un nom de fichier.
    
    Args:
        filename (str): Nom de fichier
        
    Returns:
        str: Nom nettoyé
    """
    # Supprime les caractères dangereux
    filename = re.sub(r'[<>:"/\\|?*]', '', filename)
    # Remplace les espaces par des underscores
    filename = filename.replace(' ', '_')
    # Limite la longueur
    if len(filename) > 100:
        name, ext = filename.rsplit('.', 1) if '.' in filename else (filename, '')
        filename = name[:95] + ('.' + ext if ext else '')
    
    return filename


def generate_hash(data):
    """
    Génère un hash MD5 pour des données.
    
    Args:
        data (str): Données à hasher
        
    Returns:
        str: Hash MD5
    """
    return hashlib.md5(data.encode()).hexdigest()


def days_between(date1, date2):
    """
    Calcule le nombre de jours entre deux dates.
    
    Args:
        date1 (datetime): Première date
        date2 (datetime): Deuxième date
        
    Returns:
        int: Nombre de jours
    """
    if not date1 or not date2:
        return 0
    return abs((date2 - date1).days)


def is_deadline_approaching(deadline, warning_days=7):
    """
    Vérifie si une échéance approche.
    
    Args:
        deadline (datetime): Date d'échéance
        warning_days (int): Nombre de jours d'alerte
        
    Returns:
        bool: True si l'échéance approche
    """
    if not deadline:
        return False
    
    today = datetime.now().date()
    if isinstance(deadline, datetime):
        deadline = deadline.date()
    
    return (deadline - today).days <= warning_days


def get_status_color(state):
    """
    Retourne la couleur associée à un état.
    
    Args:
        state (str): État
        
    Returns:
        str: Couleur CSS
    """
    colors = {
        'draft': '#6b7280',         # Gris
        'submitted': '#3b82f6',     # Bleu
        'under_review': '#f59e0b',  # Orange
        'approved': '#10b981',      # Vert
        'in_progress': '#3b82f6',   # Bleu
        'suspended': '#f59e0b',     # Orange
        'completed': '#10b981',     # Vert
        'cancelled': '#ef4444',     # Rouge
        'published': '#10b981',     # Vert
        'closed': '#6b7280',        # Gris
        'active': '#10b981',        # Vert
        'expired': '#ef4444',       # Rouge
        'paid': '#10b981',          # Vert
        'rejected': '#ef4444'       # Rouge
    }
    return colors.get(state, '#6b7280')


def truncate_text(text, max_length=100):
    """
    Tronque un texte à une longueur maximale.
    
    Args:
        text (str): Texte à tronquer
        max_length (int): Longueur maximale
        
    Returns:
        str: Texte tronqué
    """
    if not text:
        return ''
    
    if len(text) <= max_length:
        return text
    
    return text[:max_length-3] + '...'


def format_file_size(size_bytes):
    """
    Formate une taille de fichier.
    
    Args:
        size_bytes (int): Taille en bytes
        
    Returns:
        str: Taille formatée
    """
    if size_bytes == 0:
        return "0 B"
    
    size_names = ["B", "KB", "MB", "GB", "TB"]
    i = 0
    while size_bytes >= 1024 and i < len(size_names) - 1:
        size_bytes /= 1024.0
        i += 1
    
    return f"{size_bytes:.1f} {size_names[i]}"