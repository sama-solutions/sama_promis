from odoo import http
from odoo.http import request
import logging

_logger = logging.getLogger(__name__)

class TestSenegalController(http.Controller):
    """Contrôleur de test simple"""
    
    @http.route('/senegal2050/test', type='http', auth='public', website=True)
    def test_route(self, **kwargs):
        """Route de test simple"""
        _logger.info("Route de test appelée avec succès!")
        return "<h1>Test réussi ! Les contrôleurs Sénégal Gov fonctionnent.</h1>"
        
    @http.route('/senegal2050/dashboard-simple', type='http', auth='public', website=True)
    def dashboard_simple(self, **kwargs):
        """Tableau de bord simplifié pour tester"""
        try:
            _logger.info("Tentative d'accès au tableau de bord simple")
            
            # Test simple sans templates complexes
            projects_count = request.env['government.project'].sudo().search_count([])
            
            html_content = f"""
            <html>
                <head>
                    <title>Plan Sénégal 2050 - Tableau de Bord Test</title>
                    <style>
                        body {{ font-family: Arial, sans-serif; margin: 40px; }}
                        .card {{ border: 1px solid #ddd; padding: 20px; margin: 10px 0; }}
                        .green {{ background: #228B22; color: white; }}
                    </style>
                </head>
                <body>
                    <div class="card green">
                        <h1>🇸🇳 Plan Sénégal 2050</h1>
                        <h2>Tableau de Bord Public - Version Test</h2>
                    </div>
                    
                    <div class="card">
                        <h3>📊 Statistiques</h3>
                        <p><strong>Projets gouvernementaux:</strong> {projects_count}</p>
                        <p><strong>Status:</strong> ✅ Système opérationnel</p>
                        <p><strong>URL complète:</strong> <a href="/senegal2050/dashboard">Tableau de bord complet</a></p>
                    </div>
                    
                    <div class="card">
                        <h3>🔗 Liens de Test</h3>
                        <ul>
                            <li><a href="/senegal2050/test">Route de test simple</a></li>
                            <li><a href="/web">Interface Odoo</a></li>
                            <li><a href="/">Accueil</a></li>
                        </ul>
                    </div>
                    
                    <footer style="margin-top: 30px; text-align: center; color: #666;">
                        <p>© 2025 République du Sénégal - Module opérationnel</p>
                    </footer>
                </body>
            </html>
            """
            
            return html_content
            
        except Exception as e:
            _logger.error(f"Erreur dans dashboard_simple: {e}")
            return f"<h1>Erreur: {str(e)}</h1>"
